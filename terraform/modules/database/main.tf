# ==============================================================================
# JISR Arabic - Amazon Aurora PostgreSQL 16 (Multi-AZ) & Amazon RDS Proxy
# ==============================================================================

# --- Database Subnet Group ---
resource "aws_db_subnet_group" "main" {
  name        = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids  = var.isolated_subnet_ids
  description = "Isolated database subnets for Aurora PostgreSQL"

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
  }
}

# --- Database & Proxy Security Group ---
resource "aws_security_group" "db" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Controls inbound access to Aurora PostgreSQL and RDS Proxy"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL traffic strictly from ECS compute tasks
  ingress {
    description     = "PostgreSQL from ECS Compute Tasks"
    from_port       = 5432
    to_port         = 5432
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
    Name        = "${var.project_name}-${var.environment}-db-sg"
    Environment = var.environment
  }
}

# --- Aurora PostgreSQL Cluster ---
resource "aws_rds_cluster" "main" {
  cluster_identifier        = "${var.project_name}-${var.environment}-aurora"
  engine                    = "aurora-postgresql"
  engine_version            = "16.1"
  database_name             = var.db_name
  master_username           = var.db_username
  master_password           = var.db_password
  db_subnet_group_name      = aws_db_subnet_group.main.name
  vpc_security_group_ids    = [aws_security_group.db.id]
  storage_encrypted         = true
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-${var.environment}-aurora-final-snap"

  # Continuous Point-In-Time Recovery (PITR)
  backup_retention_period      = var.backup_retention_days
  preferred_backup_window      = "01:00-02:00" # UAE night window
  preferred_maintenance_window = "sun:02:30-sun:03:30"

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Name        = "${var.project_name}-${var.environment}-aurora"
    Environment = var.environment
  }
}

# --- Multi-AZ Cluster Instances (1 Writer + 1 Reader) ---
resource "aws_rds_cluster_instance" "instances" {
  count                = 2
  identifier           = "${var.project_name}-${var.environment}-aurora-${count.index + 1}"
  cluster_identifier   = aws_rds_cluster.main.id
  instance_class       = var.db_instance_class
  engine               = aws_rds_cluster.main.engine
  engine_version       = aws_rds_cluster.main.engine_version
  db_subnet_group_name = aws_db_subnet_group.main.name
  publicly_accessible  = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-aurora-${count.index + 1}"
    Environment = var.environment
    Role        = count.index == 0 ? "Writer" : "Reader"
  }
}

# --- IAM Role for RDS Proxy Secrets Access ---
resource "aws_iam_role" "proxy" {
  name = "${var.project_name}-${var.environment}-rds-proxy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "proxy_secrets" {
  name = "${var.project_name}-${var.environment}-proxy-secrets-policy"
  role = aws_iam_role.proxy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [var.db_credentials_secret_arn]
      }
    ]
  })
}

# --- Amazon RDS Proxy (Managed PgBouncer Connection Pooler) ---
resource "aws_db_proxy" "main" {
  name                   = "${var.project_name}-${var.environment}-proxy"
  debug_logging          = false
  engine_family          = "POSTGRESQL"
  idle_client_timeout    = 1800
  require_tls            = true
  role_arn               = aws_iam_role.proxy.arn
  vpc_security_group_ids = [aws_security_group.db.id]
  vpc_subnet_ids         = var.isolated_subnet_ids

  auth {
    auth_scheme = "SECRETS"
    iam_auth    = "DISABLED"
    secret_arn  = var.db_credentials_secret_arn
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-proxy"
    Environment = var.environment
  }
}

resource "aws_db_proxy_default_target_group" "main" {
  db_proxy_name = aws_db_proxy.main.name

  connection_pool_config {
    connection_borrow_timeout    = 30
    max_connections_percent      = 90
    max_idle_connections_percent = 50
  }
}

resource "aws_db_proxy_target" "main" {
  db_proxy_name         = aws_db_proxy.main.name
  target_group_name     = aws_db_proxy_default_target_group.main.name
  db_cluster_identifier = aws_rds_cluster.main.id
}
