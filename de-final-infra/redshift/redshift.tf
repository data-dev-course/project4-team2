data "aws_secretsmanager_secret" "redshift" {
 name = "dev/de-3-2/redshift"
}

data "aws_secretsmanager_secret_version" "secret_credentials" {
 secret_id = data.aws_secretsmanager_secret.redshift.id
}

resource "aws_redshiftserverless_namespace" "redshift_ns" {
  namespace_name = "de-3-2"
  admin_username = jsondecode(data.aws_secretsmanager_secret_version.secret_credentials.secret_string)["de-3-2_redshift_username"]
  admin_user_password = jsondecode(data.aws_secretsmanager_secret_version.secret_credentials.secret_string)["de-3-2_redshift_password"]

}

resource "aws_redshiftserverless_workgroup" "redshift_wg" {
  namespace_name = aws_redshiftserverless_namespace.redshift_ns.namespace_name
  workgroup_name = "de-3-2-redshift"
  base_capacity = 128

  security_group_ids = [aws_security_group.redshift-sg.id]
  subnet_ids = data.terraform_remote_state.vpc.outputs.private_subnets
}
