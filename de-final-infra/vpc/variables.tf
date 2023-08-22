variable "vpc_name" {
  description = "The name of the VPC"
}

variable "cidr_numeral" {
  description = "The VPC CIDR numeral (10.x.0.0/16)"
}

variable "aws_region" {
  default = "ap-northeast-2"
}

variable "shard_id" {
  default = ""
}

variable "shard_short_id" {
  default = ""
}

variable "cidr_numeral_public" {
  default = {
    "0" = "0"
    "1" = "16"
    "2" = "32"
  }
}

variable "cidr_numeral_private" {
  default = {
    "0" = "80"
    "1" = "96"
    "2" = "112"
  }
}

variable "cidr_numeral_private_mwaa" {
  default = {
    "0" = "128"
    "1" = "144"
  }
}

variable "cidr_numeral_private_db" {
  default = {
    "0" = "160"
    "1" = "176"
    "2" = "192"
  }
}

variable "cidr_numeral_private_ecs" {
  default = {
    "0" = "208"
    "1" = "224"
  }
}

variable "billing_tag" {
  description = "The AWS tag used to track AWS charges."
}

variable "availability_zones" {
  type        = list(string)
  description = "A comma-delimited list of availability zones for the VPC."
}


variable "availability_zones_without_b" {
  type        = list(string)
  description = "A comma-delimited list of availability zones except for ap-northeast-2b"
}

variable "subnet_no_private" {
  description = "This value means the number of private subnets"
  default     = "3"
}

variable "env_suffix" {
  description = "env suffix"
  default     = ""
}

# peering ID with artp VPC
variable "vpc_peer_connection_id_artp_apne2" {}
variable "destination_cidr_block" {}

#variable "vpc_peerings" {
#  description = "A list of maps containing key/value pairs that define vpc peering."
#  type        = list
#  default     = []
#}