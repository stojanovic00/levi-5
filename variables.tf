variable "aws_region" {
  description = "The AWS region to deploy into"
  default     = "eu-central-1"  # Changed from "us-east-1"
}

variable "docdb_username" {
  description = "Master username for DocumentDB"
  default     = "docdb_user"
}

variable "docdb_password" {
  description = "Master password for DocumentDB"
  default     = "YourSecurePassword123!"  # Use a strong password
}

variable "notification_email" {
  description = "Email address for SNS notifications"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  default     = "209479296454"
  type        = string
}
