# ==============================================================================
# JISR Arabic (فهيم) - Enterprise Cloud Infrastructure Root Blueprint
# Region: me-central-1 (UAE) | Target: 10,000+ Students | 1,000 CCU
# Compliance: UAE PDPL Federal Decree-Law No. 45/2021 & UAE MoE Framework
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Production S3 backend with DynamoDB state locking
  # Uncomment and configure with your organization's backend bucket
  # backend "s3" {
  #   bucket         = "jisr-terraform-state-me-central-1"
  #   key            = "production/terraform.tfstate"
  #   region         = "me-central-1"
  #   dynamodb_table = "jisr-terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region                      = var.aws_region
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  skip_region_validation      = true

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Compliance  = "UAE-PDPL"
    }
  }
}

# --- Module 1: Multi-AZ Network Topology ---
module "vpc" {
  source             = "./modules/vpc"
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# --- Module 2: Secrets Manager & Cryptographic Keys ---
module "secrets" {
  source       = "./modules/secrets"
  project_name = var.project_name
  environment  = var.environment
  db_username  = var.db_username
}

# --- Module 3: S3 Asset Storage & CloudFront CDN ---
module "storage" {
  source          = "./modules/storage"
  project_name    = var.project_name
  environment     = var.environment
  cdn_domain_name = var.cdn_subdomain
}

# --- Module 4: Aurora PostgreSQL 16 (Multi-AZ) & RDS Proxy ---
module "database" {
  source                    = "./modules/database"
  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  isolated_subnet_ids       = module.vpc.isolated_database_subnet_ids
  compute_security_group_id = module.vpc.compute_security_group_id
  db_name                   = var.db_name
  db_username               = var.db_username
  db_password               = module.secrets.db_password
  db_credentials_secret_arn = module.secrets.db_credentials_secret_arn
  db_instance_class         = var.db_instance_class
  backup_retention_days     = var.db_backup_retention_days
}

# --- Module 5: ElastiCache Redis 7 Cluster ---
module "redis" {
  source                    = "./modules/redis"
  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  isolated_subnet_ids       = module.vpc.isolated_database_subnet_ids
  compute_security_group_id = module.vpc.compute_security_group_id
  redis_node_type           = var.redis_node_type
}

# --- Module 6: ECS Fargate Cluster, ALB, & Auto-Scaling ---
module "ecs" {
  source                     = "./modules/ecs"
  project_name               = var.project_name
  environment                = var.environment
  aws_region                 = var.aws_region
  vpc_id                     = module.vpc.vpc_id
  public_subnet_ids          = module.vpc.public_subnet_ids
  private_compute_subnet_ids = module.vpc.private_compute_subnet_ids
  alb_security_group_id      = module.vpc.alb_security_group_id
  compute_security_group_id  = module.vpc.compute_security_group_id
  ecs_api_min_capacity       = var.ecs_api_min_capacity
  ecs_api_max_capacity       = var.ecs_api_max_capacity
  ecs_api_cpu                = var.ecs_api_cpu
  ecs_api_memory             = var.ecs_api_memory
  ecs_worker_min_capacity    = var.ecs_worker_min_capacity
  ecs_worker_max_capacity    = var.ecs_worker_max_capacity
  db_proxy_endpoint          = module.database.proxy_endpoint
  db_name                    = var.db_name
  db_username                = var.db_username
  db_password                = module.secrets.db_password
  redis_url                  = module.redis.redis_url
  s3_bucket_name             = module.storage.bucket_name
  s3_bucket_arn              = module.storage.bucket_arn
  cloudfront_domain_name     = module.storage.cloudfront_domain_name
  cors_origins               = var.cors_origins
  trusted_proxies            = var.trusted_proxies
  app_secrets_arn            = module.secrets.app_secrets_arn
}
