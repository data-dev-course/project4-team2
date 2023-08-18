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

- 가용영역 :"a", "c", "d"
- subnets
  - private subnets: 8
    - 3개는 private은 redshift, 3개는 rds instance (db), 2개는 mwaa 할당
    - 일반 private subnets들에 서비스별로 nat gateway 할당. (db는 없음)
    - 2개 rds instance는 subnet 그룹으로 묶여있음.
  - public subnets: 3
    - 인터넷 게이트웨이 할당됨.
- s3, api gateway 엔드포인트 생성됨

### Jenkins
이 폴더는 jenkins 구성 실패로 사용되지 않음.
ec2 인스턴스 구성 예시로 남겨둠.

### RDS
Postgres15 db instance로 구성되는 rds cluster.
1. '/databases'에서 init, plan, apply 진행 (route53 comment 처리)
2. '/databases/rds'에서 init, plan, apply 진행
3. 다시 '/databases'에서 route53 코멘트 처리 풀고, endpoint에 instance endpoint 입력 후 실행

- 가용영역 3곳의 db-private-subnet에서 작동, 메인 가용영역 ap-northeast-2d로 확인됨.
- 32GiB 할당