output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "alb_zone_id" {
  value = aws_lb.main.zone_id
}

output "alb_arn" {
  value = aws_lb.main.arn
}

output "compute_security_group_id" {
  value = var.compute_security_group_id
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecr_api_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecr_worker_url" {
  value = aws_ecr_repository.worker.repository_url
}
