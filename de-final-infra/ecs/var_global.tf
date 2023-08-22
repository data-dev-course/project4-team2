variable "account_id" {
  default = {
    prod     = "862327261051"
  }
}

# Remote State that will be used when creating other resources
# You can add any resource here, if you want to refer from others
variable "remote_state" {
  default = {
    # VPC
    vpc = {
      deapne2 = {
        region = "ap-northeast-2"
        bucket = "de-3-2"
        key    = "terraform/vpc/terraform.tfstate"
      }

      deapne2 = {
        region = "ap-northeast-2"
        bucket = "de-3-2"
        key    = "terraform/vpc/terraform.tfstate"
      }
    }


    # WAF ACL
    waf_web_acl_global = {
      prod = {
        region = ""
        bucket = ""
        key    = ""
      }
    }
  }
}