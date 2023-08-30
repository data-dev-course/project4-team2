#alb.tf
resource "aws_lb_target_group" "alb_ecs_amplify" {
  name        = "alb-ecs-amplify"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
health_check {
    enabled = true
    path    = "/health"
  }
}
resource "aws_alb" "alb_ecs_amplify" {
  name               = "ecs-fastapi-lb"
  internal           = false
  load_balancer_type = "application"
subnets = [
    data.terraform_remote_state.vpc.outputs.public_subnets[1],
    data.terraform_remote_state.vpc.outputs.ecs_private_subnets[1]
    
  ]
security_groups = [
    data.terraform_remote_state.vpc.outputs.aws_security_group_default_id
  ]

}
resource "aws_alb_listener" "my_api_http" {
  load_balancer_arn = aws_alb.alb_ecs_amplify.arn
  port              = "8000"
  protocol          = "HTTP"
  default_action {
  type             = "forward"
  target_group_arn = aws_lb_target_group.alb_ecs_amplify.arn
    }

}