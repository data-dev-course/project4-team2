# Create ECS cluster
resource "aws_ecs_cluster" "ecs" {
  name = "de-3-2-cluster"
}

resource "aws_secretsmanager_secret" "access_key" {
  name = "dev/de-3-2/env-access-key"
}

resource "aws_secretsmanager_secret_version" "access_key" {
  secret_id = aws_secretsmanager_secret.access_key.id
  secret_string = var.env_key_value
}

resource "aws_secretsmanager_secret" "access_key_secret" {
  name = "dev/de-3-2/env-access-secret-key"
}

resource "aws_secretsmanager_secret_version" "access_key_secret" {
  secret_id = aws_secretsmanager_secret.access_key_secret.id
  secret_string = var.env_key_secret_value
}

# Create ECS task definition with Fargate
resource "aws_ecs_task_definition" "ecs" {
  family                   = "de-3-2-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024" # 1 cpu
  memory                   = "2048" # 2gb
  execution_role_arn = var.execution_role_arn
  container_definitions = jsonencode([{
    "name"  = "de-3-2-backend",
    "image" = "${aws_ecr_repository.repo.repository_url}:latest",
    "portMappings" = [{
      "containerPort" = 80,
      "hostPort" = 80
    }],
    "secrets" = [{
      "name" = var.env_key_name,
      "valueFrom" = aws_secretsmanager_secret.access_key.arn
    },{
      "name" = var.env_key_secret_name,
      "valueFrom" = aws_secretsmanager_secret.access_key_secret.arn
    }],
  }])

  #container_definitions = jsonencode([{
  #  name  = "de-3-2-backend"
  #  image = "${aws_ecr_repository.repo.repository_url}:latest"
  #  portMappings = [{
  #    containerPort = 80,
  #    hostPort = 80
  #  }]
  #  environment: [{
  #    name: var.env_key_name,
  #    value: var.env_key_value
  #  },{
  #    name: var.env_key_secret_name,
  #    value: var.env_key_secret_value
  #  }]
  #  logConfiguration : {
  #      logDriver : "awslogs",
  #      options : {
  #        "awslogs-region" : "ap-northeast-2",
  #        "awslogs-group" : "/ecs/de-3-2-backend",
  #        "awslogs-stream-prefix" : "ecs"
  #      }
  #    }
  #}])
}

# Create ECS service with Fargate launch type
resource "aws_ecs_service" "ecs" {
  name            = "service-backend"
  cluster         = aws_ecs_cluster.ecs.id
  task_definition = aws_ecs_task_definition.ecs.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets = data.terraform_remote_state.vpc.outputs.ecs_private_subnets # Replace with your actual subnet IDs
    security_groups = [data.terraform_remote_state.vpc.outputs.aws_security_group_default_id] # Replace with your security group ID
  }
}