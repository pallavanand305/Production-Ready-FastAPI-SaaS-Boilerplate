# S3 Backend Configuration for Terraform State
# 
# This file configures S3 backend for storing Terraform state.
# State locking is handled by DynamoDB.
#
# Usage:
#   terraform init -backend-config=backend-dev.hcl
#   terraform init -backend-config=backend-prod.hcl

# Note: The actual backend configuration is in the main.tf file.
# Environment-specific backend configs should be in separate .hcl files:
#
# backend-dev.hcl:
#   bucket         = "your-terraform-state-bucket"
#   key            = "dev/terraform.tfstate"
#   region         = "us-east-1"
#   encrypt        = true
#   dynamodb_table = "terraform-state-lock"
#
# backend-prod.hcl:
#   bucket         = "your-terraform-state-bucket"
#   key            = "prod/terraform.tfstate"
#   region         = "us-east-1"
#   encrypt        = true
#   dynamodb_table = "terraform-state-lock"

# Prerequisites:
# 1. Create S3 bucket for state storage
# 2. Enable versioning on the bucket
# 3. Enable encryption on the bucket
# 4. Create DynamoDB table for state locking with primary key "LockID" (String)
