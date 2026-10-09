# ==============================================================================
# JISR Arabic - AWS Secrets Manager & Cryptographic Keys
# ==============================================================================

# Random secure password for PostgreSQL database
resource "random_password" "db_password" {
  length  = 32
  special = false # Avoid special characters that can cause connection URI parsing issues
}

# Random 64-character signing secret for application JWT authentication
resource "random_password" "fahim_secret_key" {
  length  = 64
  special = false
}

# --- Database Credentials Secret (used by RDS Proxy and App) ---
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}/${var.environment}/database"
  recovery_window_in_days = 0

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    engine   = "postgres"
    port     = 5432
  })
}

# --- Application Runtime Secrets ---
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.project_name}/${var.environment}/app-secrets"
  recovery_window_in_days = 0

  tags = {
    Name        = "${var.project_name}-${var.environment}-app-secrets"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    FAHIM_SECRET_KEY             = random_password.fahim_secret_key.result
    FAHIM_PAYMENT_WEBHOOK_SECRET = "whsec_placeholder_replace_with_live_stripe_secret"
    STRIPE_SECRET_KEY            = "sk_live_placeholder_replace_with_live_stripe_key"
    STRIPE_PUBLISHABLE_KEY       = "pk_live_placeholder_replace_with_live_stripe_key"
    GEMINI_API_KEY               = "AIzaSy_placeholder_replace_with_gemini_key"
    FAHIM_SMTP_HOST              = "email-smtp.me-central-1.amazonaws.com"
    FAHIM_SMTP_PORT              = "587"
    FAHIM_SMTP_USER              = "AKIA_SMTP_USER_PLACEHOLDER"
    FAHIM_SMTP_PASS              = "SMTP_PASS_PLACEHOLDER"
    FAHIM_SMTP_FROM              = "noreply@jisr.ae"
  })
}
