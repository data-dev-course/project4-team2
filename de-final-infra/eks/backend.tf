terraform {
    backend "s3" {
        bucket         = "de-3-2" # 자신의 버킷으로 수정
        key            = "terraform/eks/terraform.tfstate" # 원하는 키 사용
        region         = "ap-northeast-2"
        encrypt        = true
        dynamodb_table = "de-3-2-lock" # 앞에서 생성한 DynamoDB 이름
    }
}