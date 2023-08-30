variable "ami" {
  description = "The AMI ID to use for the instance"
  type        = string
}
variable "availability_zone" {
  description = "The availability zone where the instance will be created"
  type        = string
  default     = "ap-northeast-2a"
}

variable "key_name" {
  description = "The key name to use for the instance"
  type        = string
  default     = "DE-3-2_bastion_key"
}
variable "instance_tags" {
  description = "Tags to be applied to the instance"
  type        = map(string)
  default     = {
    Name = "DE-3-2_bastion"
  }
}
