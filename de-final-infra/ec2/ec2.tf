resource "aws_instance" "DE-3-2_bastion" {
    # ami는 terraform.tfvars에 작성
    ami           = var.ami
    instance_type = "t3.micro"
    key_name      = var.key_name
    subnet_id     = data.terraform_remote_state.vpc.outputs.public_subnets[0]
    ebs_optimized = true

    associate_public_ip_address = true
    availability_zone           = var.availability_zone
    disable_api_termination     = false

    credit_specification {
        cpu_credits = "unlimited"
    }

    metadata_options {
        http_endpoint               = "enabled"
        http_tokens                 = "optional"
        http_put_response_hop_limit = 1
    }


    tags = var.instance_tags

    vpc_security_group_ids = [
        data.terraform_remote_state.databases.outputs.db_security_group_id
    ]
}
