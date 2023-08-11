# Infrastructure as a Code: Terraform
## Amazon Web Service (AWS)

1. aws-cli install
    - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. terraform install
    - https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
3. `aws configure` and enter access key and secret key
    - `cat ~/.aws/credentials` 로 확인 가능
    - 현재 설정된 사용자 확인 : `aws sts get-caller-identity`
4. 조작할 서비스 폴더에서 `terraform init`, `terraform plan` 및 `terraform apply`
5. 서비스를 내려야 할 경우 `terraform destroy`

### VPC
#### default
- 가용영역 :"a", "c"
- 