# EKS HPA + Karpenter autoscailing

게시일: 2025-08-26T06:24:11.336Z
시리즈: AWS

---

클라우드 환경에서 애플리케이션을 운영하다 보면, **'리소스 관리'**
라는 풀리지 않는 숙제와 마주하게 됩니다. 
갑작스러운 트래픽 폭증으로 서비스가 마비되거나, 반대로 한산한 시간에도 비싼 자원을 낭비하고 있지는 않으신가요? 
사용량 예측에 실패하여 새벽에 긴급 대응을 하거나, 매달 날아오는 청구서에 한숨 쉬는 경험은 이제 그만할 때가 되었습니다.

이러한 고민을 해결할 열쇠는 바로 **'오토스케일링'** 에 있습니다. 
이번 포스트에서 **HPA(Horizontal Pod Autoscaler)** 와 **Karpenter** 를 조합하여 애플리케이션의 부하에 따라 파드(Pod)와 노드(Node)가 알아서 늘어나고 줄어드는 **'완전 자동화된 오토스케일링'** 시스템을 Terraform으로 구축하는 방법을 공유합니다.

- **HPA (Horizontal Pod Autoscaler)** : 애플리케이션의 CPU, 메모리 사용량을 감지하여 파드(Pod)의 개수를 신속하게 조절합니다.
- **Karpenter** : HPA로 인해 늘어난 파드를 배치할 공간이 부족할 때, 필요한 사양의 노드(EC2 인스턴스)를 즉시 생성하고, 반대로 불필요해진 노드는 제거하여 클러스터 전체의 비용 효율성을 극대화합니다.


# 전체아키텍쳐
1. Terraform을 사용하여 AWS의 기본 인프라(VPC, Subnet, NAT Gateway, Bastion Host, RDS)와 EKS 클러스터를 프로비저닝합니다.

2. Bastion Host를 통해 EKS 클러스터에 접근하여 AWS Load Balancer Controller, Metrics Server, Karpenter를 설치합니다.

3. 애플리케이션(Frontend, Backend)을 배포하고, 외부 트래픽을 처리하기 위해 Ingress를 생성합니다.

4. Backend Deployment에 HPA를 적용하여 CPU/Memory 사용량에 따라 파드가 자동으로 확장/축소되도록 설정합니다.

5. Karpenter는 스케줄링 대기 중인 파드를 감지하고, NodePool 설정에 따라 최적의 EC2 인스턴스를 프로비저닝하여 파드를 배치합니다.

![](https://velog.velcdn.com/images/agline/post/20b0dff3-e0cb-4334-9eb0-021346343a88/image.png)

# 1단계: Terraform으로 인프라 구축하기

## VPC, subnet 가용영역 a,b 두개
```
provider "aws" {
  region = "ap-northeast-2"
}

data "aws_availability_zones" "available" {}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "my-vpc"
  }
}

# 인터넷 게이트웨이
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "my-igw"
  }
}

# 퍼블릭 서브넷
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = element(["10.0.1.0/24", "10.0.2.0/24"], count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = element(["my-pub-2a", "my-pub-2b"], count.index)
  }
}

# 프라이빗 서브넷
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = element(["10.0.101.0/24", "10.0.102.0/24"], count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = element(["my-pvt-2a", "my-pvt-2b"], count.index)
  }
}

# 퍼블릭 NACL
resource "aws_network_acl" "public" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  ingress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "my-nacl-pub"
  }
}

# 프라이빗 NACL
resource "aws_network_acl" "private" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  ingress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "my-nacl-pvt"
  }
}

# 퍼블릭 서브넷에 퍼블릭 NACL 연결
resource "aws_network_acl_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  network_acl_id = aws_network_acl.public.id
}

# 프라이빗 서브넷에 프라이빗 NACL 연결
resource "aws_network_acl_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  network_acl_id = aws_network_acl.private.id
}

# 퍼블릭 라우팅 테이블
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "my-rtb-pub"
  }
}

# 프라이빗 라우팅 테이블 (기본 설정)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "my-rtb-pvt"
  }
}

# 퍼블릭 서브넷에 라우팅 테이블 연결
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# 프라이빗 서브넷에 라우팅 테이블 연결
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

#출력
output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
```
## EKS 설정을 위한 EIP, NAT Gateway

```
locals {
  vpc_id           = "vpc-example"
  public_subnet_ids = ["subnet-example", "subnet-example"]
  private_subnet_ids = ["subnet-example", "subnet-example"]
}

# 1. Elastic IP for NAT
resource "aws_eip" "nat_eip" {}

# 2. NAT Gateway (퍼블릭 서브넷에 생성해야 함)
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = "subnet-example"  # 퍼블릭 서브넷 중 하나
  tags = {
    Name = "my-nat-gw"
  }
}

# 3. 프라이빗 라우팅 테이블 NAT Gateway 라우팅
resource "aws_route" "private" {
  route_table_id       = "rtb-example"
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id       = aws_nat_gateway.nat.id
}
```
## EKS접근을 위한 Bastion EC2
```
provider "aws" {
  region = "ap-northeast-2"

  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

##########################
# Bastion 보안 그룹
##########################

resource "aws_security_group" "bastion_sg" {
  name        = "bastion-sg"
  description = "Allow SSH"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "bastion-sg"
  }
}

resource "aws_iam_role" "bastion_role" {
  name = "bastionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "bastion_policy" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/AdministratorAccess"
  ])
  role       = aws_iam_role.bastion_role.name
  policy_arn = each.value
}

resource "aws_iam_instance_profile" "bastion_profile" {
  name = "bastionInstanceProfile"
  role = aws_iam_role.bastion_role.name
}

##########################
# Bastion EC2 인스턴스
##########################

resource "aws_instance" "bastion" {
  ami                   = "ami-0fc8aeaa301af7663"
  instance_type         = "t3.micro"
  subnet_id             = local.public_subnet_ids[0]
  key_name              = "bastion-key"
  vpc_security_group_ids = [aws_security_group.bastion_sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.bastion_profile.name

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y unzip curl wget
              # AWS CLI v2 설치
              curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
              unzip awscliv2.zip
              ./aws/install
              # MariaDB 클라이언트 설치
              yum install -y mariadb105
              # git 설치
              sudo yum install -y git
              # kubectl 설치
              curl -LO https://dl.k8s.io/release/v1.33.0/bin/linux/amd64/kubectl
              chmod +x kubectl
              mv kubectl /usr/local/bin/
              # k9s 설치
              K9S_URL=$(curl -s https://api.github.com/repos/derailed/k9s/releases/latest \
                | grep "browser_download_url.*Linux_amd64.tar.gz" \
                | cut -d '"' -f 4 \
                | head -n 1)
              wget "$K9S_URL" -O k9s_Linux_amd64.tar.gz
              tar -xvf k9s_Linux_amd64.tar.gz
              mv k9s /usr/local/bin/
              rm -f k9s_Linux_amd64.tar.gz
              # AWS CLI 기본 설정
              mkdir -p /home/ec2-user/.aws
              cat > /home/ec2-user/.aws/credentials <<EOL
              [default]
              aws_access_key_id = ${var.aws_access_key_id}
              aws_secret_access_key = ${var.aws_secret_access_key}
              EOL
              cat > /home/ec2-user/.aws/config <<EOL
              [default]
              region = ap-northeast-2
              output = json
              EOL
              chown -R ec2-user:ec2-user /home/ec2-user/.aws
              EOF

  tags = {
    Name = "bastion"
  }
}
```
## RDS
```
##########################
# RDS 보안 그룹 (MariaDB용)
##########################

resource "aws_security_group" "rds_sg" {
  name   = "rds-sg"
  vpc_id = local.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion_sg.id]  
    description 	= Bastion에서 접근 허용
  }

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_eks_cluster.main.vpc_config[0].cluster_security_group_id]
    description     = EKS 클러스터 접근 허용
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds-sg"
  }
}

##########################
# RDS 서브넷 그룹
##########################

resource "aws_db_subnet_group" "mariadb_subnet_group" {
  name       = "mariadb-subnet-group"
  subnet_ids = local.private_subnet_ids

  tags = {
    Name = "mariadb-subnet-group"
  }
}

##########################
# RDS 인스턴스 (MariaDB)
##########################

resource "aws_db_instance" "mariadb" {
  identifier              = "mariadb-instance"
  allocated_storage       = 20
  engine                  = "mariadb"
  engine_version          = "10.6"
  instance_class          = "db.t3.small"
  db_name                 = "mydb"
  username                = "admin"
  password                = "MySecurePass123!"  # 테스트용. 운영 시 Secrets Manager 사용 권장
  skip_final_snapshot     = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  db_subnet_group_name    = aws_db_subnet_group.mariadb_subnet_group.name

  tags = {
    Name = "mariadb"
  }
}
```
## EKS cluster, NodeGroup 생성
```
##########################
# EKS 클러스터 IAM Role
##########################

resource "aws_iam_role" "eks_role" {
  name = "eksClusterRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_attach" {
  role       = aws_iam_role.eks_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

##########################
# EKS 클러스터
##########################

resource "aws_eks_cluster" "main" {
  name     = "my-eks-cluster"
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids = local.private_subnet_ids
  }

  depends_on = [aws_iam_role_policy_attachment.eks_attach]
}

##########################
# EKS 노드 그룹 IAM Role & Instance Profile
##########################

resource "aws_iam_role" "eks_node_role" {
  name = "eksNodeGroupRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_node_policy" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  ])

  role       = aws_iam_role.eks_node_role.name
  policy_arn = each.value
}

# Karpenter에서 참조할 EKS 노드 인스턴스 프로파일을 명시적으로 생성
resource "aws_iam_instance_profile" "eks_node_profile" {
  name = "eksNodeGroupProfile"
  role = aws_iam_role.eks_node_role.name
}

##########################
# EKS Managed Node Group
##########################

resource "aws_eks_node_group" "node_group" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "my-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = local.private_subnet_ids

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 1
  }

  instance_types = ["t3.small"]

  disk_size = 20

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_eks_cluster.main
  ]

  tags = {
    Name = "eks-node-group"
  }
}
```
# 2단계: 클러스터에 주요 컴포넌트 설치하기
## AWS Load Balancer Controller (LBC)
https://github.com/kubernetes-sigs/aws-load-balancer-controller/blob/main/docs/install/iam_policy.json
```
##########################
# LBC IAM
##########################
data "aws_eks_cluster" "cluster" {
  name = aws_eks_cluster.main.name
}

data "aws_eks_cluster_auth" "cluster" {
  name = aws_eks_cluster.main.name
}

data "tls_certificate" "eks_cluster" {
  url = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "oidc_provider" {
  url           = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks_cluster.certificates[0].sha1_fingerprint]
}

resource "aws_iam_policy" "lbc_policy" {
  name        = "AWSLoadBalancerControllerIAMPolicy"
  description = "Policy for AWS Load Balancer Controller"
  policy      = file("iam_policy_lbc.json")
}

resource "aws_iam_role" "lbc_sa_role" {
  name = "lbc-sa-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Federated = aws_iam_openid_connect_provider.oidc_provider.arn },
      Action    = "sts:AssumeRoleWithWebIdentity",
      Condition = {
        StringEquals = {
          "${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:kube-system:aws-load-balancer-controller"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lbc_attach" {
  role       = aws_iam_role.lbc_sa_role.name
  policy_arn = aws_iam_policy.lbc_policy.arn
}

##########################
# LBC 설치
##########################
resource "null_resource" "install_lbc" {
  depends_on = [
    aws_instance.bastion,
    aws_eks_cluster.main,
    aws_eks_node_group.node_group,
    aws_iam_role_policy_attachment.lbc_attach
  ]

  connection {
    type        = "ssh"
    host        = aws_instance.bastion.public_ip
    user        = "ec2-user"
    private_key = file("C:/.ssh/bastion-key.pem")
    timeout     = "10m"
  }

  provisioner "remote-exec" {
    inline = [
      "until aws eks --region ap-northeast-2 describe-cluster --name my-eks-cluster --query cluster.status --output text | grep -q 'ACTIVE'; do echo 'Waiting for EKS cluster to become active...'; sleep 30; done",
      "aws eks update-kubeconfig --region ap-northeast-2 --name my-eks-cluster",
      "curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash",
      "helm repo add eks https://aws.github.io/eks-charts",
      "helm repo update",

      "kubectl create ns kube-system || true",

      # 기존 설치 완전히 정리
      "echo 'Cleaning up existing installation...'",
      "helm uninstall aws-load-balancer-controller -n kube-system || true",
      "kubectl delete deployment aws-load-balancer-controller -n kube-system || true",
      "kubectl delete serviceaccount aws-load-balancer-controller -n kube-system || true",
      "kubectl delete secrets -l name=aws-load-balancer-controller -n kube-system || true",

      <<-EOT
      cat <<EOF | kubectl apply -f -
      apiVersion: v1
      kind: ServiceAccount
      metadata:
        name: aws-load-balancer-controller
        namespace: kube-system
        annotations:
          eks.amazonaws.com/role-arn: ${aws_iam_role.lbc_sa_role.arn}
        labels:
          app.kubernetes.io/name: aws-load-balancer-controller
          app.kubernetes.io/component: controller
      EOF
      EOT
      ,
      
      # Helm으로 설치 (서비스 어카운트는 생성하지 않고 기존 것 사용)
      "helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=my-eks-cluster --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller --set region=ap-northeast-2 --set vpcId=${local.vpc_id}"
    ]
  }
}
```
## Metrics Server
```
############################################
# Metrics Server Helm 설치
############################################
resource "null_resource" "install_metrics_server" {
  depends_on = [
    null_resource.install_karpenter
  ]

  connection {
    type        = "ssh"
    host        = aws_instance.bastion.public_ip
    user        = "ec2-user"
    private_key = file("C:/.ssh/bastion-key.pem")
  }

  provisioner "remote-exec" {
    inline = [
      "helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/",
      "helm repo update",
      "helm upgrade --install metrics-server metrics-server/metrics-server --namespace kube-system",
      "echo 'Metrics Server installation complete.'"
    ]
  }
}
```
## Karpenter

https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/#create-the-karpentercontroller-iam-role
```
############################################
# Karpenter IAM Role & Policy
############################################
resource "aws_iam_role" "karpenter_controller_role" {
  name = "KarpenterControllerRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Federated = aws_iam_openid_connect_provider.oidc_provider.arn
      },
      Action = "sts:AssumeRoleWithWebIdentity",
      Condition = {
        StringEquals = {
          "${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:karpenter:karpenter"
        }
      }
    }]
  })
}

data "aws_caller_identity" "current" {}

resource "aws_iam_policy" "karpenter_controller_policy" {
  name   = "KarpenterControllerPolicy"
  policy = templatefile("karpenter-controller-policy.json", {
    AWS_PARTITION  = "aws"
    AWS_ACCOUNT_ID = data.aws_caller_identity.current.account_id
    AWS_REGION     = "ap-northeast-2"
    CLUSTER_NAME   = aws_eks_cluster.main.name
  })
}

resource "aws_iam_role_policy_attachment" "karpenter_controller_attach" {
  role       = aws_iam_role.karpenter_controller_role.name
  policy_arn = aws_iam_policy.karpenter_controller_policy.arn
}

############################################
# 서브넷과 보안그룹에 Karpenter 태그 추가
############################################
resource "aws_ec2_tag" "private_subnet_tags" {
  count       = length(local.private_subnet_ids)
  resource_id = local.private_subnet_ids[count.index]
  key         = "karpenter.sh/discovery"
  value       = aws_eks_cluster.main.name
}

# EKS 클러스터의 보안그룹에 태그 추가
resource "aws_ec2_tag" "cluster_security_group_tag" {
  resource_id = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
  key         = "karpenter.sh/discovery"
  value       = aws_eks_cluster.main.name
}

############################################
# Karpenter Helm 설치
############################################
resource "null_resource" "install_karpenter" {
  depends_on = [
    aws_instance.bastion,
    aws_eks_cluster.main,
    aws_eks_node_group.node_group,
    null_resource.install_lbc,
    aws_ec2_tag.private_subnet_tags,
    aws_ec2_tag.cluster_security_group_tag
  ]

  connection {
    type        = "ssh"
    host        = aws_instance.bastion.public_ip
    user        = "ec2-user"
    private_key = file("C:/.ssh/bastion-key.pem")
  }

  provisioner "remote-exec" {
    inline = [
      <<EOT
      # LBC deployment가 준비될 때까지 기다립니다.
      kubectl wait --namespace=kube-system deployment/aws-load-balancer-controller --for=condition=Available=True --timeout=5m
      
      helm repo add karpenter https://charts.karpenter.sh/
      helm repo update
      kubectl create namespace karpenter || true
      
      # Karpenter v1.6.0 설치
      helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version 1.6.0 \
        --namespace karpenter \
        --create-namespace \
        --set "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${aws_iam_role.karpenter_controller_role.arn}" \
        --set "settings.clusterName=${aws_eks_cluster.main.name}" \
        --set "settings.clusterEndpoint=${aws_eks_cluster.main.endpoint}" \
        --set "settings.defaultInstanceProfile=${aws_iam_instance_profile.eks_node_profile.name}" \
        --set "tolerations[0].key=karpenter.sh/unschedulable" \
        --set "tolerations[0].operator=Exists" \
        --set "tolerations[0].effect=NoSchedule" \
        --set "replicas=1" \
        --set "topologySpreadConstraints[0].maxSkew=2" \
        --set "topologySpreadConstraints[0].topologyKey=topology.kubernetes.io/zone" \
        --set "topologySpreadConstraints[0].whenUnsatisfiable=ScheduleAnyway" \
        --set "topologySpreadConstraints[0].labelSelector.matchLabels.app\\.kubernetes\\.io/name=karpenter"
      EOT
    ]
  }
}
```
### 1. Karpenter IAM Role & Policy
```
resource "aws_iam_role" "karpenter_controller_role" {
  name = "KarpenterControllerRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Federated = aws_iam_openid_connect_provider.oidc_provider.arn
      },
      Action = "sts:AssumeRoleWithWebIdentity",
      Condition = {
        StringEquals = {
          "${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:karpenter:karpenter"
        }
      }
    }]
  })
}
```
- Principal: Federated = aws_iam_openid_connect_provider.oidc_provider.arn
	- EKS 클러스터의 OIDC Identity Provider를 통해 인증

- Action: sts:AssumeRoleWithWebIdentity
	- Kubernetes 서비스 어카운트가 AWS IAM 역할을 assume할 수 있게 함
- Condition: StringEquals
	- 특정 서비스 어카운트(system:serviceaccount:karpenter:karpenter)만 이 역할을 사용할 수 있도록 제한

#### EKS에서 OIDC를 왜 사용할까? 
**OIDC (OpenID Connect)**는 OAuth 2.0 위에 구축된 신원 인증 프로토콜입니다.

> 🤔 Kubernetes Pod이 AWS 서비스를 사용하려면?
   → AWS 액세스 키가 필요
   → 하지만 Pod에 키를 하드코딩하는 것은 보안상 위험!
   ✅ Pod → Kubernetes Service Account → AWS IAM Role
   안전하고 자동화된 방식으로 AWS 권한 획득!
   

```
data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer

실제 값 예시
https://oidc.eks.ap-northeast-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E

URL에서 "https://" 제거
replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", ""):sub

결과
oidc.eks.ap-northeast-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E:sub

실제 완성된 조건문
{
  "oidc.eks.ap-northeast-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E:sub": "system:serviceaccount:karpenter:karpenter"
}
```

>🔒 이 조건문의 보안 효과:
❌ 다른 네임스페이스의 Service Account → 접근 거부
❌ 다른 이름의 Service Account → 접근 거부  
❌ 일반 사용자나 다른 인증 방식 → 접근 거부
✅ karpenter 네임스페이스의 karpenter Service Account만 → 접근 허용

#### AWS Account ID 가져오기
```
data "aws_caller_identity" "current" {}
```
현재 AWS 계정의 ID를 동적으로 가져와 정책에서 사용합니다.

#### Karpenter Controller Policy
```
resource "aws_iam_policy" "karpenter_controller_policy" {
  name   = "KarpenterControllerPolicy"
  policy = templatefile("karpenter-controller-policy.json", {
    AWS_PARTITION  = "aws"
    AWS_ACCOUNT_ID = data.aws_caller_identity.current.account_id
    AWS_REGION     = "ap-northeast-2"
    CLUSTER_NAME   = aws_eks_cluster.main.name
  })
}
```
**templatefile 함수**:
- 외부 JSON 파일(karpenter-controller-policy.json)을 템플릿으로 사용
변수들을 동적으로 치환하여 정책 생성

**주요 권한 (일반적으로 포함되는 것들)**:
- EC2 인스턴스 생성/삭제/수정
- Auto Scaling Group 관리
- IAM 인스턴스 프로파일 연결
- 태그 관리
- EKS 노드 그룹 관리

### 2. 서브넷과 보안그룹에 Karpenter 태그 추가
```
resource "aws_ec2_tag" "private_subnet_tags" {
  count       = length(local.private_subnet_ids)
  resource_id = local.private_subnet_ids[count.index]
  key         = "karpenter.sh/discovery"
  value       = aws_eks_cluster.main.name
}
```
Karpenter가 노드를 배포할 서브넷을 프라이빗 서브넷으로 식별할 수 있도록 태그 추가
Karpenter는 이 태그를 통해 어느 서브넷에 새 노드를 생성할지 결정
### 3. karpneter helm 설치
```
Karpenter v1.6.0 설치
helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version 1.6.0 \
--namespace karpenter \
--create-namespace \
--set "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${aws_iam_role.karpenter_controller_role.arn}" \
--set "settings.clusterName=${aws_eks_cluster.main.name}" \
--set "settings.clusterEndpoint=${aws_eks_cluster.main.endpoint}" \
--set "settings.defaultInstanceProfile=${aws_iam_instance_profile.eks_node_profile.name}" \
--set "tolerations[0].key=karpenter.sh/unschedulable" \ → "교체 예정 노드에서도 실행할 수 있어"
--set "tolerations[0].operator=Exists" \ → "값이 뭐든 상관없어, 유연하게 대응할게"
--set "tolerations[0].effect=NoSchedule" \ → "스케줄링 제한은 괜찮지만 강제 축출은 싫어"
--set "replicas=1" \ → "나 혼자서도 충분해, 리소스 아끼자"
--set "topologySpreadConstraints[0].maxSkew=2" \ → "영역 간 차이가 2개 이하면 괜찮아"
--set "topologySpreadConstraints[0].topologyKey=topology.kubernetes.io/zone" \ → "가용영역별로 분산해줘"
--set "topologySpreadConstraints[0].whenUnsatisfiable=ScheduleAnyway" \ → "완벽하지 않아도 일단 실행하는 게 중요해"
--set "topologySpreadConstraints[0].labelSelector.matchLabels.app\\.kubernetes\\.io/name=karpenter" → "이 정책은 나(Karpenter)에게만 적용해줘"
```
#### tolerations[0].key=karpenter.sh/unschedulable
```
실제상황예시:

상황: 노드 A가 교체 예정 상태
  ↓
기존 Pod들: "이 노드 위험해, 다른 곳으로 피하자!" 🏃‍♂️
  ↓  
Karpenter: "어? 그럼 내가 누가 새 노드 만들어줘?" 🤔
  ↓
Karpenter가 피해버리면: 새 노드 생성 불가! 😱

왜 필요한가?
일반 앱 Pod: 교체 예정 노드 피함 (데이터 보호)
Karpenter: 교체 예정 노드에서도 실행 (서비스 연속성)

```
#### tolerations[0].operator=Exists
```
실제상황예시:

시나리오 1: Taint 값이 "replacing"
노드 상태: karpenter.sh/unschedulable=replacing

시나리오 2: Taint 값이 "draining"  
노드 상태: karpenter.sh/unschedulable=draining

시나리오 3: Taint 값이 "upgrading"
노드 상태: karpenter.sh/unschedulable=upgrading

만약 특정 값만 허용한다면?
이렇게 설정했다면:
tolerations:
- key: karpenter.sh/unschedulable
  value: "replacing"  # 특정 값만!
  operator: Equal
  
문제 발생:
- "draining" 상태에서는 실행 불가 ❌
- "upgrading" 상태에서도 실행 불가 ❌
→ Karpenter 서비스 중단! 😱

Exists의 장점:
operator: Exists = "키만 있으면 값은 뭐든 OK!"
→ 모든 교체 시나리오에 대응 가능 ✅
```
#### tolerations[0].effect=NoSchedule
```
NoSchedule vs NoExecute 차이:
- NoSchedule: "새로 스케줄링 안 해줄래" (기존 것은 계속 실행)
- NoExecute:  "기존 것도 강제로 쫓아낼래" (즉시 종료)

실제상황예시:
상황: 노드에 NoExecute Taint 적용됨
  ↓
Karpenter Pod: 즉시 강제 종료 😵
  ↓
새로운 스케일링 요청: "Karpenter 어디갔어?" 🤷‍♂️
  ↓  
결과: 클러스터 스케일링 마비! 😱

왜 NoSchedule만?
NoSchedule Toleration:
- 기존 Karpenter Pod: 계속 실행 ✅
- 새 Karpenter Pod: 다른 노드에 스케줄링 ✅
- 서비스 연속성: 보장됨 ✅
```
#### replicas=1
```
Karpenter의 주요 업무:
1. 클러스터 상태 모니터링 
2. 스케일링 결정  
3. AWS API 호출 
4. 노드 생성/삭제 지시 

왜 한개면 충분할까?
❌ 여러 개가 동시에 같은 일을 하면:
   Pod A: "노드 3개 더 필요해!"
   Pod B: "노드 3개 더 필요해!"  
   결과: 6개 생성 → 자원 낭비 😱

✅ 1개가 모든 걸 관리하면:
   단일 결정자: "노드 3개만 추가하자"
   결과: 정확히 3개 생성 → 효율적!

Karpenter의 고가용성은?
한개로 운영중인 Karpenter Pod 죽으면?
→ Kubernetes Deployment가 자동으로 재시작
→ 잠깐 중단되지만 곧 복구 ✅

vs 여러 개 Karpenter Pod 운영 시:
→ 복잡한 리더 선출 필요
→ 동시성 제어 복잡
→ 리소스 낭비
```
#### maxSkew=2
```
실제 가용영역 시나리오:
현재 상황:
- AZ-A: Karpenter Pod 0개
- AZ-B: Karpenter Pod 1개  
- AZ-C: Karpenter Pod 0개

차이: 최대 1개 (1-0=1) → maxSkew=2 조건 만족 ✅

왜 2개까지 허용?
너무 엄격한 경우 (maxSkew=0):
- AZ-A: 0개, AZ-B: 1개 → 차이 1개 ❌
- 새 Pod을 AZ-A나 AZ-C에 강제로 배치
- 하지만 그 영역에 적절한 노드가 없을 수도...

적당히 유연한 경우 (maxSkew=2):
- AZ-A: 0개, AZ-B: 2개, AZ-C: 0개 → 차이 2개 ✅  
- 여전히 분산되어 있고, 스케줄링도 유연함

실제 장애 상황:
AZ-A 장애 발생! 🔥
- maxSkew=0: Pod이 AZ-A에 없어서 스케줄링 실패 ❌
- maxSkew=2: AZ-B나 AZ-C에 여유롭게 배치 ✅
```
#### whenUnsatisfiable=ScheduleAnyway
```
완벽한 분산이 불가능한 상황들:

상황 1: 노드 부족
클러스터 구성:
- AZ-A: 노드 있음 ✅
- AZ-B: 노드 없음 ❌  
- AZ-C: 노드 없음 ❌

완벽한 분산 요구 시: 스케줄링 실패 ❌
유연한 정책: AZ-A에라도 배치 ✅

상황 2: 리소스 부족
리소스 요구사항:
- Karpenter Pod: CPU 500m, Memory 512Mi 필요

현재 상황:
- AZ-A: 리소스 충분 ✅
- AZ-B: 리소스 부족 ❌
- AZ-C: 리소스 부족 ❌

결과: AZ-A에 배치되어 서비스 계속 제공 ✅

DoNotSchedule vs ScheduleAnyway:
DoNotSchedule: "완벽하지 않으면 아예 실행 안 해!"
→ Karpenter 서비스 중단 가능 😱

ScheduleAnyway: "불완전해도 일단 실행해서 서비스 유지!"  
→ 고가용성 우선 ✅
```
#### labelSelector.matchLabels.app\\.kubernetes\\.io/name=karpenter
```
"다른 Pod들이 안정적으로 실행될 수 있도록 노드를 관리하는 것"

따라서: 
1. 다른 Pod들이 피하는 노드에서도 → 나는 실행되어야 함
2. 어떤 상황에서든 → 유연하게 대응해야 함  
3. 강제 종료되면 안 되고 → 서비스 연속성 유지
4. 효율적으로 → 리소스 낭비 금지
5. 가용성을 위해 → 적당한 분산
6. 완벽하지 않아도 → 서비스가 먼저
```

#### 결국 이 모든 설정은 "Karpenter가 어떤 상황에서든 안정적으로 실행되어, 클러스터 전체의 안정성과 비용 효율성을 보장하기 위함"입니다! 
# 3단계: Karpenter NodePool & EC2NodeClass
```
############################################
# Karpenter v1.6.0 NodePool & EC2NodeClass 생성
############################################
resource "null_resource" "karpenter_nodepool" {
  depends_on = [null_resource.install_karpenter]
  
  connection {
    type        = "ssh"
    host        = aws_instance.bastion.public_ip
    user        = "ec2-user"
    private_key = file("C:/.ssh/bastion-key.pem")
  }
  
  provisioner "remote-exec" {
    inline = [
      <<-EOT
      echo "Waiting for Karpenter controller to become available..."
      kubectl wait --namespace=karpenter deployment/karpenter --for=condition=Available=True --timeout=10m

      echo "Waiting for Karpenter CRDs to be established..."
      # CRD가 등록될 때까지 대기
      kubectl wait --for condition=established --timeout=300s crd/nodepools.karpenter.sh
      kubectl wait --for condition=established --timeout=300s crd/ec2nodeclasses.karpenter.k8s.aws

      # CRD 상태 확인
      echo "Checking CRD status..."
      kubectl get crd | grep karpenter

      # API 버전 확인
      echo "Checking available API versions..."
      kubectl api-resources | grep -E "(nodepool|ec2nodeclass)"

      # 추가 대기 시간
      sleep 30

      # EC2NodeClass 생성 (v1 API)
      echo "Creating EC2NodeClass..."
      cat <<EOF | kubectl apply -f -
      apiVersion: karpenter.k8s.aws/v1
      kind: EC2NodeClass
      metadata:
        name: default
      spec:
        # AMI 설정
        amiSelectorTerms:
          - alias: al2023@latest # Karpenter가 제공하는 AL2023 AMI 사용
        
        # 서브넷 선택
        subnetSelectorTerms:
          - tags:
              karpenter.sh/discovery: "${aws_eks_cluster.main.name}"
        
        # 보안 그룹 선택
        securityGroupSelectorTerms:
          - tags:
              karpenter.sh/discovery: "${aws_eks_cluster.main.name}"
        
        # IAM 인스턴스 프로파일
        instanceProfile: "${aws_iam_instance_profile.eks_node_profile.name}"
        
        # 사용자 데이터 스크립트
        userData: |
          #!/bin/bash
          /etc/eks/bootstrap.sh ${aws_eks_cluster.main.name}
          
          # 추가 설정
          echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
          sysctl -p /etc/sysctl.conf
        
        # 블록 디바이스 매핑
        blockDeviceMappings:
          - deviceName: /dev/xvda
            ebs:
              volumeSize: 20Gi
              volumeType: gp3
              deleteOnTermination: true
        
        # 메타데이터 서비스 설정
        metadataOptions:
          httpEndpoint: enabled
          httpProtocolIPv6: disabled
          httpPutResponseHopLimit: 2
          httpTokens: required
      EOF

      # EC2NodeClass 생성 확인
      if kubectl get ec2nodeclass default; then
        echo "EC2NodeClass created successfully"
      else
        echo "Failed to create EC2NodeClass"
        exit 1
      fi

      # 잠시 대기
      sleep 10

      # NodePool 생성 (v1 API)
      echo "Creating NodePool..."
      cat <<EOF | kubectl apply -f -
      apiVersion: karpenter.sh/v1
      kind: NodePool
      metadata:
        name: default
      spec:
        # 노드클래스 참조
        template:
          metadata:
            labels:
              intent: apps
              nodepool: default
          spec:
            # 노드 요구사항
            requirements:
              - key: kubernetes.io/arch
                operator: In
                values: ["amd64"]
              - key: karpenter.sh/capacity-type
                operator: In
                values: ["on-demand"]
              - key: node.kubernetes.io/instance-type
                operator: In
                values: ["t3.small"]
            
            # EC2NodeClass 참조
            nodeClassRef:
              group: karpenter.k8s.aws
              kind: EC2NodeClass
              name: default
        
        # 리소스 제한
        limits:
          cpu: 20
          memory: 40Gi
        
        # 노드 축출 정책
        disruption:
          # 빈 노드 축출 시간
          consolidationPolicy: WhenEmptyOrUnderutilized
          consolidateAfter: 5m
      EOF

      # NodePool 생성 확인
      if kubectl get nodepool default; then
        echo "NodePool created successfully"
      else
        echo "Failed to create NodePool"
        exit 1
      fi

      echo "Waiting for resources to be created..."
      sleep 15

      echo "Karpenter v1.6.0 NodePool and EC2NodeClass created successfully"

      # 생성된 리소스 확인
      echo "Checking created resources..."
      kubectl get nodepools -o wide
      kubectl get ec2nodeclasses -o wide

      EOT
    ]
  }
}
```
## CRD (Custom Resource Definition)
### CRD란?
- "새로운 언어 사전 만들기" Kubernetes를 언어라고 생각하면 됩니다.

**기본 Kubernetes 단어들 (내장 리소스):**
- Pod: "컨테이너 실행"
- Service: "네트워크 연결"
- Deployment: "애플리케이션 배포"
- Node: "서버"

**CRD = "새로운 단어 정의서":**
- NodePool: "노드 그룹 정책" (Karpenter가 만든 새 단어)
- EC2NodeClass: "AWS 노드 설정" (Karpenter가 만든 새 단어)

### Karpenter에서 CRD가 중요한 이유 
#### 1. Karpenter Controller 작동 방식
```
Karpenter Controller 시작
        ↓
"NodePool 리소스 변화 감지하겠어!"
        ↓
CRD 있나 확인
        ↓
❌ CRD 없음: "NodePool이 뭔지 몰라서 감지할 수 없어!" → 중단
✅ CRD 있음: "NodePool 변화를 감지하고 반응하겠어!" → 정상 작동
```
#### 2. 실제 노드 생성 프로세스
```
사용자가 NodePool 생성/수정
        ↓
Kubernetes API Server: "NodePool 리소스가 변경되었네"
        ↓
Karpenter Controller: "변경 감지! 새로운 노드가 필요한가?"
        ↓
EC2NodeClass 참조: "어떤 스펙의 서버를 만들지 확인"
        ↓
AWS EC2 API 호출: "실제 인스턴스 생성"
```
#### 3. CRD가 없다면?
```
❌ "NodePool이 뭔지 몰라요"
❌ Controller 아예 시작 안됨
❌ 노드 생성 불가능
```
### CRD의 실행을 기다림
```
echo "Waiting for Karpenter CRDs to be established..."
kubectl wait --for condition=established --timeout=300s crd/nodepools.karpenter.sh
kubectl wait --for condition=established --timeout=300s crd/ec2nodeclasses.karpenter.k8s.aws
```
**왜 기다려야할까?**
1. Karpenter Helm 설치 → CRD 생성 시작
2. CRD 완전 등록까지 시간 소요 (보통 30초~2분)
3. CRD 준비 완료 → NodePool/EC2NodeClass 생성 가능
## EC2NodeClass
### EC2NodeClass = "어떻게 만들까?" (HOW)
```
# EC2NodeClass는 EC2 인스턴스 생성 방법을 정의
spec:
  amiSelectorTerms: [...] # 어떤 AMI 사용할지
  userData: |             # 부팅 시 실행할 스크립트
    /etc/eks/bootstrap.sh
  blockDeviceMappings:    # 디스크 구성
    volumeSize: 20Gi
  metadataOptions:        # 보안 설정
    httpTokens: required
```
### EC2NodeClass가 담당하는 것들
```
AWS EC2 관련 모든 설정:
- AMI 선택 (운영체제)
- 보안그룹 (네트워크 방화벽)
- 서브넷 (네트워크 위치)
- IAM 인스턴스 프로파일 (권한)
- User Data (부팅 스크립트)
- EBS 볼륨 (스토리지)
- EC2 메타데이터 설정

→ "물리적 서버를 어떻게 구성할 것인가"
```
## NodePool
### NodePool = "언제, 얼마나 만들까?" (WHEN & HOW MANY)
```
# NodePool은 스케일링 조건과 제약을 정의
spec:
  requirements:           # 어떤 조건의 노드가 필요한지
    - key: node.kubernetes.io/instance-type
      values: ["t3.small"]
  limits:                 # 최대 얼마나 생성할지
    cpu: 20
  disruption:             # 언제 삭제할지
    consolidateAfter: 5m
```
### NodePool이 담당하는 것들
```
Kubernetes 스케일링 관련 모든 정책:
- 노드 요구사항 (인스턴스 타입, 아키텍처 등)
- 리소스 제한 (최대 CPU/메모리)
- 스케일링 정책 (언제 생성/삭제)
- 노드 라벨링
- Taints/Tolerations

→ "언제 얼마나 만들고 관리할 것인가"
```

## 1:N 관계 이해
### 하나의 EC2NodeClass, 여러 NodePool 가능
```
하나의 EC2NodeClass:
- 표준 AMI 설정
- 표준 보안 설정  
- 표준 네트워크 설정

여러 NodePool:
- 개발용 (작은 인스턴스)
- 운영용 (큰 인스턴스)  
- GPU용 (GPU 인스턴스)
- Spot용 (비용 절약)

→ 공통 인프라 설정은 재사용하면서 
  용도별 스케일링 정책은 분리
```
## EC2NodeClass VS NodePool
| 구분 | EC2NodeClass | NodePool |
| :--- | :--- | :--- |
| **역할** | AWS 인프라 템플릿 | Kubernetes 스케일링 정책 |
| **관심사** | HOW (어떻게 만들까) | WHEN/HOW MANY (언제/얼마나) |
| **설정 내용** | AMI, 보안그룹, 서브넷, 스토리지 | 인스턴스 타입, 리소스 제한, 스케일링 |
| **변경 빈도** | 낮음 (인프라 표준) | 높음 (워크로드별 요구사항) |
| **재사용성** | 높음 (여러 NodePool이 참조) | 낮음 (특정 용도) |