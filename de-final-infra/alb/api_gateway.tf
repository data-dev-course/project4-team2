resource "aws_apigatewayv2_vpc_link" "alb_vpc_link" {
  name               = "de-3-2-vpc-link"
  security_group_ids = [data.terraform_remote_state.vpc.outputs.aws_security_group_default_id]
  subnet_ids         = [
    data.terraform_remote_state.vpc.outputs.public_subnets[1],
    data.terraform_remote_state.vpc.outputs.public_subnets[2],
  ]
}

resource "aws_apigatewayv2_api" "alb_backend" {
  name          = "de-3-2-backend-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_route" "alb_backend" {
  api_id    = aws_apigatewayv2_api.alb_backend.id
  route_key = "ANY /example"
  target    = "integrations/${aws_apigatewayv2_integration.alb_backend.id}"
}

resource "aws_apigatewayv2_integration" "alb_backend" {
  api_id                   = aws_apigatewayv2_api.alb_backend.id
  integration_type         = "HTTP_PROXY"
  integration_method       = "ANY"
  integration_uri          = "http://${your_alb_dns_name}" # Replace with your ALB DNS name
  connection_type          = "VPC_LINK"
  connection_id            = aws_apigatewayv2_vpc_link.alb_backend.id
  description              = "Integration for de 3-2 backend route"
}

resource "aws_apigatewayv2_deployment" "alb_backend" {
  api_id      = aws_apigatewayv2_api.alb_backend.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_apigatewayv2_stage" "alb_backend" {
  api_id     = aws_apigatewayv2_api.alb_backend.id
  name       = "prod"
  deployment_id = aws_apigatewayv2_deployment.alb_backend.id
}

resource "aws_apigatewayv2_domain_name" "alb_backend" {
  domain_name      = "api.korrect.com"  # Replace with your domain
  domain_name_configuration {
    certificate_arn = aws_acm_certificate.alb_backend.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "alb_backend" {
  api_id      = aws_apigatewayv2_api.alb_backend.id
  domain_name = aws_apigatewayv2_domain_name.alb_backend.domain_name
  stage       = aws_apigatewayv2_stage.alb_backend.name
}