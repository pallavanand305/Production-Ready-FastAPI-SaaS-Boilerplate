# Production Environment Variables

environment = "prod"
aws_region  = "us-east-1"

# VPC
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

# RDS
rds_instance_class          = "db.t3.small"
rds_allocated_storage       = 100
rds_multi_az                = true
rds_backup_retention_period = 30
rds_deletion_protection     = true
rds_skip_final_snapshot     = false
database_name               = "fastapi_prod"

# ElastiCache
redis_node_type                 = "cache.t3.small"
redis_num_cache_nodes           = 3
redis_automatic_failover_enabled = true
redis_multi_az_enabled          = true
redis_snapshot_retention_limit  = 7

# ECS
ecs_desired_count = 3
ecs_task_cpu      = "512"
ecs_task_memory   = "1024"
container_port    = 8000
