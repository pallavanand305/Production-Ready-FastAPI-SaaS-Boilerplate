# Development Environment Variables

environment = "dev"
aws_region  = "us-east-1"

# VPC
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# RDS
rds_instance_class          = "db.t3.micro"
rds_allocated_storage       = 20
rds_multi_az                = false
rds_backup_retention_period = 3
rds_deletion_protection     = false
rds_skip_final_snapshot     = true
database_name               = "fastapi_dev"

# ElastiCache
redis_node_type                 = "cache.t3.micro"
redis_num_cache_nodes           = 1
redis_automatic_failover_enabled = false
redis_multi_az_enabled          = false
redis_snapshot_retention_limit  = 1

# ECS
ecs_desired_count = 1
ecs_task_cpu      = "256"
ecs_task_memory   = "512"
container_port    = 8000
