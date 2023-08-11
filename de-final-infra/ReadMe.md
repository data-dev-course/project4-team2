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

- 각 폴더에는 terraform.tfvars가 존재 -> 보안상의 이유로 gitignore 처리
### VPC

- 가용영역 :"a", "c"
- subnets
  - private subnets: 4
    - 2개는 일반 private, 2개는 rds instance 용
    - 일반 private subnets들에 nat gateway 각각 할당되어 있음.
    - 2개 rds instance는 subnet 그룹으로 묶여있음.
  - public subnets: 2
    - 인터넷 게이트웨이 할당됨.
- s3, api gateway 엔드포인트 생성됨

