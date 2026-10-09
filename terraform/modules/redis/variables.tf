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

variable "redis_node_type" {
  type    = string
  default = "cache.m6g.large"
}
