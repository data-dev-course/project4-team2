output "db_subnet_group_ids" {
  description = "subnet group ids"
  value       = aws_db_subnet_group.rds.subnet_ids
}

output "db_subnet_group_name" {
  description = "subnet group name"
  value       = aws_db_subnet_group.rds.name
}

output "db_parameter_group_name" {
  description = "postgres parameter group name"
  value       = aws_db_parameter_group.rds_postgres_pg.name
}

output "db_security_group_name" {
    description = "db security group name"
    value = aws_security_group.rds_postgres.name
}

output "db_security_group_id" {
    description = "db security group id"
    value = aws_security_group.rds_postgres.id
}