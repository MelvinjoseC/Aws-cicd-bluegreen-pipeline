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

resource "aws_cloudwatch_metric_alarm" "prod_latency_blue" {
  alarm_name          = "${var.project_name}-prod-latency-blue"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  extended_statistic  = "p95"
  threshold           = 1.0 # 1.0 second response time SLA
  treat_missing_data  = "notBreaching"
  alarm_description   = "Watches blue target group p95 response time; rolls back if SLA is violated."

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.blue.arn_suffix
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "prod_latency_green" {
  alarm_name          = "${var.project_name}-prod-latency-green"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  extended_statistic  = "p95"
  threshold           = 1.0 # 1.0 second response time SLA
  treat_missing_data  = "notBreaching"
  alarm_description   = "Watches green target group p95 response time; rolls back if SLA is violated."

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.green.arn_suffix
  }

  tags = local.common_tags
}
