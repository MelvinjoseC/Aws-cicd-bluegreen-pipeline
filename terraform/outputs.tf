output "prod_alb_dns_name" {
  description = "Public DNS name of the production ALB"
  value       = aws_lb.main.dns_name
}

output "dev_alb_dns_name" {
  description = "Public DNS name of the dev ALB"
  value       = aws_lb.nonprod["dev"].dns_name
}

output "staging_alb_dns_name" {
  description = "Public DNS name of the staging ALB — set this as the STAGING_ALB_DNS secret"
  value       = aws_lb.nonprod["staging"].dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL the pipeline pushes images to"
  value       = aws_ecr_repository.app.repository_url
}

output "github_deploy_role_arn" {
  description = "Role ARN GitHub Actions assumes via OIDC — set this as the AWS_GITHUB_OIDC_ROLE_ARN secret"
  value       = aws_iam_role.github_deploy.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "waf_web_acl_arn" {
  description = "ARN of the AWS WAFv2 Web ACL protecting the production ALB"
  value       = aws_wafv2_web_acl.main.arn
}

output "alb_access_logs_bucket" {
  description = "S3 bucket receiving encrypted ALB access logs"
  value       = aws_s3_bucket.alb_logs.bucket
}

output "cloudwatch_dashboard_name" {
  description = "Name of the production CloudWatch Operational Dashboard"
  value       = aws_cloudwatch_dashboard.prod.dashboard_name
}
