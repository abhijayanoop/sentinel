resource "aws_ecs_cluster" "sentinel" {
  name = "sentinel-cluster"
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "sentinel-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = var.app_image
      essential = true
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ENVIRONMENT", value = "production" },
        { name = "OPENAI_MODEL", value = "gpt-4o" },
        { name = "OPENAI_EMBEDDING_MODEL", value = "text-embedding-3-small" },
        { name = "AWS_REGION", value = var.aws_region },
      ]

      secrets = [
        { name = "WEBHOOK_SECRET", valueFrom = data.aws_secretsmanager_secret.webhook.arn },
        { name = "JWT_SECRET", valueFrom = data.aws_secretsmanager_secret.jwt.arn },
        { name = "DB_PASSWORD", valueFrom = data.aws_secretsmanager_secret.db_password.arn },
        { name = "OPENAI_API_KEY", valueFrom = data.aws_secretsmanager_secret.openai.arn },
      ]

      environment = concat(
        [
          { name = "ENVIRONMENT", value = "production" },
          { name = "OPENAI_MODEL", value = "gpt-4o" },
          { name = "OPENAI_EMBEDDING_MODEL", value = "text-embedding-3-small" },
          { name = "AWS_REGION", value = var.aws_region },
          { name = "DATABASE_HOST", value = aws_db_instance.sentinel_db.address },
          { name = "DATABASE_PORT", value = "5432" },
          { name = "DATABASE_NAME", value = "sentinel" },
          { name = "DATABASE_USER", value = "sentinel_admin" },
        ]
      )

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.sentinel.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "backend" {
  name            = "sentinel-backend-service"
  cluster         = aws_ecs_cluster.sentinel.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = true
  }
}