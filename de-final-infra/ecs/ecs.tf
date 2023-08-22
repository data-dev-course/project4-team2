module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "5.2.1"
  
  cluster_name = "de-3-2-cluster"

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = "/aws/ecs/de-3-2-ec2"
      }
    }
  }

  # Capacity provider
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 50
        base   = 20
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 50
      }
    }
  }

  services = {
    fast_api_backend = {
        cpu = 1024
        memory = 4096
        
        container_definitions = {
            fluent-bit = {
                cpu = 512
                memory = 1024
                essential = true
                image = "??"
                firelens_configuration = {
                    type = "fluentbit"
                }
                memory_reservation = 50
            }

            (var.container_name) = {
                cpu       = 512
                memory    = 1024
                essential = true
                image     = "??"
                port_mappings = [
                    {
                    name          = var.container_name
                    containerPort = var.container_port
                    hostPort      = var.container_port
                    protocol      = "tcp"
                    }
                ]
                readonly_root_filesystem = false

                dependencies = [{
                    containerName = "fluent-bit"
                    condition     = "START"
                }]

                enable_cloudwatch_logging = true

                memory_reservation = 100
                }
            }
            service_connect_configuration = {
                namespace = aws_service_discovery_http_namespace.this.arn
                service = {
                client_alias = {
                    port     = var.container_port
                    dns_name = var.container_name
                }
                port_name      = var.container_name
                discovery_name = var.container_name
                }
            }

            load_balancer = {
                service = {
                target_group_arn = element(module.alb.target_group_arns, 0)
                container_name   = var.container_name
                container_port   = var.container_port
                }
            }

            subnet_ids = data.terraform_remote_state.vpc.outputs.ecs_private_subnets

        }
    }
  }

  tags = {
    Environment = "dev"
    Name     = "de-3-2-cluster"
  }
}
