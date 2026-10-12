# AWS Secrets Manager integration with KMS CMK encryption
# Allows runtime injection of secure credentials directly into ECS containers

resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.project_name}-app-secrets"
  description             = "Application secrets for ${var.project_name}"
  kms_key_id              = aws_kms_key.app_cmk.arn
  recovery_window_in_days = 0

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app_secrets_val" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    API_KEY      = "production-service-token-v1"
    DATABASE_URL = "postgres://app_user:protected_pass@cluster.internal:5432/app"
  })
}

# Attach SecretsManager access to ECS execution role
resource "aws_iam_policy" "ecs_secrets_access" {
  name        = "${var.project_name}-secrets-read"
  description = "Allows ECS execution role to decrypt Secrets Manager values"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [aws_secretsmanager_secret.app_secrets.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = [aws_kms_key.app_cmk.arn]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_attach" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = aws_iam_policy.ecs_secrets_access.arn
}
