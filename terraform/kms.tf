# Customer Managed Key (CMK) for multi-service encryption
# Enforces enterprise compliance, envelope encryption, and key rotation

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "app_cmk" {
  description             = "KMS CMK for ${var.project_name} - Secrets, CloudWatch Logs, and ECR"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "${var.project_name}-key-policy"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs Encryption"
        Effect = "Allow"
        Principal = {
          Service = "logs.${var.aws_region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager Encryption"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_kms_alias" "app_cmk_alias" {
  name          = "alias/${var.project_name}-cmk"
  target_key_id = aws_kms_key.app_cmk.key_id
}

output "kms_cmk_arn" {
  description = "ARN of the KMS Customer Managed Key"
  value       = aws_kms_key.app_cmk.arn
}
