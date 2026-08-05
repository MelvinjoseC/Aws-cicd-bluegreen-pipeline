resource "aws_cloudwatch_metric_alarm" "prod_5xx_blue" {
  alarm_name          = "${var.project_name}-prod-5xx-rate-blue"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_description   = "Watches the blue target group; CodeDeploy rolls back automatically if this fires during deployment."

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.blue.arn_suffix
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "prod_5xx_green" {
  alarm_name          = "${var.project_name}-prod-5xx-rate-green"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_description   = "Watches the green target group; CodeDeploy rolls back automatically if this fires during deployment."

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.green.arn_suffix
  }

  tags = local.common_tags
}
