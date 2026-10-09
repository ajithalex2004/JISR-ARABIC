# ==============================================================================
# JISR Arabic - Root Terraform Outputs
# ==============================================================================

output "alb_dns_name" {
  description = "Application Load Balancer DNS hostname for public DNS CNAME mapping (api.jisr.ae)"
  value       = module.ecs.alb_dns_name
}

output "cloudfront_domain_name" {
  description = "CloudFront CDN distribution domain name for asset CNAME mapping (cdn.jisr.ae)"
  value       = module.storage.cloudfront_domain_name
}

output "s3_bucket_name" {
  description = "Production S3 bucket name for audio, PDFs, and learning assets"
  value       = module.storage.bucket_name
}

output "rds_cluster_endpoint" {
  description = "Aurora PostgreSQL cluster primary writer endpoint"
  value       = module.database.cluster_endpoint
}

output "rds_proxy_endpoint" {
  description = "Amazon RDS Proxy endpoint (PgBouncer connection pooler) for FastAPI replicas"
  value       = module.database.proxy_endpoint
}

output "redis_url" {
  description = "ElastiCache Redis cluster connection URI"
  value       = module.redis.redis_url
}

output "ecr_api_url" {
  description = "Amazon ECR repository URL for the FastAPI backend image"
  value       = module.ecs.ecr_api_url
}

output "ecr_worker_url" {
  description = "Amazon ECR repository URL for the background worker image"
  value       = module.ecs.ecr_worker_url
}

output "app_secrets_arn" {
  description = "AWS Secrets Manager ARN containing production application secrets"
  value       = module.secrets.app_secrets_arn
}
