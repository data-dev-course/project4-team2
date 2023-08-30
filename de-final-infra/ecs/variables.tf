variable "container_name" {
  default = "de-3-2-backend"
}

variable "container_port" {
  type    = number
  default = 80
}

variable "execution_role_arn" {
}

variable "env_key_name" {
  description = "ECS as environment variables."
}

variable "env_key_secret_name" {
  description = "ECS as environment variables. ACCESS KEY"
}

variable "env_key_value" {
  description = "ECS as environment variables."
}

variable "env_key_secret_value" {
  description = "ECS as environment variables. ACCESS KEY"
}

variable "alb_target_group_arn" {}