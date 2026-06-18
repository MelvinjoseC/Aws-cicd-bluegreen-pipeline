resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "prod" {
  name              = "/ecs/${var.project_name}-prod"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "prod" {
  family                   = "${var.project_name}-prod"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "cicd-demo-app"
    image     = "${aws_ecr_repository.app.repository_url}:latest"
    essential = true
    portMappings = [{
      containerPort = var.container_port
      protocol      = "tcp"
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.prod.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "prod"
      }
    }
  }])
}

resource "aws_ecs_service" "prod" {
  name            = "${var.project_name}-prod"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.prod.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  deployment_controller {
    type = "CODE_DEPLOY"
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.blue.arn
    container_name   = "cicd-demo-app"
    container_port   = var.container_port
  }

  # After the first deploy, CodeDeploy owns task definition and target
  # group swaps for this service — Terraform should leave them alone.
  lifecycle {
    ignore_changes = [task_definition, load_balancer]
  }
}
