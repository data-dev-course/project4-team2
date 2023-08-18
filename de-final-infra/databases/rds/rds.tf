module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.1.1"
  
  identifier = "de-3-2-rds"

  engine = "postgres"
  engine_version = "15"
  family = "postgres15" # DB parameter group
  major_engine_version = "15"         # DB option group
  instance_class = "db.t3.medium"

  db_name  = "PostgresRDS32"
  username = "admin32"
  password = aws_secretsmanager_secret_version.password.secret_string
  port     = "5432"

  allocated_storage     = 32

  multi_az               = true
  db_subnet_group_name   = data.terraform_remote_state.databases.outputs.db_subnet_group_name
  vpc_security_group_ids = [data.terraform_remote_state.databases.outputs.db_security_group_id]

  maintenance_window              = "sun:04:30-sun:05:30"
  backup_window                   = "04:00-04:30"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  create_cloudwatch_log_group     = true

  backup_retention_period = 1
  skip_final_snapshot     = true
  deletion_protection     = false

  create_db_option_group = false
  create_db_parameter_group = false
  parameter_group_name = "de-3-2-postgres15-pg"
}

resource "aws_secretsmanager_secret" "password" {
  name = "dev/de-3-2/rds"
}

resource "aws_secretsmanager_secret_version" "password" {
  secret_id = aws_secretsmanager_secret.password.id
  secret_string = var.rds_postgres_password
}