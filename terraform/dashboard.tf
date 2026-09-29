# ---------------------------------------------------------------------
# CloudWatch Operational Dashboard for Production Blue-Green Deployments
# ---------------------------------------------------------------------

resource "aws_cloudwatch_dashboard" "prod" {
  dashboard_name = "${var.project_name}-production-overview"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "ALB Request Distribution (Blue vs Green Target Groups)"
          period  = 60
          stat    = "Sum"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "TargetGroup", aws_lb_target_group.blue.arn_suffix, "LoadBalancer", aws_lb.main.arn_suffix, { label = "Blue Target Group Requests", color = "#1f77b4" }],
            ["AWS/ApplicationELB", "RequestCount", "TargetGroup", aws_lb_target_group.green.arn_suffix, "LoadBalancer", aws_lb.main.arn_suffix, { label = "Green Target Group Requests", color = "#2ca02c" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "HTTP 5XX & 4XX Error Rates"
          period = 60
          stat   = "Sum"
          view   = "timeSeries"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", aws_lb.main.arn_suffix, { label = "Target 5XX", color = "#d62728" }],
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", aws_lb.main.arn_suffix, { label = "ELB 5XX", color = "#ff7f0e" }],
            ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", aws_lb.main.arn_suffix, { label = "Target 4XX", color = "#9467bd" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Target Response Time Latency (p50, p95, p99)"
          period = 60
          view   = "timeSeries"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix, { stat = "p50", label = "p50 Latency (s)", color = "#17becf" }],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix, { stat = "p95", label = "p95 Latency (s)", color = "#bcbd22" }],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix, { stat = "p99", label = "p99 Latency (s)", color = "#e377c2" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "ECS Fargate CPU & Memory Utilization"
          period = 60
          stat   = "Average"
          view   = "timeSeries"
          region = var.aws_region
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", aws_ecs_service.prod.name, "ClusterName", aws_ecs_cluster.main.name, { label = "Prod ECS CPU (%)", color = "#2ca02c" }],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", aws_ecs_service.prod.name, "ClusterName", aws_ecs_cluster.main.name, { label = "Prod ECS Memory (%)", color = "#1f77b4" }]
          ]
        }
      }
    ]
  })
}
