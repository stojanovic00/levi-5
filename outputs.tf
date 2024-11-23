output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "api_endpoint" {
  description = "Invoke URL of the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.api_gateway.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.api_stage.stage_name}${aws_api_gateway_resource.api_resource.path}"
}

output "private_key_pem" {
  description = "Private key for SSH access"
  value       = tls_private_key.example.private_key_pem
  sensitive   = true
}

output "docdb_cluster_endpoint" {
  description = "DocumentDB Cluster Endpoint"
  value       = aws_docdb_cluster.docdb_cluster.endpoint
}

output "lambda_api_url" {
  description = "URL for invoking the Lambda function via API Gateway"
  value       = "https://${aws_api_gateway_rest_api.lambda_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.lambda_api_stage.stage_name}"
}