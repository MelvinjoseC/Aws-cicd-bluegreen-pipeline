variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-\\d$", var.aws_region))
    error_message = "The aws_region variable must be a valid AWS region identifier (e.g. us-east-1)."
  }
}

variable "project_name" {
  description = "Name prefix applied to all resources"
  type        = string
  default     = "cicd-demo"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "The vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "container_port" {
  description = "Port the application container listens on"
  type        = number
  default     = 8080

  validation {
    condition     = var.container_port > 0 && var.container_port <= 65535
    error_message = "The container_port must be a valid TCP port number between 1 and 65535."
  }
}

variable "task_cpu" {
  description = "Fargate task CPU units"
  type        = string
  default     = "256"
}

variable "task_memory" {
  description = "Fargate task memory in MiB"
  type        = string
  default     = "512"
}

variable "github_org_repo" {
  description = "GitHub org/repo allowed to assume the OIDC deploy role, e.g. your-username/your-repo"
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_org_repo))
    error_message = "The github_org_repo must be formatted as 'organization-or-user/repository'."
  }
}

variable "ecs_autoscale_min_capacity" {
  description = "Minimum number of tasks for production ECS service autoscaling"
  type        = number
  default     = 2

  validation {
    condition     = var.ecs_autoscale_min_capacity >= 1
    error_message = "Minimum autoscaling capacity must be at least 1."
  }
}

variable "ecs_autoscale_max_capacity" {
  description = "Maximum number of tasks for production ECS service autoscaling"
  type        = number
  default     = 10

  validation {
    condition     = var.ecs_autoscale_max_capacity >= 2
    error_message = "Maximum autoscaling capacity must be at least 2."
  }
}

variable "ecs_target_cpu_utilization" {
  description = "Target average CPU utilization percentage for autoscaling trigger"
  type        = number
  default     = 70
}

variable "ecs_target_memory_utilization" {
  description = "Target average Memory utilization percentage for autoscaling trigger"
  type        = number
  default     = 80
}
