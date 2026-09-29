# ---------------------------------------------------------------------
# AWS Systems Manager (SSM) Parameter Store for Production Configuration
# ---------------------------------------------------------------------

resource "aws_ssm_parameter" "log_level" {
  name        = "/${var.project_name}/production/LOG_LEVEL"
  description = "Application log level configuration"
  type        = "String"
  value       = "INFO"

  tags = merge(local.common_tags, {
    Environment = "production"
  })
}

resource "aws_ssm_parameter" "app_environment" {
  name        = "/${var.project_name}/production/ENVIRONMENT"
  description = "Runtime environment identification"
  type        = "String"
  value       = "production"

  tags = merge(local.common_tags, {
    Environment = "production"
  })
}

# IAM Policy for ECS Tasks to securely retrieve parameters
data "aws_iam_policy_document" "ecs_ssm_read" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/*"
    ]
  }
}

resource "aws_iam_policy" "ecs_ssm_read" {
  name        = "${var.project_name}-ecs-ssm-read-policy"
  description = "Allows ECS tasks to read configuration parameters from SSM Parameter Store"
  policy      = data.aws_iam_policy_document.ecs_ssm_read.json
  tags        = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_ssm" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = aws_iam_policy.ecs_ssm_read.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_ssm" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.ecs_ssm_read.arn
}
