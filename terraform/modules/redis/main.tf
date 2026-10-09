# ==============================================================================
# JISR Arabic - Amazon ElastiCache for Redis 7 (Multi-AZ Cluster)
# ==============================================================================

# --- Redis Subnet Group ---
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.isolated_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-subnet-group"
    Environment = var.environment
  }
}

# --- Redis Security Group ---
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Controls inbound access to ElastiCache Redis cluster"
  vpc_id      = var.vpc_id

  # Inbound port 6379 strictly from ECS compute tasks
  ingress {
    description     = "Redis port 6379 from ECS compute"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.compute_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-sg"
    Environment = var.environment
  }
}

# --- Redis Parameter Group ---
resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-redis7-params"
  family = "redis7"

  # Volatile-LRU: Evict keys with an expire set when memory limit reached
  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis7-params"
    Environment = var.environment
  }
}

# --- Redis Replication Group (Primary + Replica in separate AZs) ---
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "JISR Arabic Redis Cache & Distributed Task Queue"
  node_type                  = var.redis_node_type
  num_cache_clusters         = 2
  parameter_group_name       = aws_elasticache_parameter_group.main.name
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  automatic_failover_enabled = true
  multi_az_enabled           = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = false # Allows high-speed unencrypted local VPC socket transport

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis"
    Environment = var.environment
  }
}
