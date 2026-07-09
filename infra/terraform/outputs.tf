output "ecr_repository_url" {
  description = "The address to push your Docker image to"
  value       = aws_ecr_repository.sentinel_backend.repository_url
}

output "db_endpoint" {
  description = "The database's address"
  value       = aws_db_instance.sentinel_db.address
}

output "cluster_name" {
  description = "The ECS cluster name"
  value       = aws_ecs_cluster.sentinel.name
}

output "service_name" {
  description = "The ECS service name"
  value       = aws_ecs_service.backend.name
}
