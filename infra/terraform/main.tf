terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "sentinel_backend" {
  name         = "sentinel-backend"
  force_delete = true
}

resource "aws_db_instance" "sentinel_db" {
  identifier             = "sentinel-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  db_name                = "sentinel"
  username               = "sentinel_admin"
  password               = var.db_password
  skip_final_snapshot    = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
}

resource "aws_cloudwatch_log_group" "sentinel" {
  name              = "/ecs/sentinel-backend"
  retention_in_days = 7
}