resource "aws_instance" "jenkins" {
  ami             = "ami-0c9c942bd7bf113a2" # Canonical, Ubuntu, 22.04 LTS, amd64 jammy image build on 2023-05-16
  instance_type   = "t3.small"
  key_name        = "de-3-2-jenkins"
  iam_instance_profile = ""
  subnet_id = data.terraform_remote_state.vpc.outputs.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]
  ebs_optimized = false

  tags = {
    Name  = "DE-3-2-ec2-jenkins"
    app   = "ec2-jenkins"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt update
              sudo apt install -y openjdk-11-jdk
              curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
                /usr/share/keyrings/jenkins-keyring.asc > /dev/null
              echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
                https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
                /etc/apt/sources.list.d/jenkins.list > /dev/null
              sudo apt update
              wget https://get.jenkins.io/war-stable/2.332.3/jenkins.war
              java -jar jenkins.war
              EOF

  ebs_block_device {
    device_name = "/dev/xvda"
    volume_type = "gp2"
    volume_size = "30"
  }
}

resource "aws_security_group" "jenkins_sg" {
  name        = "jenkins_sg"
  description = "Jenkins Security Group"
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # WARNING: This allows access from everywhere. Consider restricting it.
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# resource "aws_key_pair" "deployer" {
#   key_name   = "deployer-key"
#   public_key = file("~/.ssh/id_rsa.pub")  # Ensure you have the public key here
# }
