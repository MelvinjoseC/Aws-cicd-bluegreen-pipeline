# Terraform Backend Configuration
# Enables team concurrency locking via DynamoDB and state history retention via S3

terraform {
  # Note: Run terraform/modules/remote_state first to provision bucket and DynamoDB table.
  # backend "s3" {
  #   bucket         = "cicd-demo-tfstate-us-east-1"
  #   key            = "platform/ecs-bluegreen.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "cicd-demo-tfstate-lock"
  #   encrypt        = true
  # }
}
