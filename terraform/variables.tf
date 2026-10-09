# ==============================================================================
# JISR Arabic (فهيم) - Root Terraform Variables
# Target Capacity: 10,000+ Students | 1,000 Concurrent Users (CCU)
# AWS Region: me-central-1 (UAE - Abu Dhabi / Dubai) for UAE PDPL Data Residency
# ==============================================================================

variable "aws_region" {
  description = "Target AWS Region (UAE Data Residency required under UAE PDPL Federal Decree-Law No. 45/2021)"
  type        = string
  default     = "me-central-1"
}

variable "environment" {
  description = "Deployment environment name (e.g., production, staging)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project identifier for naming resources"
  type        = string
  default     = "jisr-arabic"
}

variable "domain_name" {
  description = "Apex domain name for the educational platform"
  type        = string
  default     = "jisr.ae"
}

variable "api_subdomain" {
  description = "Subdomain dedicated to the FastAPI backend API"
  type        = string
  default     = "api.jisr.ae"
}

variable "cdn_subdomain" {
  description = "Subdomain dedicated to the CloudFront CDN asset distribution"
  type        = string
  default     = "cdn.jisr.ae"
}

# --- Network Configuration ---
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

# --- Compute (ECS Fargate) Configuration ---
variable "ecs_api_min_capacity" {
  description = "Minimum number of stateless FastAPI container replicas (Multi-AZ HA)"
  type        = number
  default     = 2
}

variable "ecs_api_max_capacity" {
  description = "Maximum number of FastAPI replicas under peak school hour auto-scaling"
  type        = number
  default     = 6
}

variable "ecs_api_cpu" {
  description = "vCPU units allocated per FastAPI task (1024 = 1 vCPU, 2048 = 2 vCPU)"
  type        = number
  default     = 1024
}

variable "ecs_api_memory" {
  description = "Memory in MiB allocated per FastAPI task (2048 = 2 GB, 4096 = 4 GB)"
  type        = number
  default     = 2048
}

variable "ecs_worker_min_capacity" {
  description = "Minimum number of background worker daemon tasks"
  type        = number
  default     = 1
}

variable "ecs_worker_max_capacity" {
  description = "Maximum number of background worker tasks"
  type        = number
  default     = 3
}

# --- Database (Aurora PostgreSQL & RDS Proxy) Configuration ---
variable "db_name" {
  description = "Production PostgreSQL database name"
  type        = string
  default     = "jisr_prod"
}

variable "db_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "jisr_admin"
}

variable "db_instance_class" {
  description = "Instance class for Aurora PostgreSQL cluster instances"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "db_backup_retention_days" {
  description = "Point-in-Time Recovery (PITR) continuous backup retention in days"
  type        = number
  default     = 35
}

# --- In-Memory Cache (ElastiCache Redis) Configuration ---
variable "redis_node_type" {
  description = "ElastiCache Redis instance type"
  type        = string
  default     = "cache.m6g.large"
}

# --- CORS & Trusted Proxies ---
variable "cors_origins" {
  description = "Comma-separated allowlist of origins permitted for CORS"
  type        = string
  default     = "https://jisr.ae,https://app.jisr.ae,https://admin.jisr.ae"
}

variable "trusted_proxies" {
  description = "CIDR ranges permitted to supply forwarded IP headers"
  type        = string
  default     = "127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
}

variable "availability_zones" {
  description = "Explicit list of availability zones. Useful for offline dry-runs and staging simulations."
  type        = list(string)
  default     = []
}
