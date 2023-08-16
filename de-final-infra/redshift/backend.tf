terraform {
    backend "s3" {
        bucket         = "de-3-2" 
        key            = "terraform/redshift/terraform.tfstate" 
        region         = "ap-northeast-2"
        encrypt        = true
        dynamodb_table = "de-3-2-lock" 
    }
}