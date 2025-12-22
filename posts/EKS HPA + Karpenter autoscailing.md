# EKS HPA + Karpenter autoscailing

게시일: Tue, 26 Aug 2025 06:24:11 GMT
링크: https://velog.io/@agline/EKS-HPA-Karpenter-autoscailing

---

<p>클라우드 환경에서 애플리케이션을 운영하다 보면, <strong>'리소스 관리'</strong>
라는 풀리지 않는 숙제와 마주하게 됩니다. 
갑작스러운 트래픽 폭증으로 서비스가 마비되거나, 반대로 한산한 시간에도 비싼 자원을 낭비하고 있지는 않으신가요? 
사용량 예측에 실패하여 새벽에 긴급 대응을 하거나, 매달 날아오는 청구서에 한숨 쉬는 경험은 이제 그만할 때가 되었습니다.</p>
<p>이러한 고민을 해결할 열쇠는 바로 <strong>'오토스케일링'</strong> 에 있습니다. 
이번 포스트에서 <strong>HPA(Horizontal Pod Autoscaler)</strong> 와 <strong>Karpenter</strong> 를 조합하여 애플리케이션의 부하에 따라 파드(Pod)와 노드(Node)가 알아서 늘어나고 줄어드는 <strong>'완전 자동화된 오토스케일링'</strong> 시스템을 Terraform으로 구축하는 방법을 공유합니다.</p>
<ul>
<li><strong>HPA (Horizontal Pod Autoscaler)</strong> : 애플리케이션의 CPU, 메모리 사용량을 감지하여 파드(Pod)의 개수를 신속하게 조절합니다.</li>
<li><strong>Karpenter</strong> : HPA로 인해 늘어난 파드를 배치할 공간이 부족할 때, 필요한 사양의 노드(EC2 인스턴스)를 즉시 생성하고, 반대로 불필요해진 노드는 제거하여 클러스터 전체의 비용 효율성을 극대화합니다.</li>
</ul>
<h1 id="전체아키텍쳐">전체아키텍쳐</h1>
<ol>
<li><p>Terraform을 사용하여 AWS의 기본 인프라(VPC, Subnet, NAT Gateway, Bastion Host, RDS)와 EKS 클러스터를 프로비저닝합니다.</p>
</li>
<li><p>Bastion Host를 통해 EKS 클러스터에 접근하여 AWS Load Balancer Controller, Metrics Server, Karpenter를 설치합니다.</p>
</li>
<li><p>애플리케이션(Frontend, Backend)을 배포하고, 외부 트래픽을 처리하기 위해 Ingress를 생성합니다.</p>
</li>
<li><p>Backend Deployment에 HPA를 적용하여 CPU/Memory 사용량에 따라 파드가 자동으로 확장/축소되도록 설정합니다.</p>
</li>
<li><p>Karpenter는 스케줄링 대기 중인 파드를 감지하고, NodePool 설정에 따라 최적의 EC2 인스턴스를 프로비저닝하여 파드를 배치합니다.</p>
</li>
</ol>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/20b0dff3-e0cb-4334-9eb0-021346343a88/image.png" /></p>
<h1 id="1단계-terraform으로-인프라-구축하기">1단계: Terraform으로 인프라 구축하기</h1>
<h2 id="vpc-subnet-가용영역-ab-두개">VPC, subnet 가용영역 a,b 두개</h2>
<pre><code>provider &quot;aws&quot; {
  region = &quot;ap-northeast-2&quot;
}

data &quot;aws_availability_zones&quot; &quot;available&quot; {}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# VPC
resource &quot;aws_vpc&quot; &quot;main&quot; {
  cidr_block           = &quot;10.0.0.0/16&quot;
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = &quot;my-vpc&quot;
  }
}

# 인터넷 게이트웨이
resource &quot;aws_internet_gateway&quot; &quot;igw&quot; {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = &quot;my-igw&quot;
  }
}

# 퍼블릭 서브넷
resource &quot;aws_subnet&quot; &quot;public&quot; {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = element([&quot;10.0.1.0/24&quot;, &quot;10.0.2.0/24&quot;], count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = element([&quot;my-pub-2a&quot;, &quot;my-pub-2b&quot;], count.index)
  }
}

# 프라이빗 서브넷
resource &quot;aws_subnet&quot; &quot;private&quot; {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = element([&quot;10.0.101.0/24&quot;, &quot;10.0.102.0/24&quot;], count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = element([&quot;my-pvt-2a&quot;, &quot;my-pvt-2b&quot;], count.index)
  }
}

# 퍼블릭 NACL
resource &quot;aws_network_acl&quot; &quot;public&quot; {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = &quot;-1&quot;
    rule_no    = 100
    action     = &quot;allow&quot;
    cidr_block = &quot;0.0.0.0/0&quot;
    from_port  = 0
    to_port    = 0
  }

  ingress {
    protocol   = &quot;-1&quot;
    rule_no    = 100
    action     = &quot;allow&quot;
    cidr_block = &quot;0.0.0.0/0&quot;
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = &quot;my-nacl-pub&quot;
  }
}

# 프라이빗 NACL
resource &quot;aws_network_acl&quot; &quot;private&quot; {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = &quot;-1&quot;
    rule_no    = 100
    action     = &quot;allow&quot;
    cidr_block = &quot;0.0.0.0/0&quot;
    from_port  = 0
    to_port    = 0
  }

  ingress {
    protocol   = &quot;-1&quot;
    rule_no    = 100
    action     = &quot;allow&quot;
    cidr_block = &quot;0.0.0.0/0&quot;
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = &quot;my-nacl-pvt&quot;
  }
}

# 퍼블릭 서브넷에 퍼블릭 NACL 연결
resource &quot;aws_network_acl_association&quot; &quot;public&quot; {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  network_acl_id = aws_network_acl.public.id
}

# 프라이빗 서브넷에 프라이빗 NACL 연결
resource &quot;aws_network_acl_association&quot; &quot;private&quot; {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  network_acl_id = aws_network_acl.private.id
}

# 퍼블릭 라우팅 테이블
resource &quot;aws_route_table&quot; &quot;public&quot; {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = &quot;0.0.0.0/0&quot;
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = &quot;my-rtb-pub&quot;
  }
}

# 프라이빗 라우팅 테이블 (기본 설정)
resource &quot;aws_route_table&quot; &quot;private&quot; {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = &quot;my-rtb-pvt&quot;
  }
}

# 퍼블릭 서브넷에 라우팅 테이블 연결
resource &quot;aws_route_table_association&quot; &quot;public&quot; {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# 프라이빗 서브넷에 라우팅 테이블 연결
resource &quot;aws_route_table_association&quot; &quot;private&quot; {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

#출력
output &quot;public_subnet_ids&quot; {
  value = aws_subnet.public[*].id
}

output &quot;private_subnet_ids&quot; {
  value = aws_subnet.private[*].id
}</code></pre><h2 id="eks-설정을-위한-eip-nat-gateway">EKS 설정을 위한 EIP, NAT Gateway</h2>
<pre><code>locals {
  vpc_id           = &quot;vpc-example&quot;
  public_subnet_ids = [&quot;subnet-example&quot;, &quot;subnet-example&quot;]
  private_subnet_ids = [&quot;subnet-example&quot;, &quot;subnet-example&quot;]
}

# 1. Elastic IP for NAT
resource &quot;aws_eip&quot; &quot;nat_eip&quot; {}

# 2. NAT Gateway (퍼블릭 서브넷에 생성해야 함)
resource &quot;aws_nat_gateway&quot; &quot;nat&quot; {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = &quot;subnet-example&quot;  # 퍼블릭 서브넷 중 하나
  tags = {
    Name = &quot;my-nat-gw&quot;
  }
}

# 3. 프라이빗 라우팅 테이블 NAT Gateway 라우팅
resource &quot;aws_route&quot; &quot;private&quot; {
  route_table_id       = &quot;rtb-example&quot;
  destination_cidr_block = &quot;0.0.0.0/0&quot;
  nat_gateway_id       = aws_nat_gateway.nat.id
}</code></pre><h2 id="eks접근을-위한-bastion-ec2">EKS접근을 위한 Bastion EC2</h2>
<pre><code>provider &quot;aws&quot; {
  region = &quot;ap-northeast-2&quot;

  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

##########################
# Bastion 보안 그룹
##########################

resource &quot;aws_security_group&quot; &quot;bastion_sg&quot; {
  name        = &quot;bastion-sg&quot;
  description = &quot;Allow SSH&quot;
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = &quot;tcp&quot;
    cidr_blocks = [&quot;0.0.0.0/0&quot;]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = &quot;-1&quot;
    cidr_blocks = [&quot;0.0.0.0/0&quot;]
  }

  tags = {
    Name = &quot;bastion-sg&quot;
  }
}

resource &quot;aws_iam_role&quot; &quot;bastion_role&quot; {
  name = &quot;bastionRole&quot;

  assume_role_policy = jsonencode({
    Version = &quot;2012-10-17&quot;,
    Statement = [{
      Effect = &quot;Allow&quot;,
      Principal = {
        Service = &quot;ec2.amazonaws.com&quot;
      },
      Action = &quot;sts:AssumeRole&quot;
    }]
  })
}

resource &quot;aws_iam_role_policy_attachment&quot; &quot;bastion_policy&quot; {
  for_each = toset([
    &quot;arn:aws:iam::aws:policy/AmazonEKSClusterPolicy&quot;,
    &quot;arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy&quot;,
    &quot;arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly&quot;,
    &quot;arn:aws:iam::aws:policy/AdministratorAccess&quot;
  ])
  role       = aws_iam_role.bastion_role.name
  policy_arn = each.value
}

resource &quot;aws_iam_instance_profile&quot; &quot;bastion_profile&quot; {
  name = &quot;bastionInstanceProfile&quot;
  role = aws_iam_role.bastion_role.name
}

##########################
# Bastion EC2 인스턴스
##########################

resource &quot;aws_instance&quot; &quot;bastion&quot; {
  ami                   = &quot;ami-0fc8aeaa301af7663&quot;
  instance_type         = &quot;t3.micro&quot;
  subnet_id             = local.public_subnet_ids[0]
  key_name              = &quot;bastion-key&quot;
  vpc_security_group_ids = [aws_security_group.bastion_sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.bastion_profile.name

  user_data = &lt;&lt;-EOF
              #!/bin/bash
              yum update -y
              yum install -y unzip curl wget
              # AWS CLI v2 설치
              curl &quot;https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip&quot; -o &quot;awscliv2.zip&quot;
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
                | grep &quot;browser_download_url.*Linux_amd64.tar.gz&quot; \
                | cut -d '&quot;' -f 4 \
                | head -n 1)
              wget &quot;$K9S_URL&quot; -O k9s_Linux_amd64.tar.gz
              tar -xvf k9s_Linux_amd64.tar.gz
              mv k9s /usr/local/bin/
              rm -f k9s_Linux_amd64.tar.gz
              # AWS CLI 기본 설정
              mkdir -p /home/ec2-user/.aws
              cat &gt; /home/ec2-user/.aws/credentials &lt;&lt;EOL
              [default]
              aws_access_key_id = ${var.aws_access_key_id}
              aws_secret_access_key = ${var.aws_secret_access_key}
              EOL
              cat &gt; /home/ec2-user/.aws/config &lt;&lt;EOL
              [default]
              region = ap-northeast-2
              output = json
              EOL
              chown -R ec2-user:ec2-user /home/ec2-user/.aws
              EOF

  tags = {
    Name = &quot;bastion&quot;
  }
}</code></pre><h2 id="rds">RDS</h2>
<pre><code>##########################
# RDS 보안 그룹 (MariaDB용)
##########################

resource &quot;aws_security_group&quot; &quot;rds_sg&quot; {
  name   = &quot;rds-sg&quot;
  vpc_id = local.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = &quot;tcp&quot;
    security_groups = [aws_security_group.bastion_sg.id]  
    description     = Bastion에서 접근 허용
  }

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = &quot;tcp&quot;
    security_groups = [aws_eks_cluster.main.vpc_config[0].cluster_security_group_id]
    description     = EKS 클러스터 접근 허용
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = &quot;-1&quot;
    cidr_blocks = [&quot;0.0.0.0/0&quot;]
  }

  tags = {
    Name = &quot;rds-sg&quot;
  }
}

##########################
# RDS 서브넷 그룹
##########################

resource &quot;aws_db_subnet_group&quot; &quot;mariadb_subnet_group&quot; {
  name       = &quot;mariadb-subnet-group&quot;
  subnet_ids = local.private_subnet_ids

  tags = {
    Name = &quot;mariadb-subnet-group&quot;
  }
}

##########################
# RDS 인스턴스 (MariaDB)
##########################

resource &quot;aws_db_instance&quot; &quot;mariadb&quot; {
  identifier              = &quot;mariadb-instance&quot;
  allocated_storage       = 20
  engine                  = &quot;mariadb&quot;
  engine_version          = &quot;10.6&quot;
  instance_class          = &quot;db.t3.small&quot;
  db_name                 = &quot;mydb&quot;
  username                = &quot;admin&quot;
  password                = &quot;MySecurePass123!&quot;  # 테스트용. 운영 시 Secrets Manager 사용 권장
  skip_final_snapshot     = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  db_subnet_group_name    = aws_db_subnet_group.mariadb_subnet_group.name

  tags = {
    Name = &quot;mariadb&quot;
  }
}</code></pre><h2 id="eks-cluster-nodegroup-생성">EKS cluster, NodeGroup 생성</h2>
<pre><code>##########################
# EKS 클러스터 IAM Role
##########################

resource &quot;aws_iam_role&quot; &quot;eks_role&quot; {
  name = &quot;eksClusterRole&quot;

  assume_role_policy = jsonencode({
    Version = &quot;2012-10-17&quot;,
    Statement = [{
      Action = &quot;sts:AssumeRole&quot;,
      Effect = &quot;Allow&quot;,
      Principal = {
        Service = &quot;eks.amazonaws.com&quot;
      }
    }]
  })
}

resource &quot;aws_iam_role_policy_attachment&quot; &quot;eks_attach&quot; {
  role       = aws_iam_role.eks_role.name
  policy_arn = &quot;arn:aws:iam::aws:policy/AmazonEKSClusterPolicy&quot;
}

##########################
# EKS 클러스터
##########################

resource &quot;aws_eks_cluster&quot; &quot;main&quot; {
  name     = &quot;my-eks-cluster&quot;
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids = local.private_subnet_ids
  }

  depends_on = [aws_iam_role_policy_attachment.eks_attach]
}

##########################
# EKS 노드 그룹 IAM Role &amp; Instance Profile
##########################

resource &quot;aws_iam_role&quot; &quot;eks_node_role&quot; {
  name = &quot;eksNodeGroupRole&quot;

  assume_role_policy = jsonencode({
    Version = &quot;2012-10-17&quot;,
    Statement = [{
      Effect = &quot;Allow&quot;,
      Principal = {
        Service = &quot;ec2.amazonaws.com&quot;
      },
      Action = &quot;sts:AssumeRole&quot;
    }]
  })
}

resource &quot;aws_iam_role_policy_attachment&quot; &quot;eks_node_policy&quot; {
  for_each = toset([
    &quot;arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy&quot;,
    &quot;arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly&quot;,
    &quot;arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy&quot;
  ])

  role       = aws_iam_role.eks_node_role.name
  policy_arn = each.value
}

# Karpenter에서 참조할 EKS 노드 인스턴스 프로파일을 명시적으로 생성
resource &quot;aws_iam_instance_profile&quot; &quot;eks_node_profile&quot; {
  name = &quot;eksNodeGroupProfile&quot;
  role = aws_iam_role.eks_node_role.name
}

##########################
# EKS Managed Node Group
##########################

resource &quot;aws_eks_node_group&quot; &quot;node_group&quot; {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = &quot;my-node-group&quot;
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = local.private_subnet_ids

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 1
  }

  instance_types = [&quot;t3.small&quot;]

  disk_size = 20

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_eks_cluster.main
  ]

  tags = {
    Name = &quot;eks-node-group&quot;
  }
}</code></pre><h1 id="2단계-클러스터에-주요-컴포넌트-설치하기">2단계: 클러스터에 주요 컴포넌트 설치하기</h1>
<h2 id="aws-load-balancer-controller-lbc">AWS Load Balancer Controller (LBC)</h2>
<p><a href="https://github.com/kubernetes-sigs/aws-load-balancer-controller/blob/main/docs/install/iam_policy.json">https://github.com/kubernetes-sigs/aws-load-balancer-controller/blob/main/docs/install/iam_policy.json</a></p>
<pre><code>##########################
# LBC IAM
##########################
data &quot;aws_eks_cluster&quot; &quot;cluster&quot; {
  name = aws_eks_cluster.main.name
}

data &quot;aws_eks_cluster_auth&quot; &quot;cluster&quot; {
  name = aws_eks_cluster.main.name
}

data &quot;tls_certificate&quot; &quot;eks_cluster&quot; {
  url = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
}

resource &quot;aws_iam_openid_connect_provider&quot; &quot;oidc_provider&quot; {
  url           = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
  client_id_list  = [&quot;sts.amazonaws.com&quot;]
  thumbprint_list = [data.tls_certificate.eks_cluster.certificates[0].sha1_fingerprint]
}

resource &quot;aws_iam_policy&quot; &quot;lbc_policy&quot; {
  name        = &quot;AWSLoadBalancerControllerIAMPolicy&quot;
  description = &quot;Policy for AWS Load Balancer Controller&quot;
  policy      = file(&quot;iam_policy_lbc.json&quot;)
}

resource &quot;aws_iam_role&quot; &quot;lbc_sa_role&quot; {
  name = &quot;lbc-sa-role&quot;

  assume_role_policy = jsonencode({
    Version = &quot;2012-10-17&quot;,
    Statement = [{
      Effect    = &quot;Allow&quot;,
      Principal = { Federated = aws_iam_openid_connect_provider.oidc_provider.arn },
      Action    = &quot;sts:AssumeRoleWithWebIdentity&quot;,
      Condition = {
        StringEquals = {
          &quot;${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, &quot;https://&quot;, &quot;&quot;)}:sub&quot; = &quot;system:serviceaccount:kube-system:aws-load-balancer-controller&quot;
        }
      }
    }]
  })
}

resource &quot;aws_iam_role_policy_attachment&quot; &quot;lbc_attach&quot; {
  role       = aws_iam_role.lbc_sa_role.name
  policy_arn = aws_iam_policy.lbc_policy.arn
}

##########################
# LBC 설치
##########################
resource &quot;null_resource&quot; &quot;install_lbc&quot; {
  depends_on = [
    aws_instance.bastion,
    aws_eks_cluster.main,
    aws_eks_node_group.node_group,
    aws_iam_role_policy_attachment.lbc_attach
  ]

  connection {
    type        = &quot;ssh&quot;
    host        = aws_instance.bastion.public_ip
    user        = &quot;ec2-user&quot;
    private_key = file(&quot;C:/.ssh/bastion-key.pem&quot;)
    timeout     = &quot;10m&quot;
  }

  provisioner &quot;remote-exec&quot; {
    inline = [
      &quot;until aws eks --region ap-northeast-2 describe-cluster --name my-eks-cluster --query cluster.status --output text | grep -q 'ACTIVE'; do echo 'Waiting for EKS cluster to become active...'; sleep 30; done&quot;,
      &quot;aws eks update-kubeconfig --region ap-northeast-2 --name my-eks-cluster&quot;,
      &quot;curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash&quot;,
      &quot;helm repo add eks https://aws.github.io/eks-charts&quot;,
      &quot;helm repo update&quot;,

      &quot;kubectl create ns kube-system || true&quot;,

      # 기존 설치 완전히 정리
      &quot;echo 'Cleaning up existing installation...'&quot;,
      &quot;helm uninstall aws-load-balancer-controller -n kube-system || true&quot;,
      &quot;kubectl delete deployment aws-load-balancer-controller -n kube-system || true&quot;,
      &quot;kubectl delete serviceaccount aws-load-balancer-controller -n kube-system || true&quot;,
      &quot;kubectl delete secrets -l name=aws-load-balancer-controller -n kube-system || true&quot;,

      &lt;&lt;-EOT
      cat &lt;&lt;EOF | kubectl apply -f -
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
      &quot;helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=my-eks-cluster --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller --set region=ap-northeast-2 --set vpcId=${local.vpc_id}&quot;
    ]
  }
}</code></pre><h2 id="metrics-server">Metrics Server</h2>
<pre><code>############################################
# Metrics Server Helm 설치
############################################
resource &quot;null_resource&quot; &quot;install_metrics_server&quot; {
  depends_on = [
    null_resource.install_karpenter
  ]

  connection {
    type        = &quot;ssh&quot;
    host        = aws_instance.bastion.public_ip
    user        = &quot;ec2-user&quot;
    private_key = file(&quot;C:/.ssh/bastion-key.pem&quot;)
  }

  provisioner &quot;remote-exec&quot; {
    inline = [
      &quot;helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/&quot;,
      &quot;helm repo update&quot;,
      &quot;helm upgrade --install metrics-server metrics-server/metrics-server --namespace kube-system&quot;,
      &quot;echo 'Metrics Server installation complete.'&quot;
    ]
  }
}</code></pre><h2 id="karpenter">Karpenter</h2>
<p><a href="https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/#create-the-karpentercontroller-iam-role">https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/#create-the-karpentercontroller-iam-role</a></p>
<pre><code>############################################
# Karpenter IAM Role &amp; Policy
############################################
resource &quot;aws_iam_role&quot; &quot;karpenter_controller_role&quot; {
  name = &quot;KarpenterControllerRole&quot;

  assume_role_policy = jsonencode({
    Version = &quot;2012-10-17&quot;,
    Statement = [{
      Effect = &quot;Allow&quot;,
      Principal = {
        Federated = aws_iam_openid_connect_provider.oidc_provider.arn
      },
      Action = &quot;sts:AssumeRoleWithWebIdentity&quot;,
      Condition = {
        StringEquals = {
          &quot;${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, &quot;https://&quot;, &quot;&quot;)}:sub&quot; = &quot;system:serviceaccount:karpenter:karpenter&quot;
        }
      }
    }]
  })
}

data &quot;aws_caller_identity&quot; &quot;current&quot; {}

resource &quot;aws_iam_policy&quot; &quot;karpenter_controller_policy&quot; {
  name   = &quot;KarpenterControllerPolicy&quot;
  policy = templatefile(&quot;karpenter-controller-policy.json&quot;, {
    AWS_PARTITION  = &quot;aws&quot;
    AWS_ACCOUNT_ID = data.aws_caller_identity.current.account_id
    AWS_REGION     = &quot;ap-northeast-2&quot;
    CLUSTER_NAME   = aws_eks_cluster.main.name
  })
}

resource &quot;aws_iam_role_policy_attachment&quot; &quot;karpenter_controller_attach&quot; {
  role       = aws_iam_role.karpenter_controller_role.name
  policy_arn = aws_iam_policy.karpenter_controller_policy.arn
}

############################################
# 서브넷과 보안그룹에 Karpenter 태그 추가
############################################
resource &quot;aws_ec2_tag&quot; &quot;private_subnet_tags&quot; {
  count       = length(local.private_subnet_ids)
  resource_id = local.private_subnet_ids[count.index]
  key         = &quot;karpenter.sh/discovery&quot;
  value       = aws_eks_cluster.main.name
}

# EKS 클러스터의 보안그룹에 태그 추가
resource &quot;aws_ec2_tag&quot; &quot;cluster_security_group_tag&quot; {
  resource_id = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
  key         = &quot;karpenter.sh/discovery&quot;
  value       = aws_eks_cluster.main.name
}

############################################
# Karpenter Helm 설치
############################################
resource &quot;null_resource&quot; &quot;install_karpenter&quot; {
  depends_on = [
    aws_instance.bastion,
    aws_eks_cluster.main,
    aws_eks_node_group.node_group,
    null_resource.install_lbc,
    aws_ec2_tag.private_subnet_tags,
    aws_ec2_tag.cluster_security_group_tag
  ]

  connection {
    type        = &quot;ssh&quot;
    host        = aws_instance.bastion.public_ip
    user        = &quot;ec2-user&quot;
    private_key = file(&quot;C:/.ssh/bastion-key.pem&quot;)
  }

  provisioner &quot;remote-exec&quot; {
    inline = [
      &lt;&lt;EOT
      # LBC deployment가 준비될 때까지 기다립니다.
      kubectl wait --namespace=kube-system deployment/aws-load-balancer-controller --for=condition=Available=True --timeout=5m

      helm repo add karpenter https://charts.karpenter.sh/
      helm repo update
      kubectl create namespace karpenter || true

      # Karpenter v1.6.0 설치
      helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version 1.6.0 \
        --namespace karpenter \
        --create-namespace \
        --set &quot;serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${aws_iam_role.karpenter_controller_role.arn}&quot; \
        --set &quot;settings.clusterName=${aws_eks_cluster.main.name}&quot; \
        --set &quot;settings.clusterEndpoint=${aws_eks_cluster.main.endpoint}&quot; \
        --set &quot;settings.defaultInstanceProfile=${aws_iam_instance_profile.eks_node_profile.name}&quot; \
        --set &quot;tolerations[0].key=karpenter.sh/unschedulable&quot; \
        --set &quot;tolerations[0].operator=Exists&quot; \
        --set &quot;tolerations[0].effect=NoSchedule&quot; \
        --set &quot;replicas=1&quot; \
        --set &quot;topologySpreadConstraints[0].maxSkew=2&quot; \
        --set &quot;topologySpreadConstraints[0].topologyKey=topology.kubernetes.io/zone&quot; \
        --set &quot;topologySpreadConstraints[0].whenUnsatisfiable=ScheduleAnyway&quot; \
        --set &quot;topologySpreadConstraints[0].labelSelector.matchLabels.app\\.kubernetes\\.io/name=karpenter&quot;
      EOT
    ]
  }
}</code></pre><h3 id="1-karpenter-iam-role--policy">1. Karpenter IAM Role &amp; Policy</h3>
<pre><code>resource &quot;aws_iam_role&quot; &quot;karpenter_controller_role&quot; {
  name = &quot;KarpenterControllerRole&quot;

  assume_role_policy = jsonencode({
    Version = &quot;2012-10-17&quot;,
    Statement = [{
      Effect = &quot;Allow&quot;,
      Principal = {
        Federated = aws_iam_openid_connect_provider.oidc_provider.arn
      },
      Action = &quot;sts:AssumeRoleWithWebIdentity&quot;,
      Condition = {
        StringEquals = {
          &quot;${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, &quot;https://&quot;, &quot;&quot;)}:sub&quot; = &quot;system:serviceaccount:karpenter:karpenter&quot;
        }
      }
    }]
  })
}</code></pre><ul>
<li><p>Principal: Federated = aws_iam_openid_connect_provider.oidc_provider.arn</p>
<ul>
<li>EKS 클러스터의 OIDC Identity Provider를 통해 인증</li>
</ul>
</li>
<li><p>Action: sts:AssumeRoleWithWebIdentity</p>
<ul>
<li>Kubernetes 서비스 어카운트가 AWS IAM 역할을 assume할 수 있게 함</li>
</ul>
</li>
<li><p>Condition: StringEquals</p>
<ul>
<li>특정 서비스 어카운트(system:serviceaccount:karpenter:karpenter)만 이 역할을 사용할 수 있도록 제한</li>
</ul>
</li>
</ul>
<h4 id="eks에서-oidc를-왜-사용할까">EKS에서 OIDC를 왜 사용할까?</h4>
<p><strong>OIDC (OpenID Connect)</strong>는 OAuth 2.0 위에 구축된 신원 인증 프로토콜입니다.</p>
<blockquote>
<p>🤔 Kubernetes Pod이 AWS 서비스를 사용하려면?
   → AWS 액세스 키가 필요
   → 하지만 Pod에 키를 하드코딩하는 것은 보안상 위험!
   ✅ Pod → Kubernetes Service Account → AWS IAM Role
   안전하고 자동화된 방식으로 AWS 권한 획득!</p>
</blockquote>
<pre><code>data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer

실제 값 예시
https://oidc.eks.ap-northeast-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E

URL에서 &quot;https://&quot; 제거
replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, &quot;https://&quot;, &quot;&quot;):sub

결과
oidc.eks.ap-northeast-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E:sub

실제 완성된 조건문
{
  &quot;oidc.eks.ap-northeast-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E:sub&quot;: &quot;system:serviceaccount:karpenter:karpenter&quot;
}</code></pre><blockquote>
<p>🔒 이 조건문의 보안 효과:
❌ 다른 네임스페이스의 Service Account → 접근 거부
❌ 다른 이름의 Service Account → 접근 거부<br />❌ 일반 사용자나 다른 인증 방식 → 접근 거부
✅ karpenter 네임스페이스의 karpenter Service Account만 → 접근 허용</p>
</blockquote>
<h4 id="aws-account-id-가져오기">AWS Account ID 가져오기</h4>
<pre><code>data &quot;aws_caller_identity&quot; &quot;current&quot; {}</code></pre><p>현재 AWS 계정의 ID를 동적으로 가져와 정책에서 사용합니다.</p>
<h4 id="karpenter-controller-policy">Karpenter Controller Policy</h4>
<pre><code>resource &quot;aws_iam_policy&quot; &quot;karpenter_controller_policy&quot; {
  name   = &quot;KarpenterControllerPolicy&quot;
  policy = templatefile(&quot;karpenter-controller-policy.json&quot;, {
    AWS_PARTITION  = &quot;aws&quot;
    AWS_ACCOUNT_ID = data.aws_caller_identity.current.account_id
    AWS_REGION     = &quot;ap-northeast-2&quot;
    CLUSTER_NAME   = aws_eks_cluster.main.name
  })
}</code></pre><p><strong>templatefile 함수</strong>:</p>
<ul>
<li>외부 JSON 파일(karpenter-controller-policy.json)을 템플릿으로 사용
변수들을 동적으로 치환하여 정책 생성</li>
</ul>
<p><strong>주요 권한 (일반적으로 포함되는 것들)</strong>:</p>
<ul>
<li>EC2 인스턴스 생성/삭제/수정</li>
<li>Auto Scaling Group 관리</li>
<li>IAM 인스턴스 프로파일 연결</li>
<li>태그 관리</li>
<li>EKS 노드 그룹 관리</li>
</ul>
<h3 id="2-서브넷과-보안그룹에-karpenter-태그-추가">2. 서브넷과 보안그룹에 Karpenter 태그 추가</h3>
<pre><code>resource &quot;aws_ec2_tag&quot; &quot;private_subnet_tags&quot; {
  count       = length(local.private_subnet_ids)
  resource_id = local.private_subnet_ids[count.index]
  key         = &quot;karpenter.sh/discovery&quot;
  value       = aws_eks_cluster.main.name
}</code></pre><p>Karpenter가 노드를 배포할 서브넷을 프라이빗 서브넷으로 식별할 수 있도록 태그 추가
Karpenter는 이 태그를 통해 어느 서브넷에 새 노드를 생성할지 결정</p>
<h3 id="3-karpneter-helm-설치">3. karpneter helm 설치</h3>
<pre><code>Karpenter v1.6.0 설치
helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version 1.6.0 \
--namespace karpenter \
--create-namespace \
--set &quot;serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${aws_iam_role.karpenter_controller_role.arn}&quot; \
--set &quot;settings.clusterName=${aws_eks_cluster.main.name}&quot; \
--set &quot;settings.clusterEndpoint=${aws_eks_cluster.main.endpoint}&quot; \
--set &quot;settings.defaultInstanceProfile=${aws_iam_instance_profile.eks_node_profile.name}&quot; \
--set &quot;tolerations[0].key=karpenter.sh/unschedulable&quot; \ → &quot;교체 예정 노드에서도 실행할 수 있어&quot;
--set &quot;tolerations[0].operator=Exists&quot; \ → &quot;값이 뭐든 상관없어, 유연하게 대응할게&quot;
--set &quot;tolerations[0].effect=NoSchedule&quot; \ → &quot;스케줄링 제한은 괜찮지만 강제 축출은 싫어&quot;
--set &quot;replicas=1&quot; \ → &quot;나 혼자서도 충분해, 리소스 아끼자&quot;
--set &quot;topologySpreadConstraints[0].maxSkew=2&quot; \ → &quot;영역 간 차이가 2개 이하면 괜찮아&quot;
--set &quot;topologySpreadConstraints[0].topologyKey=topology.kubernetes.io/zone&quot; \ → &quot;가용영역별로 분산해줘&quot;
--set &quot;topologySpreadConstraints[0].whenUnsatisfiable=ScheduleAnyway&quot; \ → &quot;완벽하지 않아도 일단 실행하는 게 중요해&quot;
--set &quot;topologySpreadConstraints[0].labelSelector.matchLabels.app\\.kubernetes\\.io/name=karpenter&quot; → &quot;이 정책은 나(Karpenter)에게만 적용해줘&quot;</code></pre><h4 id="tolerations0keykarpentershunschedulable">tolerations[0].key=karpenter.sh/unschedulable</h4>
<pre><code>실제상황예시:

상황: 노드 A가 교체 예정 상태
  ↓
기존 Pod들: &quot;이 노드 위험해, 다른 곳으로 피하자!&quot; 🏃‍♂️
  ↓  
Karpenter: &quot;어? 그럼 내가 누가 새 노드 만들어줘?&quot; 🤔
  ↓
Karpenter가 피해버리면: 새 노드 생성 불가! 😱

왜 필요한가?
일반 앱 Pod: 교체 예정 노드 피함 (데이터 보호)
Karpenter: 교체 예정 노드에서도 실행 (서비스 연속성)
</code></pre><h4 id="tolerations0operatorexists">tolerations[0].operator=Exists</h4>
<pre><code>실제상황예시:

시나리오 1: Taint 값이 &quot;replacing&quot;
노드 상태: karpenter.sh/unschedulable=replacing

시나리오 2: Taint 값이 &quot;draining&quot;  
노드 상태: karpenter.sh/unschedulable=draining

시나리오 3: Taint 값이 &quot;upgrading&quot;
노드 상태: karpenter.sh/unschedulable=upgrading

만약 특정 값만 허용한다면?
이렇게 설정했다면:
tolerations:
- key: karpenter.sh/unschedulable
  value: &quot;replacing&quot;  # 특정 값만!
  operator: Equal

문제 발생:
- &quot;draining&quot; 상태에서는 실행 불가 ❌
- &quot;upgrading&quot; 상태에서도 실행 불가 ❌
→ Karpenter 서비스 중단! 😱

Exists의 장점:
operator: Exists = &quot;키만 있으면 값은 뭐든 OK!&quot;
→ 모든 교체 시나리오에 대응 가능 ✅</code></pre><h4 id="tolerations0effectnoschedule">tolerations[0].effect=NoSchedule</h4>
<pre><code>NoSchedule vs NoExecute 차이:
- NoSchedule: &quot;새로 스케줄링 안 해줄래&quot; (기존 것은 계속 실행)
- NoExecute:  &quot;기존 것도 강제로 쫓아낼래&quot; (즉시 종료)

실제상황예시:
상황: 노드에 NoExecute Taint 적용됨
  ↓
Karpenter Pod: 즉시 강제 종료 😵
  ↓
새로운 스케일링 요청: &quot;Karpenter 어디갔어?&quot; 🤷‍♂️
  ↓  
결과: 클러스터 스케일링 마비! 😱

왜 NoSchedule만?
NoSchedule Toleration:
- 기존 Karpenter Pod: 계속 실행 ✅
- 새 Karpenter Pod: 다른 노드에 스케줄링 ✅
- 서비스 연속성: 보장됨 ✅</code></pre><h4 id="replicas1">replicas=1</h4>
<pre><code>Karpenter의 주요 업무:
1. 클러스터 상태 모니터링 
2. 스케일링 결정  
3. AWS API 호출 
4. 노드 생성/삭제 지시 

왜 한개면 충분할까?
❌ 여러 개가 동시에 같은 일을 하면:
   Pod A: &quot;노드 3개 더 필요해!&quot;
   Pod B: &quot;노드 3개 더 필요해!&quot;  
   결과: 6개 생성 → 자원 낭비 😱

✅ 1개가 모든 걸 관리하면:
   단일 결정자: &quot;노드 3개만 추가하자&quot;
   결과: 정확히 3개 생성 → 효율적!

Karpenter의 고가용성은?
한개로 운영중인 Karpenter Pod 죽으면?
→ Kubernetes Deployment가 자동으로 재시작
→ 잠깐 중단되지만 곧 복구 ✅

vs 여러 개 Karpenter Pod 운영 시:
→ 복잡한 리더 선출 필요
→ 동시성 제어 복잡
→ 리소스 낭비</code></pre><h4 id="maxskew2">maxSkew=2</h4>
<pre><code>실제 가용영역 시나리오:
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
- maxSkew=2: AZ-B나 AZ-C에 여유롭게 배치 ✅</code></pre><h4 id="whenunsatisfiablescheduleanyway">whenUnsatisfiable=ScheduleAnyway</h4>
<pre><code>완벽한 분산이 불가능한 상황들:

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
DoNotSchedule: &quot;완벽하지 않으면 아예 실행 안 해!&quot;
→ Karpenter 서비스 중단 가능 😱

ScheduleAnyway: &quot;불완전해도 일단 실행해서 서비스 유지!&quot;  
→ 고가용성 우선 ✅</code></pre><h4 id="labelselectormatchlabelsappkubernetesionamekarpenter">labelSelector.matchLabels.app\.kubernetes\.io/name=karpenter</h4>
<pre><code>&quot;다른 Pod들이 안정적으로 실행될 수 있도록 노드를 관리하는 것&quot;

따라서: 
1. 다른 Pod들이 피하는 노드에서도 → 나는 실행되어야 함
2. 어떤 상황에서든 → 유연하게 대응해야 함  
3. 강제 종료되면 안 되고 → 서비스 연속성 유지
4. 효율적으로 → 리소스 낭비 금지
5. 가용성을 위해 → 적당한 분산
6. 완벽하지 않아도 → 서비스가 먼저</code></pre><h4 id="결국-이-모든-설정은-karpenter가-어떤-상황에서든-안정적으로-실행되어-클러스터-전체의-안정성과-비용-효율성을-보장하기-위함입니다">결국 이 모든 설정은 &quot;Karpenter가 어떤 상황에서든 안정적으로 실행되어, 클러스터 전체의 안정성과 비용 효율성을 보장하기 위함&quot;입니다!</h4>
<h1 id="3단계-karpenter-nodepool--ec2nodeclass">3단계: Karpenter NodePool &amp; EC2NodeClass</h1>
<pre><code>############################################
# Karpenter v1.6.0 NodePool &amp; EC2NodeClass 생성
############################################
resource &quot;null_resource&quot; &quot;karpenter_nodepool&quot; {
  depends_on = [null_resource.install_karpenter]

  connection {
    type        = &quot;ssh&quot;
    host        = aws_instance.bastion.public_ip
    user        = &quot;ec2-user&quot;
    private_key = file(&quot;C:/.ssh/bastion-key.pem&quot;)
  }

  provisioner &quot;remote-exec&quot; {
    inline = [
      &lt;&lt;-EOT
      echo &quot;Waiting for Karpenter controller to become available...&quot;
      kubectl wait --namespace=karpenter deployment/karpenter --for=condition=Available=True --timeout=10m

      echo &quot;Waiting for Karpenter CRDs to be established...&quot;
      # CRD가 등록될 때까지 대기
      kubectl wait --for condition=established --timeout=300s crd/nodepools.karpenter.sh
      kubectl wait --for condition=established --timeout=300s crd/ec2nodeclasses.karpenter.k8s.aws

      # CRD 상태 확인
      echo &quot;Checking CRD status...&quot;
      kubectl get crd | grep karpenter

      # API 버전 확인
      echo &quot;Checking available API versions...&quot;
      kubectl api-resources | grep -E &quot;(nodepool|ec2nodeclass)&quot;

      # 추가 대기 시간
      sleep 30

      # EC2NodeClass 생성 (v1 API)
      echo &quot;Creating EC2NodeClass...&quot;
      cat &lt;&lt;EOF | kubectl apply -f -
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
              karpenter.sh/discovery: &quot;${aws_eks_cluster.main.name}&quot;

        # 보안 그룹 선택
        securityGroupSelectorTerms:
          - tags:
              karpenter.sh/discovery: &quot;${aws_eks_cluster.main.name}&quot;

        # IAM 인스턴스 프로파일
        instanceProfile: &quot;${aws_iam_instance_profile.eks_node_profile.name}&quot;

        # 사용자 데이터 스크립트
        userData: |
          #!/bin/bash
          /etc/eks/bootstrap.sh ${aws_eks_cluster.main.name}

          # 추가 설정
          echo &quot;net.ipv4.ip_forward = 1&quot; &gt;&gt; /etc/sysctl.conf
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
        echo &quot;EC2NodeClass created successfully&quot;
      else
        echo &quot;Failed to create EC2NodeClass&quot;
        exit 1
      fi

      # 잠시 대기
      sleep 10

      # NodePool 생성 (v1 API)
      echo &quot;Creating NodePool...&quot;
      cat &lt;&lt;EOF | kubectl apply -f -
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
                values: [&quot;amd64&quot;]
              - key: karpenter.sh/capacity-type
                operator: In
                values: [&quot;on-demand&quot;]
              - key: node.kubernetes.io/instance-type
                operator: In
                values: [&quot;t3.small&quot;]

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
        echo &quot;NodePool created successfully&quot;
      else
        echo &quot;Failed to create NodePool&quot;
        exit 1
      fi

      echo &quot;Waiting for resources to be created...&quot;
      sleep 15

      echo &quot;Karpenter v1.6.0 NodePool and EC2NodeClass created successfully&quot;

      # 생성된 리소스 확인
      echo &quot;Checking created resources...&quot;
      kubectl get nodepools -o wide
      kubectl get ec2nodeclasses -o wide

      EOT
    ]
  }
}</code></pre><h2 id="crd-custom-resource-definition">CRD (Custom Resource Definition)</h2>
<h3 id="crd란">CRD란?</h3>
<ul>
<li>&quot;새로운 언어 사전 만들기&quot; Kubernetes를 언어라고 생각하면 됩니다.</li>
</ul>
<p><strong>기본 Kubernetes 단어들 (내장 리소스):</strong></p>
<ul>
<li>Pod: &quot;컨테이너 실행&quot;</li>
<li>Service: &quot;네트워크 연결&quot;</li>
<li>Deployment: &quot;애플리케이션 배포&quot;</li>
<li>Node: &quot;서버&quot;</li>
</ul>
<p><strong>CRD = &quot;새로운 단어 정의서&quot;:</strong></p>
<ul>
<li>NodePool: &quot;노드 그룹 정책&quot; (Karpenter가 만든 새 단어)</li>
<li>EC2NodeClass: &quot;AWS 노드 설정&quot; (Karpenter가 만든 새 단어)</li>
</ul>
<h3 id="karpenter에서-crd가-중요한-이유">Karpenter에서 CRD가 중요한 이유</h3>
<h4 id="1-karpenter-controller-작동-방식">1. Karpenter Controller 작동 방식</h4>
<pre><code>Karpenter Controller 시작
        ↓
&quot;NodePool 리소스 변화 감지하겠어!&quot;
        ↓
CRD 있나 확인
        ↓
❌ CRD 없음: &quot;NodePool이 뭔지 몰라서 감지할 수 없어!&quot; → 중단
✅ CRD 있음: &quot;NodePool 변화를 감지하고 반응하겠어!&quot; → 정상 작동</code></pre><h4 id="2-실제-노드-생성-프로세스">2. 실제 노드 생성 프로세스</h4>
<pre><code>사용자가 NodePool 생성/수정
        ↓
Kubernetes API Server: &quot;NodePool 리소스가 변경되었네&quot;
        ↓
Karpenter Controller: &quot;변경 감지! 새로운 노드가 필요한가?&quot;
        ↓
EC2NodeClass 참조: &quot;어떤 스펙의 서버를 만들지 확인&quot;
        ↓
AWS EC2 API 호출: &quot;실제 인스턴스 생성&quot;</code></pre><h4 id="3-crd가-없다면">3. CRD가 없다면?</h4>
<pre><code>❌ &quot;NodePool이 뭔지 몰라요&quot;
❌ Controller 아예 시작 안됨
❌ 노드 생성 불가능</code></pre><h3 id="crd의-실행을-기다림">CRD의 실행을 기다림</h3>
<pre><code>echo &quot;Waiting for Karpenter CRDs to be established...&quot;
kubectl wait --for condition=established --timeout=300s crd/nodepools.karpenter.sh
kubectl wait --for condition=established --timeout=300s crd/ec2nodeclasses.karpenter.k8s.aws</code></pre><p><strong>왜 기다려야할까?</strong></p>
<ol>
<li>Karpenter Helm 설치 → CRD 생성 시작</li>
<li>CRD 완전 등록까지 시간 소요 (보통 30초~2분)</li>
<li>CRD 준비 완료 → NodePool/EC2NodeClass 생성 가능<h2 id="ec2nodeclass">EC2NodeClass</h2>
<h3 id="ec2nodeclass--어떻게-만들까-how">EC2NodeClass = &quot;어떻게 만들까?&quot; (HOW)</h3>
<pre><code># EC2NodeClass는 EC2 인스턴스 생성 방법을 정의
spec:
amiSelectorTerms: [...] # 어떤 AMI 사용할지
userData: |             # 부팅 시 실행할 스크립트
 /etc/eks/bootstrap.sh
blockDeviceMappings:    # 디스크 구성
 volumeSize: 20Gi
metadataOptions:        # 보안 설정
 httpTokens: required</code></pre><h3 id="ec2nodeclass가-담당하는-것들">EC2NodeClass가 담당하는 것들</h3>
```
AWS EC2 관련 모든 설정:</li>
</ol>
<ul>
<li>AMI 선택 (운영체제)</li>
<li>보안그룹 (네트워크 방화벽)</li>
<li>서브넷 (네트워크 위치)</li>
<li>IAM 인스턴스 프로파일 (권한)</li>
<li>User Data (부팅 스크립트)</li>
<li>EBS 볼륨 (스토리지)</li>
<li>EC2 메타데이터 설정</li>
</ul>
<p>→ &quot;물리적 서버를 어떻게 구성할 것인가&quot;</p>
<pre><code>## NodePool
### NodePool = &quot;언제, 얼마나 만들까?&quot; (WHEN &amp; HOW MANY)</code></pre><h1 id="nodepool은-스케일링-조건과-제약을-정의">NodePool은 스케일링 조건과 제약을 정의</h1>
<p>spec:
  requirements:           # 어떤 조건의 노드가 필요한지
    - key: node.kubernetes.io/instance-type
      values: [&quot;t3.small&quot;]
  limits:                 # 최대 얼마나 생성할지
    cpu: 20
  disruption:             # 언제 삭제할지
    consolidateAfter: 5m</p>
<pre><code>### NodePool이 담당하는 것들</code></pre><p>Kubernetes 스케일링 관련 모든 정책:</p>
<ul>
<li>노드 요구사항 (인스턴스 타입, 아키텍처 등)</li>
<li>리소스 제한 (최대 CPU/메모리)</li>
<li>스케일링 정책 (언제 생성/삭제)</li>
<li>노드 라벨링</li>
<li>Taints/Tolerations</li>
</ul>
<p>→ &quot;언제 얼마나 만들고 관리할 것인가&quot;</p>
<pre><code>
## 1:N 관계 이해
### 하나의 EC2NodeClass, 여러 NodePool 가능</code></pre><p>하나의 EC2NodeClass:</p>
<ul>
<li>표준 AMI 설정</li>
<li>표준 보안 설정  </li>
<li>표준 네트워크 설정</li>
</ul>
<p>여러 NodePool:</p>
<ul>
<li>개발용 (작은 인스턴스)</li>
<li>운영용 (큰 인스턴스)  </li>
<li>GPU용 (GPU 인스턴스)</li>
<li>Spot용 (비용 절약)</li>
</ul>
<p>→ 공통 인프라 설정은 재사용하면서 
  용도별 스케일링 정책은 분리</p>
<p>```</p>
<h2 id="ec2nodeclass-vs-nodepool">EC2NodeClass VS NodePool</h2>
<table>
<thead>
<tr>
<th align="left">구분</th>
<th align="left">EC2NodeClass</th>
<th align="left">NodePool</th>
</tr>
</thead>
<tbody><tr>
<td align="left"><strong>역할</strong></td>
<td align="left">AWS 인프라 템플릿</td>
<td align="left">Kubernetes 스케일링 정책</td>
</tr>
<tr>
<td align="left"><strong>관심사</strong></td>
<td align="left">HOW (어떻게 만들까)</td>
<td align="left">WHEN/HOW MANY (언제/얼마나)</td>
</tr>
<tr>
<td align="left"><strong>설정 내용</strong></td>
<td align="left">AMI, 보안그룹, 서브넷, 스토리지</td>
<td align="left">인스턴스 타입, 리소스 제한, 스케일링</td>
</tr>
<tr>
<td align="left"><strong>변경 빈도</strong></td>
<td align="left">낮음 (인프라 표준)</td>
<td align="left">높음 (워크로드별 요구사항)</td>
</tr>
<tr>
<td align="left"><strong>재사용성</strong></td>
<td align="left">높음 (여러 NodePool이 참조)</td>
<td align="left">낮음 (특정 용도)</td>
</tr>
</tbody></table>