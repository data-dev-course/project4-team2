# Route53 Record for Primary DB endpoint
resource "aws_route53_record" "postgres_db" {
  zone_id         = data.terraform_remote_state.vpc.outputs.route53_internal_zone_id
  name            = "de-3-2-rds.${data.terraform_remote_state.vpc.outputs.route53_internal_domain}"
  type            = "CNAME"
  ttl             = 60
  records         = ["de-3-2-rds.ch4xfyi6stod.ap-northeast-2.rds.amazonaws.com:5432"]
}