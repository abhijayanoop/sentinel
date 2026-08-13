resource "aws_sns_topic" "alarms" {
  name = "sentinel-alarms"
}

resource "aws_cloudwatch_metric_alarm" "backend_unhealthy" {
  alarm_name          = "sentinel-backend-unhealthy"
  comparison_operator = "LessThanThreshold"
  evaluation_periods = 2
  period = 60
  statistic = "Average"
  threshold = 1
  namespace = "AWS/ApplicationELB"
  metric_name = "HealthyHostCount"
  # a container that crashes within seconds of starting never accumulates the
  # 90s of sustained failed health checks needed for UnHealthyHostCount to
  # register it — but it does mean nothing is ever registered as healthy
  treat_missing_data = "breaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.backend.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
  ok_actions    = [aws_sns_topic.alarms.arn]
}

# --- Lambda: reshapes the SNS/CloudWatch payload and forwards it, HMAC-signed,
# to the backend's /webhooks/cloudwatch endpoint (see backend/app/api/webhooks.py) ---

data "archive_file" "cloudwatch_forwarder" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/cloudwatch_forwarder"
  output_path = "${path.module}/../lambda/cloudwatch_forwarder.zip"
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "cloudwatch_forwarder" {
  name               = "sentinel-cloudwatch-forwarder"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "cloudwatch_forwarder_logs" {
  role       = aws_iam_role.cloudwatch_forwarder.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "cloudwatch_forwarder_secret" {
  name = "sentinel-read-webhook-secret"
  role = aws_iam_role.cloudwatch_forwarder.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [data.aws_secretsmanager_secret.webhook.arn]
      }
    ]
  })
}

resource "aws_lambda_function" "cloudwatch_forwarder" {
  function_name    = "sentinel-cloudwatch-forwarder"
  role             = aws_iam_role.cloudwatch_forwarder.arn
  handler          = "index.handler"
  runtime          = "python3.12"
  timeout          = 15
  filename         = data.archive_file.cloudwatch_forwarder.output_path
  source_code_hash = data.archive_file.cloudwatch_forwarder.output_base64sha256

  environment {
    variables = {
      BACKEND_URL        = "http://${aws_lb.main.dns_name}/webhooks/cloudwatch"
      WEBHOOK_SECRET_ARN = data.aws_secretsmanager_secret.webhook.arn
    }
  }
}

resource "aws_lambda_permission" "sns_invoke" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cloudwatch_forwarder.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.alarms.arn
}

resource "aws_sns_topic_subscription" "cloudwatch_forwarder" {
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.cloudwatch_forwarder.arn
}
