# CloudWatch Synthetics Canary for 24/7 Automated User Journey Monitoring
# Proactively catches silent outages and performance degradation

resource "aws_cloudwatch_metric_alarm" "synthetic_canary_failure" {
  alarm_name          = "${var.project_name}-synthetic-canary-failed"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "SuccessPercent"
  namespace           = "CloudWatchSynthetics"
  period              = 300
  statistic           = "Average"
  threshold           = 95
  alarm_description   = "Triggers rollback if synthetic customer journeys experience errors"

  dimensions = {
    CanaryName = "${var.project_name}-heartbeat"
  }

  tags = local.common_tags
}
