variable "aws_region" {
  description = "Which AWS region (data center location) to deploy into"
  default     = "ap-south-1"
}

variable "db_password" {
  description = "The master password for the Postgres database"
  type        = string
  sensitive   = true
}

variable "app_image" {
  description = "The full address of your app's image in ECR (you set this after pushing)"
  type        = string
  default     = ""
}

variable "webhook_secret" {
  description = "The HMAC secret your app uses to verify webhooks"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "The secret your app uses to sign login tokens"
  type        = string
  sensitive   = true
}