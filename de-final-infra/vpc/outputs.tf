# Region
output "aws_region" {
  description = "Region of VPC"
  value = var.aws_region
}

output "region_namespace" {
  description = "Region name without '-'"
  value = replace(var.aws_region, "-", "")
}

# Availability_zones
output "availability_zones" {
  description = "Availability zone list of VPC"
  value = var.availability_zones
}

# VPC
output "vpc_name" {
  description = "The name of the VPC which is also the environment name"
  value       = var.vpc_name
}

output "vpc_id" {
  description = "VPC ID of newly created VPC"
  value = aws_vpc.main.id
}

output "cidr_block" {
  description = "CIDR block of VPC"
  value = aws_vpc.main.cidr_block
}

output "cidr_numeral" {
  description = "number that specifies the vpc range (B class)"
  value = var.cidr_numeral
}

# Shard
output "shard_id" {
  description = "The shard ID which will be used to distinguish the env of resources"
  value       = var.shard_id
}

output "shard_short_id" {
  description = "Short version of shard ID"
  value       = var.shard_short_id
}

# Prviate subnets
output "private_subnets" {
  description = "List of private subnet ID in VPC"
  value = aws_subnet.private.*.id
}

# Public subnets
output "public_subnets" {
  description = "List of public subnet ID in VPC"
  value = aws_subnet.public.*.id
}

# Private Database Subnets
output "db_private_subnets" {
  description = "List of DB private subnet ID in VPC"
  value = aws_subnet.private_db.*.id
}

# Private MWAA Subnets
output "mwaa_private_subnets" {
  description = "List of mwaa private subnet ID in VPC"
  value = aws_subnet.private_mwaa.*.id
}

# Private ECS Subnets
output "ecs_private_subnets" {
  description = "List of ecs private subnet ID in VPC"
  value = aws_subnet.private_ecs.*.id
}


# Route53
output "route53_internal_zone_id" {
  description = "Internal Zone ID for VPC"
  value = aws_route53_zone.internal.zone_id
}

output "route53_internal_domain" {
  description = "Internal Domain Name for VPC"
  value = aws_route53_zone.internal.name
}

output "aws_security_group_default_id" {
  description = "ID of default security group"
  value = aws_security_group.default.id
}

# ETC
output "env_suffix" {
  description = "Suffix of the environment"
  value       = var.env_suffix
}

output "billing_tag" {
  description = "The environment value for biliing consolidation."
  value       = var.billing_tag
}