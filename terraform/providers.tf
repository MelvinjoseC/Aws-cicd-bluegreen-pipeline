terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure a remote backend before running `terraform init`, e.g.:
  #   terraform init \
  #     -backend-config="bucket=your-tfstate-bucket" \
  #     -backend-config="key=cicd-demo/terraform.tfstate" \
  #     -backend-config="region=us-east-1"
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}
