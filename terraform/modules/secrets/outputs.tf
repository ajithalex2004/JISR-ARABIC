output "db_password" {
  value     = random_password.db_password.result
  sensitive = true
}

output "db_credentials_secret_arn" {
  value = aws_secretsmanager_secret.db_credentials.arn
}

output "app_secrets_arn" {
  value = aws_secretsmanager_secret.app_secrets.arn
}
