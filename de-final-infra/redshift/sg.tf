resource "aws_security_group" "redshift-sg" {
  name        = "redshift-sg-${data.terraform_remote_state.vpc.outputs.vpc_name}"
  description = "redshift security group for ${data.terraform_remote_state.vpc.outputs.vpc_name}"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
}