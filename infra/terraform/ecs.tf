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
      name         = "backend"
      image        = var.app_image
      essential    = true
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment = [
        { name = "ENVIRONMENT", value = "production" },
        { name = "DATABASE_URL", value = "postgresql+psycopg://sentinel_admin:${var.db_password}@${aws_db_instance.sentinel_db.address}:5432/sentinel" },
        { name = "WEBHOOK_SECRET", value = var.webhook_secret },
        { name = "JWT_SECRET", value = var.jwt_secret },
      ]
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