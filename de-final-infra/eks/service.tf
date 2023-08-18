module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.16.0"

  cluster_name = var.cluster_name
  cluster_version = "1.27"
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.vpc.outputs.private_subnets

  cluster_endpoint_public_access  = true 
  cloudwatch_log_group_retention_in_days = 1

  eks_managed_node_groups = {
    default_node_group = {
        min_size = 2
        max_size = 3
        desired_size = 2
        instance_types = ["m6i.large"]
    }
  }

  tags = {
    name = "de-3-2-eks"
    environment = "dev"
  }
}