resource "aws_security_group" "ec2" {
  name        = "${var.vpc_name}-${var.service_name}"
  description = "${var.service_name}'s ssh and HTTP traffic allowance Security Group"
  vpc_id      = var.target_vpc

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = var.ext_lb_ingress_cidrs
    description = "SSH port"
  }

  ingress {
    from_port = 8080
    to_port   = 8080
    protocol  = "tcp"
    cidr_blocks = var.ext_lb_ingress_cidrs
    description = "HTTP Traffic"
  }

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = var.ext_lb_ingress_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
    description = "Internal outbound traffic"
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "https any outbound"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Internal outbound traffic"
  }
}

resource "aws_instance" "public_ec2" {
  ami                    = var.base_ami
  instance_type          = var.instance_type
  key_name               = var.key_name
  iam_instance_profile   = var.instance_profile
  subnet_id              = var.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.ec2.id]
  ebs_optimized          = var.ebs_optimized

  root_block_device {
    volume_size = "10"
  }

  tags = {
    Name  = "${var.stack}-${var.service_name}"
    app   = "${var.service_name}"
    stack = var.stack
  }

}