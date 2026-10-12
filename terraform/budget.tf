# FinOps Budget and CloudWatch Cost Alarm
# Alerts platform engineers if monthly infrastructure spend exceeds forecasted limits

resource "aws_sns_topic" "finops_alerts" {
  name = "${var.project_name}-finops-alerts"
  tags = local.common_tags
}

resource "aws_budgets_budget" "monthly_spend" {
  name              = "${var.project_name}-monthly-budget"
  budget_type       = "COST"
  limit_amount      = "150"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2026-01-01_00:00"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["platform-finops@example.com"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["platform-finops@example.com"]
  }
}
