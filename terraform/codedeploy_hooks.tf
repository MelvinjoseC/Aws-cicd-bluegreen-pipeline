# CodeDeploy Lifecycle Hook Lambda Infrastructure

resource "aws_iam_role" "codedeploy_hook_lambda" {
  name = "${var.project_name}-codedeploy-hook-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
  tags = local.common_tags
}

resource "aws_iam_role_policy" "codedeploy_hook_policy" {
  name = "${var.project_name}-hook-policy"
  role = aws_iam_role.codedeploy_hook_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "codedeploy:PutLifecycleEventHookExecutionStatus"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
