data "aws_secretsmanager_secret" "webhook" {
    name = "sentinel/webhook-secret"
}

data "aws_secretsmanager_secret" "jwt" {
    name = "sentinel/jwt-secret"
}

data "aws_secretsmanager_secret" "db_password" {
  name = "sentinel/db-password"
}

data "aws_secretsmanager_secret" "openai" {
  name = "sentinel/openai-api-key"
}