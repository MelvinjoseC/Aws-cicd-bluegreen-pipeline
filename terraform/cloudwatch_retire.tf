# CloudWatch ECS Task Churn & Health Alarms
# Monitors rapid task exits or premature container terminations

resource "aws_cloudwatch_metric_alarm" "task_churn" {
  alarm_name          = "${var.project_name}-task-churn-detected"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 90
  alarm_description   = "Triggered when ECS task memory exceeds 90%, risking OOM kills"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.prod.name
  }

  tags = local.common_tags
}
