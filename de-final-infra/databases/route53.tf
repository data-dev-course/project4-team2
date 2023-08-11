# Route53 Record for Primary DB endpoint
resource "aws_route53_record" "postgres_db" {
  zone_id         = data.terraform_remote_state.vpc.outputs.route53_internal_zone_id
  name            = "de-3-2-postgres.${data.terraform_remote_state.vpc.outputs.route53_internal_domain}"
  type            = "CNAME"
  ttl             = 60
  records         = [var.rds_postgres_endpoint]
}