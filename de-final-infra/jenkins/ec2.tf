module "ec2" {
  source = "../module/ec2"

  service_name  = "ec2-jenkins"
  base_ami      = "ami-01056eaaa603955a4" # Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type
  instance_type = "t3.small"
  #  instance_profile          = data.terraform_remote_state.iam.outputs.elasticstack_instance_profile_name
  instance_profile = ""
  vpc_name         = data.terraform_remote_state.vpc.outputs.vpc_name
  public_subnets   = data.terraform_remote_state.vpc.outputs.public_subnets
  private_subnets  = data.terraform_remote_state.vpc.outputs.private_subnets
  target_vpc       = data.terraform_remote_state.vpc.outputs.vpc_id
  shard_id         = data.terraform_remote_state.vpc.outputs.shard_id

  route53_internal_domain  = data.terraform_remote_state.vpc.outputs.route53_internal_domain
  route53_internal_zone_id = data.terraform_remote_state.vpc.outputs.route53_internal_zone_id
  internal_domain_name     = "art.internal"

  stack         = "de-3-2"
  ebs_optimized = false

  key_name = "DE-3-2-DK"
  #  acm_external_ssl_certificate_arn = var.r53_variables.prod.star_weverse_io_acm_arn_apnortheast2

  #  route53_external_zone_id         = var.r53_variables.prod.weverse_io_zone_id

  ext_lb_ingress_cidrs = [
    "0.0.0.0/0",
    "10.0.0.0/8"
  ]

  lb_variables = var.lb_variables
  sg_variables = var.sg_variables
}