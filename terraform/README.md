# Terraform Infrastructure

This directory contains Terraform configurations for deploying the FastAPI SaaS application to AWS.

## Architecture

The infrastructure includes:
- **VPC**: Multi-AZ VPC with public, private, and data subnets
- **RDS**: PostgreSQL database with multi-AZ, automated backups, and encryption
- **ElastiCache**: Redis cluster with replication and encryption
- **ECS**: Fargate-based container orchestration
- **ALB**: Application Load Balancer with HTTPS support
- **IAM**: Least-privilege roles for ECS tasks

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials
4. **S3 Bucket** for Terraform state storage
5. **DynamoDB Table** for state locking

## Setup

### 1. Create S3 Backend

```bash
# Create S3 bucket for state
aws s3 mb s3://your-terraform-state-bucket --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket your-terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-terraform-state-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Create Backend Config Files

Create `backend-dev.hcl`:
```hcl
bucket         = "your-terraform-state-bucket"
key            = "dev/terraform.tfstate"
region         = "us-east-1"
encrypt        = true
dynamodb_table = "terraform-state-lock"
```

Create `backend-prod.hcl`:
```hcl
bucket         = "your-terraform-state-bucket"
key            = "prod/terraform.tfstate"
region         = "us-east-1"
encrypt        = true
dynamodb_table = "terraform-state-lock"
```

### 3. Create Secrets File

Create `secrets.tfvars` (DO NOT commit to git):
```hcl
db_master_username = "admin"
db_master_password = "your-secure-password"
redis_auth_token   = "your-redis-auth-token"
container_image    = "your-ecr-repo/fastapi-app:latest"
```

## Usage

### Development Environment

```bash
# Initialize Terraform
terraform init -backend-config=backend-dev.hcl

# Plan changes
terraform plan -var-file=dev.tfvars -var-file=secrets.tfvars

# Apply changes
terraform apply -var-file=dev.tfvars -var-file=secrets.tfvars

# Destroy infrastructure
terraform destroy -var-file=dev.tfvars -var-file=secrets.tfvars
```

### Production Environment

```bash
# Initialize Terraform
terraform init -backend-config=backend-prod.hcl

# Plan changes
terraform plan -var-file=prod.tfvars -var-file=secrets.tfvars

# Apply changes
terraform apply -var-file=prod.tfvars -var-file=secrets.tfvars
```

## Modules

### VPC Module
Creates VPC with:
- Public subnets (for ALB)
- Private subnets (for ECS tasks)
- Data subnets (for RDS and Redis)
- NAT Gateways for outbound internet access
- Route tables and associations

### RDS Module
Creates PostgreSQL database with:
- Multi-AZ deployment
- Automated backups (7-30 days retention)
- Encryption at rest
- Enhanced monitoring
- Parameter groups for logging

### ElastiCache Module
Creates Redis cluster with:
- Replication group
- Multi-AZ deployment
- Encryption at rest and in transit
- Auth token support
- Automated snapshots

### ECS Module
Creates ECS infrastructure with:
- Fargate cluster
- Task definitions
- Service with auto-scaling
- CloudWatch log groups
- Security groups

### ALB Module
Creates Application Load Balancer with:
- HTTP to HTTPS redirect
- Health checks
- Target groups
- Security groups

### IAM Module
Creates IAM roles with:
- ECS task execution role
- ECS task role with least privileges
- Managed policies

## Outputs

After applying, Terraform outputs:
- `vpc_id`: VPC identifier
- `database_endpoint`: RDS connection endpoint
- `redis_endpoint`: Redis connection endpoint
- `alb_dns_name`: Load balancer DNS name
- `ecs_cluster_name`: ECS cluster name
- `ecs_service_name`: ECS service name

## Security Best Practices

1. **State Encryption**: S3 bucket encrypted, DynamoDB for locking
2. **Secrets Management**: Use AWS Secrets Manager or Parameter Store
3. **Least Privilege**: IAM roles have minimal required permissions
4. **Network Isolation**: Private subnets for application and data layers
5. **Encryption**: RDS and Redis encrypted at rest and in transit
6. **Multi-AZ**: High availability with multi-AZ deployments
7. **Backup**: Automated backups with retention policies

## Cost Optimization

### Development
- Single AZ deployment
- Smaller instance types (t3.micro)
- Reduced backup retention
- Single ECS task

### Production
- Multi-AZ for high availability
- Larger instance types (t3.small+)
- Extended backup retention
- Multiple ECS tasks with auto-scaling

## Troubleshooting

### State Lock Issues
```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

### Module Errors
```bash
# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

### Dependency Issues
```bash
# Refresh state
terraform refresh -var-file=dev.tfvars -var-file=secrets.tfvars

# Target specific resource
terraform apply -target=module.vpc -var-file=dev.tfvars -var-file=secrets.tfvars
```

## Maintenance

### Updating Infrastructure
1. Update variable files or module code
2. Run `terraform plan` to review changes
3. Run `terraform apply` to apply changes
4. Monitor CloudWatch for any issues

### Backup State
```bash
# Download current state
terraform state pull > terraform.tfstate.backup
```

### Import Existing Resources
```bash
# Import existing resource
terraform import module.vpc.aws_vpc.main vpc-xxxxx
```

## Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
