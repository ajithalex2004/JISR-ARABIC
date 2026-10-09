# ==============================================================================
# JISR Arabic - Amazon ECS Fargate Cluster, ALB, & Auto-Scaling
# ==============================================================================

# --- ECR Repositories ---
resource "aws_ecr_repository" "api" {
  name                 = "${var.project_name}/api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-ecr-api"
    Environment = var.environment
  }
}

resource "aws_ecr_repository" "worker" {
  name                 = "${var.project_name}/worker"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-ecr-worker"
    Environment = var.environment
  }
}

# --- ECS Cluster with Container Insights ---
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cluster"
    Environment = var.environment
  }
}

# --- CloudWatch Log Groups ---
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}-${var.environment}-api"
  retention_in_days = 30

  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}-${var.environment}-worker"
  retention_in_days = 30

  tags = {
    Environment = var.environment
  }
}

# --- Application Load Balancer (Multi-AZ Public Subnets) ---
resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb"
    Environment = var.environment
  }
}

# --- Target Group with Liveness Health Probe ---
resource "aws_lb_target_group" "api" {
  name        = "${var.project_name}-${var.environment}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/api/health"
    port                = "8000"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-tg"
    Environment = var.environment
  }
}

# --- ALB Listener ---
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

# --- IAM Roles for ECS Tasks ---

# 1. Task Execution Role (Pull from ECR, CloudWatch Logs, Read Secrets)
resource "aws_iam_role" "execution" {
  name = "${var.project_name}-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "execution_standard" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "execution_secrets" {
  name = "${var.project_name}-${var.environment}-execution-secrets-policy"
  role = aws_iam_role.execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [var.app_secrets_arn]
      }
    ]
  })
}

# 2. Task Role (Runtime permissions for Python app: S3 read/write)
resource "aws_iam_role" "task" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "task_s3" {
  name = "${var.project_name}-${var.environment}-task-s3-policy"
  role = aws_iam_role.task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

# --- ECS Task Definitions ---

# 1. API Container Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-${var.environment}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.ecs_api_cpu)
  memory                   = tostring(var.ecs_api_memory)
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true
      command   = ["api"]
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "FAHIM_ENV", value = var.environment },
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${var.db_proxy_endpoint}:5432/${var.db_name}" },
        { name = "REDIS_URL", value = var.redis_url },
        { name = "STORAGE_BACKEND", value = "s3" },
        { name = "S3_BUCKET_NAME", value = var.s3_bucket_name },
        { name = "S3_REGION_NAME", value = var.aws_region },
        { name = "S3_CDN_DOMAIN", value = var.cloudfront_domain_name },
        { name = "FAHIM_CORS_ORIGINS", value = var.cors_origins },
        { name = "FAHIM_TRUSTED_PROXIES", value = var.trusted_proxies },
        { name = "DB_POOL_SIZE", value = "15" },
        { name = "DB_MAX_OVERFLOW", value = "10" },
        { name = "FASTAPI_THREAD_LIMIT", value = "200" },
        { name = "WEB_CONCURRENCY", value = "2" },
        { name = "FAHIM_DISABLE_IN_PROCESS_WORKER", value = "1" }
      ]
      secrets = [
        { name = "FAHIM_SECRET_KEY", valueFrom = "${var.app_secrets_arn}:FAHIM_SECRET_KEY::" },
        { name = "FAHIM_PAYMENT_WEBHOOK_SECRET", valueFrom = "${var.app_secrets_arn}:FAHIM_PAYMENT_WEBHOOK_SECRET::" },
        { name = "STRIPE_SECRET_KEY", valueFrom = "${var.app_secrets_arn}:STRIPE_SECRET_KEY::" },
        { name = "STRIPE_PUBLISHABLE_KEY", valueFrom = "${var.app_secrets_arn}:STRIPE_PUBLISHABLE_KEY::" },
        { name = "GEMINI_API_KEY", valueFrom = "${var.app_secrets_arn}:GEMINI_API_KEY::" },
        { name = "FAHIM_SMTP_HOST", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_HOST::" },
        { name = "FAHIM_SMTP_PORT", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_PORT::" },
        { name = "FAHIM_SMTP_USER", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_USER::" },
        { name = "FAHIM_SMTP_PASS", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_PASS::" },
        { name = "FAHIM_SMTP_FROM", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_FROM::" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-api-task"
    Environment = var.environment
  }
}

# 2. Worker Container Task Definition
resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-${var.environment}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = "${aws_ecr_repository.worker.repository_url}:latest"
      essential = true
      command   = ["worker"]
      environment = [
        { name = "FAHIM_ENV", value = var.environment },
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${var.db_proxy_endpoint}:5432/${var.db_name}" },
        { name = "REDIS_URL", value = var.redis_url },
        { name = "STORAGE_BACKEND", value = "s3" },
        { name = "S3_BUCKET_NAME", value = var.s3_bucket_name },
        { name = "S3_REGION_NAME", value = var.aws_region },
        { name = "S3_CDN_DOMAIN", value = var.cloudfront_domain_name },
        { name = "DB_POOL_SIZE", value = "5" },
        { name = "DB_MAX_OVERFLOW", value = "5" }
      ]
      secrets = [
        { name = "FAHIM_SECRET_KEY", valueFrom = "${var.app_secrets_arn}:FAHIM_SECRET_KEY::" },
        { name = "GEMINI_API_KEY", valueFrom = "${var.app_secrets_arn}:GEMINI_API_KEY::" },
        { name = "FAHIM_SMTP_HOST", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_HOST::" },
        { name = "FAHIM_SMTP_PORT", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_PORT::" },
        { name = "FAHIM_SMTP_USER", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_USER::" },
        { name = "FAHIM_SMTP_PASS", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_PASS::" },
        { name = "FAHIM_SMTP_FROM", valueFrom = "${var.app_secrets_arn}:FAHIM_SMTP_FROM::" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-worker-task"
    Environment = var.environment
  }
}

# --- ECS Services ---

# 1. API Service (Multi-AZ Fargate)
resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-${var.environment}-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.ecs_api_min_capacity
  launch_type     = "FARGATE"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  network_configuration {
    subnets          = var.private_compute_subnet_ids
    security_groups  = [var.compute_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name        = "${var.project_name}-${var.environment}-api-service"
    Environment = var.environment
  }
}

# 2. Worker Service (Standalone Daemon)
resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-${var.environment}-worker-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.ecs_worker_min_capacity
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_compute_subnet_ids
    security_groups  = [var.compute_security_group_id]
    assign_public_ip = false
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-worker-service"
    Environment = var.environment
  }
}

# --- Auto-Scaling Policies for API Replicas ---

resource "aws_appautoscaling_target" "api" {
  max_capacity       = var.ecs_api_max_capacity
  min_capacity       = var.ecs_api_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto-Scale on CPU Utilization > 70%
resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "${var.project_name}-${var.environment}-api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto-Scale on ALB Request Count per Target > 300 requests/minute
resource "aws_appautoscaling_policy" "api_requests" {
  name               = "${var.project_name}-${var.environment}-api-requests-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.api.arn_suffix}"
    }
    target_value       = 300.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
