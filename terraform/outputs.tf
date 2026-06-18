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
