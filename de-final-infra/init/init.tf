provider "aws" {
  region = "ap-northeast-2" # Please use the default region ID
}

# S3 bucket for backend
resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = "de-3-2"
  versioning_configuration {
    status = "Enabled"
  }
}

# DynamoDB for terraform state lock
resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "de-3-2-lock"
  hash_key       = "LockID"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "LockID"
    type = "S"
  }
}

variable "account_id" {
 default = "DE-3-2" # Please use the account alias for id
}