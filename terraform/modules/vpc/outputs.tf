output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_compute_subnet_ids" {
  value = aws_subnet.private_compute[*].id
}

output "isolated_database_subnet_ids" {
  value = aws_subnet.isolated_database[*].id
}

output "alb_security_group_id" {
  value = aws_security_group.alb.id
}

output "compute_security_group_id" {
  value = aws_security_group.compute.id
}
