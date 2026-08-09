data "aws_caller_identity" "current" {}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_deploy" {
  name = "sentinel-github-deploy"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # ONLY your repo can assume this role
          "token.actions.githubusercontent.com:sub" = "repo:abhijayanoop/sentinel:*"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "github_deploy" {
  name = "sentinel-deploy-permissions"
  role = aws_iam_role.github_deploy.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload", "ecr:BatchGetImage",
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:DescribeServices", "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition", "ecs:UpdateService",
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = [aws_iam_role.ecs_execution_role.arn, aws_iam_role.ecs_task_role.arn]
      },
      {
        Effect   = "Allow"
        Action   = ["elasticloadbalancing:DescribeLoadBalancers"]
        Resource = "*"
      },
    ]
  })
}

output "github_deploy_role_arn" {
  value = aws_iam_role.github_deploy.arn
}