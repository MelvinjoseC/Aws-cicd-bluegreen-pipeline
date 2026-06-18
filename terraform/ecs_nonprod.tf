locals {
  nonprod_envs = ["dev", "staging"]
}

resource "aws_lb" "nonprod" {
  for_each = toset(local.nonprod_envs)

  name               = "${var.project_name}-${each.key}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = { Name = "${var.project_name}-${each.key}-alb" }
}

resource "aws_lb_target_group" "nonprod" {
  for_each = toset(local.nonprod_envs)

  name        = "${var.project_name}-${each.key}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 15
    timeout             = 5
  }

  tags = { Name = "${var.project_name}-${each.key}-tg" }
}

resource "aws_lb_listener" "nonprod" {
  for_each = toset(local.nonprod_envs)

  load_balancer_arn = aws_lb.nonprod[each.key].arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.nonprod[each.key].arn
  }
}

resource "aws_cloudwatch_log_group" "nonprod" {
  for_each = toset(local.nonprod_envs)

  name              = "/ecs/${var.project_name}-${each.key}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "nonprod" {
  for_each = toset(local.nonprod_envs)

  family                   = "${var.project_name}-${each.key}"
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
        "awslogs-group"         = aws_cloudwatch_log_group.nonprod[each.key].name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = each.key
      }
    }
  }])
}

resource "aws_ecs_service" "nonprod" {
  for_each = toset(local.nonprod_envs)

  name            = "${var.project_name}-${each.key}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.nonprod[each.key].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.nonprod[each.key].arn
    container_name   = "cicd-demo-app"
    container_port   = var.container_port
  }

  # The pipeline updates the running task definition directly via the AWS
  # CLI/Actions — Terraform shouldn't revert it back to ":latest" on plan.
  lifecycle {
    ignore_changes = [task_definition]
  }
}
