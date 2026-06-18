resource "aws_lb" "main" {
  name               = "${var.project_name}-prod-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = { Name = "${var.project_name}-prod-alb" }
}

resource "aws_lb_target_group" "blue" {
  name        = "${var.project_name}-tg-blue"
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

  tags = { Name = "${var.project_name}-tg-blue" }
}

resource "aws_lb_target_group" "green" {
  name        = "${var.project_name}-tg-green"
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

  tags = { Name = "${var.project_name}-tg-green" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue.arn
  }

  # CodeDeploy repoints this listener between the blue and green target
  # groups during each deployment — Terraform shouldn't fight it afterwards.
  lifecycle {
    ignore_changes = [default_action]
  }
}
