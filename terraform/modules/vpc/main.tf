# ==============================================================================
# JISR Arabic - Multi-AZ VPC Architecture (3 Availability Zones)
# ==============================================================================

data "aws_availability_zones" "available" {
  count = length(var.availability_zones) == 0 ? 1 : 0
  state = "available"
}

locals {
  azs = length(var.availability_zones) > 0 ? var.availability_zones : data.aws_availability_zones.available[0].names
}

# --- VPC Core ---
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc"
    Environment = var.environment
  }
}

# --- Internet Gateway for Public Subnets ---
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project_name}-${var.environment}-igw"
    Environment = var.environment
  }
}

# --- Public Subnets (ALB & NAT Gateways) ---
resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1) # 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-public-${local.azs[count.index]}"
    Environment = var.environment
    Tier        = "Public"
  }
}

# --- Private Compute Subnets (FastAPI & Background Workers) ---
resource "aws_subnet" "private_compute" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10) # 10.0.10.0/24, 10.0.11.0/24, 10.0.12.0/24
  availability_zone = local.azs[count.index]

  tags = {
    Name        = "${var.project_name}-${var.environment}-compute-${local.azs[count.index]}"
    Environment = var.environment
    Tier        = "Private-Compute"
  }
}

# --- Isolated Database Subnets (Aurora PostgreSQL & ElastiCache Redis) ---
resource "aws_subnet" "isolated_database" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100) # 10.0.100.0/24, 10.0.101.0/24, 10.0.102.0/24
  availability_zone = local.azs[count.index]

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-${local.azs[count.index]}"
    Environment = var.environment
    Tier        = "Isolated-Database"
  }
}

# --- Elastic IPs & NAT Gateways (Multi-AZ for Outbound Internet from Compute) ---
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"

  tags = {
    Name        = "${var.project_name}-${var.environment}-nat-eip-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "nat" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name        = "${var.project_name}-${var.environment}-nat-${count.index + 1}"
    Environment = var.environment
  }

  depends_on = [aws_internet_gateway.gw]
}

# --- Routing Tables ---

# 1. Public Route Table -> Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  count          = 3
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# 2. Private Compute Route Tables -> NAT Gateway
resource "aws_route_table" "private_compute" {
  count  = 3
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index % 2].id
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-compute-rt-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "private_compute" {
  count          = 3
  subnet_id      = aws_subnet.private_compute[count.index].id
  route_table_id = aws_route_table.private_compute[count.index].id
}

# 3. Isolated Database Route Table (No Internet Access)
resource "aws_route_table" "isolated_database" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "isolated_database" {
  count          = 3
  subnet_id      = aws_subnet.isolated_database[count.index].id
  route_table_id = aws_route_table.isolated_database.id
}

# --- Core Security Groups (Acyclic Hierarchy) ---

# 1. ALB Security Group (Public Edge)
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Allows inbound HTTP/HTTPS traffic to Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP Public Access"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Public Access"
    from_port   = 443
    to_port     = 443
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
    Name        = "${var.project_name}-${var.environment}-alb-sg"
    Environment = var.environment
  }
}

# 2. Compute Security Group (Private ECS Tasks)
resource "aws_security_group" "compute" {
  name        = "${var.project_name}-${var.environment}-compute-sg"
  description = "Allows inbound traffic to FastAPI strictly from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB strictly"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-compute-sg"
    Environment = var.environment
  }
}

