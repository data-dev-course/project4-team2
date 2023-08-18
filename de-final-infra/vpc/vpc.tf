# VPC
# Whole network cidr will be 10.0.0.0/8 
# A VPC cidr will use the B class with 10.xxx.0.0/16
# You should set cidr advertently because if the number of VPC get larger then the ip range could be in shortage.
resource "aws_vpc" "main" {
  cidr_block = "10.${var.cidr_numeral}.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "de-3-2-vpc"
  }
}

# internet gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "de-3-2-vpc-igw"
  }

}

# NAT Gateway 
resource "aws_nat_gateway" "nat_0" {
  # Count means how many you want to create the same resource
  # This will be generated with array format
  # For example, if the number of availability zone is three, then nat[0], nat[1], nat[2] will be created.
  # If you want to create each resource with independent name, then you have to copy the same code and modify some code
  count = 1

  # element is used for select the resource from the array 
  # Usage = element (array, index) => equals array[index]
  allocation_id = aws_eip.nat_0[count.index].id
  
  #Subnet Setting
  # nat[0] will be attached to subnet[0]. Same to all index.
  subnet_id = element(aws_subnet.public.*.id, count.index)

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "de-3-2-vpc-NAT-GW0"
  }

}

# NAT Gateway 
resource "aws_nat_gateway" "nat_1" {
  # Count means how many you want to create the same resource
  # This will be generated with array format
  # For example, if the number of availability zone is three, then nat[0], nat[1], nat[2] will be created.
  # If you want to create each resource with independent name, then you have to copy the same code and modify some code
  count = 1

  # element is used for select the resource from the array 
  # Usage = element (array, index) => equals array[index]
  allocation_id = aws_eip.nat_1[count.index].id
  
  #Subnet Setting
  # nat[0] will be attached to subnet[0]. Same to all index.
  subnet_id = element(aws_subnet.public.*.id, count.index)

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "de-3-2-vpc-NAT-GW1"
  }

}

# Elastic IP for NAT Gateway 
resource "aws_eip" "nat_0" {
  # Count value should be same with that of aws_nat_gateway because all nat will get elastic ip
  count = 1
  domain = "vpc"

  lifecycle {
    create_before_destroy = true
  }
}

# Elastic IP for NAT Gateway 
resource "aws_eip" "nat_1" {
  # Count value should be same with that of aws_nat_gateway because all nat will get elastic ip
  count = 1
  domain = "vpc"

  lifecycle {
    create_before_destroy = true
  }
}

#### Public Subnets
# Subnet will use cidr with /20 -> The number of available IP is 4,096
resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
  count  = length(var.availability_zones)

  cidr_block = "10.${var.cidr_numeral}.${var.cidr_numeral_public[count.index]}.0/20"
  availability_zone = "ap-northeast-2a"

  # Public IP will be assigned automatically when the instance is launch in the public subnet
  map_public_ip_on_launch = true
  tags = {
    Name = "de-3-2-vpc-public-${count.index}"
  }
}

# Route Table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "de-3-2-vpc-rt-public"
  }
}

# Route Table Association for public subnets
resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = element(aws_subnet.public.*.id, count.index)
  route_table_id = aws_route_table.public.id
}

#### PRIVATE SUBNETS
# Subnet will use cidr with /20 -> The number of available IP is 4,096
resource "aws_subnet" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  cidr_block        = "10.${var.cidr_numeral}.${var.cidr_numeral_private[count.index]}.0/20"
  availability_zone = element(var.availability_zones, count.index)
  tags = {
    Name = "de-3-2-vpc-private-${count.index}"
    immutable_metadata = "{ \"purpose\": \"internal_${var.vpc_name}\", \"target\": null }"
    Network = "Private"
  }
}

# Route Table for private subnets
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  count  = length(var.availability_zones)
  tags = {
    Name = "de-3-2-vpc-rt-private-${count.index}"
    Network = "Private"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = element(aws_route_table.private.*.id, count.index)
}

# DB PRIVATE SUBNETS
# This subnet is only for the database. 
# For security, it is better to assign ip range for database only.
# This is also going to use /20 cidr, which might be too many IPs... Please count it carefully and change the cidr.
resource "aws_subnet" "private_db" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  cidr_block        = "10.${var.cidr_numeral}.${var.cidr_numeral_private_db[count.index]}.0/20"
  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name               = "de-3-2-vpc-db-private-${count.index}"
    immutable_metadata = "{ \"purpose\": \"internal_db_${var.vpc_name}\", \"target\": null }"
    Network            = "Private"
  }
}

# Route Table for DB subnets
resource "aws_route_table" "private_db" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "de-3-2-vpc-rt-privatedb-${count.index}"
    Network = "Private"
  }
}

# Route Table Association for DB subnets
resource "aws_route_table_association" "private_db" {
  count          = length(var.availability_zones)
  subnet_id      = element(aws_subnet.private_db.*.id, count.index)
  route_table_id = element(aws_route_table.private_db.*.id, count.index)
}

# MWAA PRIVATE SUBNETS
resource "aws_subnet" "private_mwaa" {
  count  = length(var.availability_zones)-1
  vpc_id = aws_vpc.main.id

  cidr_block        = "10.${var.cidr_numeral}.${var.cidr_numeral_private_mwaa[count.index]}.0/20"
  availability_zone = element(var.availability_zones, count.index)
  tags = {
    Name = "de-3-2-vpc-mwaa-private-${count.index}"
    immutable_metadata = "{ \"purpose\": \"internal_${var.vpc_name}\", \"target\": null }"
    Network = "Private"
  }
}

# Route Table for mwaa private subnets
resource "aws_route_table" "private_mwaa" {
  vpc_id = aws_vpc.main.id
  count  = length(var.availability_zones)-1
  tags = {
    Name = "de-3-2-vpc-rt-private-maww-${count.index}"
    Network = "Private"
  }
}

resource "aws_route_table_association" "private_mwaa" {
  count          = length(var.availability_zones)-1
  subnet_id      = element(aws_subnet.private_mwaa.*.id, count.index)
  route_table_id = element(aws_route_table.private_mwaa.*.id, count.index)
}