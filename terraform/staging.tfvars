# ==============================================================================
# JISR Arabic (فهيم) - Staging Variable Overrides
# Target: Pre-Production Staging Verification
# Region: me-central-1 (AWS UAE)
# ==============================================================================

aws_region   = "me-central-1" # AWS UAE (Abu Dhabi / Dubai)
environment  = "staging"
project_name = "jisr-arabic"

# --- Domain & Networking ---
domain_name   = "staging.jisr.ae"
api_subdomain = "api.staging.jisr.ae"
cdn_subdomain = "cdn.staging.jisr.ae"
vpc_cidr      = "10.10.0.0/16"

# --- Compute Capacity (ECS Fargate) ---
ecs_api_min_capacity = 2
ecs_api_max_capacity = 4
ecs_api_cpu          = 512  # 0.5 vCPU per replica
ecs_api_memory       = 1024 # 1 GB RAM per replica

ecs_worker_min_capacity = 1
ecs_worker_max_capacity = 2

# --- Database & Connection Pooling ---
db_name                  = "jisr_staging"
db_username              = "jisr_staging_admin"
db_instance_class        = "db.t4g.medium" # Cost-effective staging tier
db_backup_retention_days = 7

# --- In-Memory Caching ---
redis_node_type = "cache.t4g.medium"

# --- Security & Proxies ---
cors_origins    = "https://staging.jisr.ae,https://app.staging.jisr.ae"
trusted_proxies = "127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

# --- Availability Zones (Multi-AZ UAE me-central-1) ---
availability_zones = ["me-central-1a", "me-central-1b", "me-central-1c"]
