# Database Security Group
# This security Group needs to be made before creating database
resource "aws_security_group" "rds_postgres" {
  name        = "de-3-2-postgres-sg"
  description = "de 3-2 postgres SG"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id

  # Not using 3306 for mysql is recommended
  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"

    # You can add SG ID of instances which need to use this database.
    security_groups = []

    description = "Postresql Port"
  }

  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"

    security_groups = []

    description = "Postresql Port from vpc"
  }


  tags = {
    Name = "de-3-2-postgres-sg"
  }
}