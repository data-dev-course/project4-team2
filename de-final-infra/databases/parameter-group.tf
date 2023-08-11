# PostgreSQL DB Group
# This is for the database instance not the cluster.
resource "aws_db_parameter_group" "rds_postgres_pg" {
  name   = "de-3-2-postgres15-pg"
  family = "postgres15" # DB parameter group

  parameter {
    name = "application_name"
    value = "de-3-2-postgres-instance"
  }
  parameter  {
      name  = "autovacuum"
      value = 1
    }
  parameter {
      name  = "client_encoding"
      value = "utf8"
    }

  parameter {
    # Set Timezone to Seoul
    name  = "timezone"
    value = "UTC"
  }
  parameter {
    # Increase the maximum number of connections to 16000 which is the maximum of aurora DB connection
    name  = "max_connections"
    value = 16000
  }
}