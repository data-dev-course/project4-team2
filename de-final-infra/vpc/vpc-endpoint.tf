# Gateway Type Endpoint ( S3, DynamoDB )
## S3 Endpoint
resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"
  
  tags = {
   Name = "s3-${var.shard_id}"
  }
}

# Interface Type Endpoint 
# Security Group of VPC Endpoint (API Gateway)
resource "aws_security_group" "apigateway_vpc_endpoint_sg" {
  name = "apigateway_vpc_endpoint-${var.vpc_name}"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 443
    to_port = 443
    protocol = "TCP"

    cidr_blocks = [
      "10.0.0.0/8"
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
    description = "Internal outbound any traffic"
  }

  tags = {
    Name = "apigateway-${var.vpc_name}"
  }
}

## API Gateway Endpoint
resource "aws_vpc_endpoint" "apigateway_endpoint" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.execute-api"
  vpc_endpoint_type = "Interface"

  security_group_ids = [
    aws_security_group.apigateway_vpc_endpoint_sg.id
  ]

  private_dns_enabled = true
  auto_accept         = true

  tags = {
   Name = "apigateway-${var.shard_id}"
  }
}

resource "aws_vpc_endpoint_subnet_association" "apigateway_endpoint" {
  count           = length(var.availability_zones)
  vpc_endpoint_id = aws_vpc_endpoint.apigateway_endpoint.id
  subnet_id       = element(aws_subnet.private.*.id, count.index)
}