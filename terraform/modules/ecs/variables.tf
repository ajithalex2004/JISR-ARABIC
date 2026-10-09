variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_compute_subnet_ids" {
  type = list(string)
}

variable "alb_security_group_id" {
  type = string
}

variable "compute_security_group_id" {
  type = string
}

variable "ecs_api_min_capacity" {
  type    = number
  default = 2
}

variable "ecs_api_max_capacity" {
  type    = number
  default = 6
}

variable "ecs_api_cpu" {
  type    = number
  default = 1024
}

variable "ecs_api_memory" {
  type    = number
  default = 2048
}

variable "ecs_worker_min_capacity" {
  type    = number
  default = 1
}

variable "ecs_worker_max_capacity" {
  type    = number
  default = 3
}

variable "db_proxy_endpoint" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "redis_url" {
  type = string
}

variable "s3_bucket_name" {
  type = string
}

variable "s3_bucket_arn" {
  type = string
}

variable "cloudfront_domain_name" {
  type = string
}

variable "cors_origins" {
  type = string
}

variable "trusted_proxies" {
  type = string
}

variable "app_secrets_arn" {
  type = string
}
