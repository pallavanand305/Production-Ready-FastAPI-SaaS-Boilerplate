# Main Terraform Configuration
# Wires all modules together

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Backend configuration should be provided via backend config file
    # terraform init -backend-config=backend-{env}.hcl
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  tags               = local.common_tags
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  project_name            = var.project_name
  vpc_id                  = module.vpc.vpc_id
  subnet_ids              = module.vpc.data_subnet_ids
  allowed_security_groups = [module.ecs.ecs_security_group_id]

  engine_version          = var.rds_engine_version
  instance_class          = var.rds_instance_class
  allocated_storage       = var.rds_allocated_storage
  max_allocated_storage   = var.rds_max_allocated_storage
  database_name           = var.database_name
  master_username         = var.db_master_username
  master_password         = var.db_master_password
  multi_az                = var.rds_multi_az
  backup_retention_period = var.rds_backup_retention_period
  deletion_protection     = var.rds_deletion_protection
  skip_final_snapshot     = var.rds_skip_final_snapshot

  tags = local.common_tags
}

# ElastiCache Module
module "elasticache" {
  source = "./modules/elasticache"

  project_name            = var.project_name
  vpc_id                  = module.vpc.vpc_id
  subnet_ids              = module.vpc.data_subnet_ids
  allowed_security_groups = [module.ecs.ecs_security_group_id]

  engine_version              = var.redis_engine_version
  node_type                   = var.redis_node_type
  num_cache_nodes             = var.redis_num_cache_nodes
  auth_token_enabled          = var.redis_auth_token_enabled
  auth_token                  = var.redis_auth_token
  automatic_failover_enabled  = var.redis_automatic_failover_enabled
  multi_az_enabled            = var.redis_multi_az_enabled
  snapshot_retention_limit    = var.redis_snapshot_retention_limit

  tags = local.common_tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  tags         = local.common_tags
}

# ALB Module
module "alb" {
  source = "./modules/alb"

  project_name    = var.project_name
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.public_subnet_ids
  certificate_arn = var.acm_certificate_arn

  tags = local.common_tags
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"

  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids

  task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  task_role_arn           = module.iam.ecs_task_role_arn

  alb_target_group_arn = module.alb.target_group_arn
  alb_security_group_id = module.alb.alb_security_group_id

  container_image = var.container_image
  container_port  = var.container_port
  desired_count   = var.ecs_desired_count
  cpu             = var.ecs_task_cpu
  memory          = var.ecs_task_memory

  environment_variables = {
    DATABASE_URL = "postgresql://${var.db_master_username}:${var.db_master_password}@${module.rds.db_instance_address}:${module.rds.db_instance_port}/${var.database_name}"
    REDIS_URL    = "redis://${module.elasticache.redis_endpoint}:${module.elasticache.redis_port}"
    ENVIRONMENT  = var.environment
  }

  tags = local.common_tags
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
