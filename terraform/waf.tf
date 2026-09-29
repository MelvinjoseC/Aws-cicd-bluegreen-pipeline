# ---------------------------------------------------------------------
# AWS WAFv2 Web ACL Protection for Production Application Load Balancer
# ---------------------------------------------------------------------

resource "aws_wafv2_web_acl" "main" {
  name        = "${var.project_name}-prod-waf"
  description = "Production WAF Web ACL protecting ALB against OWASP Top 10 and Layer 7 floods"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rule 1: IP Rate Limiting (mitigates DDoS and abusive crawling)
  rule {
    name     = "RateLimit2000Per5Min"
    priority = 10

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-waf-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: AWS Managed Rules - Common Rule Set (OWASP Core Rule Set)
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 20

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-waf-common-rules"
      sampled_requests_enabled   = true
    }
  }

  # Rule 3: AWS Managed Rules - Known Bad Inputs
  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 30

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-waf-known-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  # Rule 4: AWS Managed Rules - Amazon IP Reputation List
  rule {
    name     = "AWS-AWSManagedRulesAmazonIpReputationList"
    priority = 40

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-waf-ip-reputation"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-prod-waf-metric"
    sampled_requests_enabled   = true
  }

  tags = merge(local.common_tags, {
    Name        = "${var.project_name}-prod-waf"
    Environment = "production"
  })
}

# Associate WAF Web ACL with Production ALB
resource "aws_wafv2_web_acl_association" "prod_alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}
