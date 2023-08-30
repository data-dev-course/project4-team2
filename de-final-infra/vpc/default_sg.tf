# Default Security Group 
# This is the security group for most of instances should have 
resource "aws_security_group" "default" {
  name        = "main-${var.vpc_name}"
  description = "default group for ${var.vpc_name}"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port = 8000       # You could set additional ingress port 
    to_port   = 8000
    protocol  = "tcp"
    cidr_blocks = [
      "10.0.0.0/8",
    ]
  }
    
  ingress {
    from_port = 80       # You could set additional ingress port 
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = [
      "10.0.0.0/8",
    ]
  }
    
  # Instance should allow jmx exportor to access for monitoring
  ingress {
    from_port   = 10080
    to_port     = 10080
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"] 
    description = "inbound rule for jmx exporter"
  }

  # Instance should allow node exporter to access for monitoring
  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "inbound rule for node exporter"
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "https any outbound"
  }

  egress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "http any outbound"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "https any outbound"
  }

  # Instance should allow ifselt to send the log file to kafka
  egress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "kafka any outbound"
  }


  # Instance should allow ifselt to send the log file to elasticsearch
  egress {
    from_port   = 9200
    to_port     = 9200
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "ElasticSearch any outbound"
  }

}