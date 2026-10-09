variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "isolated_subnet_ids" {
  type = list(string)
}

variable "compute_security_group_id" {
  type = string
}

variable "db_name" {
  type    = string
  default = "jisr_prod"
}

variable "db_username" {
  type    = string
  default = "jisr_admin"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_credentials_secret_arn" {
  type = string
}

variable "db_instance_class" {
  type    = string
  default = "db.r6g.xlarge"
}

variable "backup_retention_days" {
  type    = number
  default = 35
}
