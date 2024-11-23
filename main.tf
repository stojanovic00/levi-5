# Data source to get availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source to get AWS Account ID
data "aws_caller_identity" "current" {}

# VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "MainVPC"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main_vpc.id

  tags = {
    Name = "MainInternetGateway"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "PublicRouteTable"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnets" {
  count                   = 2
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = cidrsubnet("10.0.0.0/16", 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "PublicSubnet-${count.index}"
  }
}


# Private Subnets
resource "aws_subnet" "private_subnets" {
  count             = 2
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet("10.0.0.0/16", 8, count.index + 2)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "PrivateSubnet-${count.index}"
  }
}


# Associate subnets with route table
resource "aws_route_table_association" "public_subnet_assoc" {
  count          = length(aws_subnet.public_subnets)
  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

# Security Group for EC2
resource "aws_security_group" "ec2_sg" {
  name        = "EC2SecurityGroup"
  description = "Allow SSH and HTTP"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # For simplicity; restrict in production
  }

  ingress {
    description = "HTTP access"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "EC2SecurityGroup"
  }
}

# Security Group for DocumentDB
resource "aws_security_group" "docdb_sg" {
  name        = "DocDBSecurityGroup"
  description = "Allow EC2 access to DocumentDB"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    description     = "Allow EC2 instances to access DocumentDB"
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "DocDBSecurityGroup"
  }
}

# Generate a key pair for EC2
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "generated-key"
  public_key = tls_private_key.example.public_key_openssh
}


data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical's AWS account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 Instance
resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public_subnets[0].id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = aws_key_pair.generated_key.key_name
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y httpd
              sudo systemctl start httpd
              sudo systemctl enable httpd
              echo "Welcome to the App Server" > /var/www/html/index.html
              EOF

  tags = {
    Name = "AppServer"
  }
}

# Create an IAM instance profile
resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "EC2InstanceProfile"
  role = aws_iam_role.ec2_role.name
}

# DocumentDB Subnet Group
resource "aws_docdb_subnet_group" "docdb_subnet_group" {
  name       = "docdb-subnet-group"
  subnet_ids = aws_subnet.private_subnets[*].id

  tags = {
    Name = "DocDBSubnetGroup"
  }
}

# DocumentDB Cluster
resource "aws_docdb_cluster" "docdb_cluster" {
  cluster_identifier      = "docdb-cluster"
  master_username         = var.docdb_username
  master_password         = var.docdb_password
  vpc_security_group_ids  = [aws_security_group.docdb_sg.id]
  db_subnet_group_name    = aws_docdb_subnet_group.docdb_subnet_group.name
  backup_retention_period = 1

  tags = {
    Name = "DocDBCluster"
  }
}

# DocumentDB Cluster Instance
resource "aws_docdb_cluster_instance" "docdb_instance" {
  identifier         = "docdb-instance"
  cluster_identifier = aws_docdb_cluster.docdb_cluster.id
  instance_class     = "db.r5.large"
  engine             = "docdb"

  tags = {
    Name = "DocDBInstance"
  }
}

# API Gateway

## REST API
resource "aws_api_gateway_rest_api" "api_gateway" {
  name = "MyAPIGateway"
}

## API Resource
resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "path"
}

## Method
resource "aws_api_gateway_method" "api_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

## Integration
resource "aws_api_gateway_integration" "api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.api_resource.id
  http_method             = aws_api_gateway_method.api_method.http_method
  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  uri                     = "http://${aws_instance.app_server.public_ip}"
}

## Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  triggers = {
    redeployment = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.api_integration
  ]
}

## Stage
resource "aws_api_gateway_stage" "api_stage" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  deployment_id = aws_api_gateway_deployment.api_deployment.id
}

# SNS Topic
resource "aws_sns_topic" "email_notifications" {
  name = "EmailNotificationsTopic"

  tags = {
    Name = "EmailNotificationsTopic"
  }
}

# SNS Topic Subscription
resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.email_notifications.arn
  protocol  = "email"
  endpoint  = var.notification_email  # Define this variable in variables.tf
}


# IAM Role for Lambda
resource "aws_iam_role" "lambda_match_notifier_role" {
  name = "lambda_match_notifier_role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_policy" "lambda_match_notifier_policy" {
  name        = "lambda_match_notifier_policy"
  description = "Policy for Lambda to publish to SNS"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "sns:Publish"
        ],
        "Effect": "Allow",
        "Resource": aws_sns_topic.email_notifications.arn
      },
      {
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Effect": "Allow",
        "Resource": "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_match_notifier_attachment" {
  role       = aws_iam_role.lambda_match_notifier_role.name
  policy_arn = aws_iam_policy.lambda_match_notifier_policy.arn
}

# Lambda Function
resource "aws_lambda_function" "match_notifier" {
  function_name    = "MatchNotifierFunction"
  filename         = "lambda_functions/match_notifier/match_notifier.zip"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  role             = aws_iam_role.lambda_match_notifier_role.arn
  source_code_hash = filebase64sha256("lambda_functions/match_notifier/match_notifier.zip")

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.email_notifications.arn
    }
  }
}

# API Gateway for Lambda Invocation
resource "aws_api_gateway_rest_api" "lambda_api" {
  name = "LambdaAPI"
}

# Resource
resource "aws_api_gateway_resource" "lambda_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "notify"
}

# Method
resource "aws_api_gateway_method" "lambda_method" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.lambda_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.lambda_resource.id
  http_method             = aws_api_gateway_method.lambda_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.match_notifier.invoke_arn
}

# Lambda Permission
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.match_notifier.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}

# Deployment
resource "aws_api_gateway_deployment" "lambda_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  depends_on  = [aws_api_gateway_integration.lambda_integration]

  lifecycle {
    create_before_destroy = true
  }
}

# Stage
resource "aws_api_gateway_stage" "lambda_api_stage" {
  deployment_id = aws_api_gateway_deployment.lambda_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  stage_name    = "prod"
}

# IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "EC2LambdaInvokeRole"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy for EC2 to Invoke Lambda
resource "aws_iam_policy" "ec2_lambda_invoke_policy" {
  name        = "EC2LambdaInvokePolicy"
  description = "Policy for EC2 to invoke Lambda functions"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "lambda:InvokeFunction",
        "Resource": [
          aws_lambda_function.match_notifier.arn,
          aws_lambda_function.match_saver.arn
        ]
      }
    ]
  })
}

# Attach the policy to the EC2 role
resource "aws_iam_role_policy_attachment" "ec2_lambda_invoke_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_lambda_invoke_policy.arn
}

# IAM Policy Document
resource "aws_lambda_permission" "allow_account_invoke" {
  statement_id  = "AllowExecutionFromAccount"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.match_notifier.function_name
  principal     = var.aws_account_id
}

data "aws_iam_policy_document" "lambda_permission_policy" {
  statement {
    sid    = "AllowExecutionFromEC2"
    effect = "Allow"

    actions = ["lambda:InvokeFunction"]

    resources = [aws_lambda_function.match_notifier.arn]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.ec2_role.arn]
    }
  }
}


resource "aws_s3_bucket" "match_results_bucket" {
  bucket = "match-results-bucket-${random_string.bucket_suffix.result}"

  tags = {
    Name = "MatchResultsBucket"
  }
}

# Random string for unique bucket name
resource "random_string" "bucket_suffix" {
  length  = 6
  special = false
  upper   = false
}



# IAM Role for Lambda_2
resource "aws_iam_role" "lambda_match_saver_role" {
  name = "lambda_match_saver_role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_match_saver_policy" {
  name        = "lambda_match_saver_policy"
  description = "Policy for Lambda to write to S3"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutObject"
        ],
        "Resource": "${aws_s3_bucket.match_results_bucket.arn}/*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_match_saver_attachment" {
  role       = aws_iam_role.lambda_match_saver_role.name
  policy_arn = aws_iam_policy.lambda_match_saver_policy.arn
}

# Lambda Function for Saving Match Results
resource "aws_lambda_function" "match_saver" {
  function_name    = "MatchSaverFunction"
  filename         = "lambda_functions/match_saver/match_saver.zip"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  role             = aws_iam_role.lambda_match_saver_role.arn
  source_code_hash = filebase64sha256("lambda_functions/match_saver/match_saver.zip")

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.match_results_bucket.bucket
    }
  }
}

# Lambda Permission to Allow Invocation from EC2
resource "aws_lambda_permission" "allow_ec2_invoke_match_saver" {
  statement_id  = "AllowExecutionFromEC2MatchSaver"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.match_saver.function_name
  principal     = data.aws_caller_identity.current.account_id
}


# IAM Policy for EC2 to Access DynamoDB
resource "aws_iam_policy" "ec2_dynamodb_access" {
  name        = "EC2DynamoDBAccessPolicy"
  description = "Allow EC2 to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:DeleteItem",
          "dynamodb:BatchWriteItem"
        ],
        Resource = "arn:aws:dynamodb:eu-central-1:${data.aws_caller_identity.current.account_id}:table/*"
      }
    ]
  })
}
