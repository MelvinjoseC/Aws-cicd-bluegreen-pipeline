# ---------------------------------------------------------------------
# Application Auto Scaling for ECS Fargate Production Service
# ---------------------------------------------------------------------

resource "aws_appautoscaling_target" "prod" {
  max_capacity       = var.ecs_autoscale_max_capacity
  min_capacity       = var.ecs_autoscale_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.prod.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# CPU-based Target Tracking Auto Scaling Policy
resource "aws_appautoscaling_policy" "prod_cpu" {
  name               = "${var.project_name}-prod-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.prod.resource_id
  scalable_dimension = aws_appautoscaling_target.prod.scalable_dimension
  service_namespace  = aws_appautoscaling_target.prod.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value       = var.ecs_target_cpu_utilization
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Memory-based Target Tracking Auto Scaling Policy
resource "aws_appautoscaling_policy" "prod_memory" {
  name               = "${var.project_name}-prod-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.prod.resource_id
  scalable_dimension = aws_appautoscaling_target.prod.scalable_dimension
  service_namespace  = aws_appautoscaling_target.prod.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value       = var.ecs_target_memory_utilization
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
