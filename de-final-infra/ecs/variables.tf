variable "container_name" {
  default = "de-3-2-backend"
}

variable "container_port" {
  type    = number
  default = 80
}

variable "execution_role_arn" {
}