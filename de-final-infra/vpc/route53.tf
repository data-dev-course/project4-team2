resource "aws_route53_zone" "internal" {
  name    = "route53.internal"
  comment = "de-3-2-vpc - Managed by Terraform"

  vpc {
    vpc_id = aws_vpc.main.id
  }
}