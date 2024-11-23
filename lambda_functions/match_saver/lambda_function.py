import json
import boto3
import os


def lambda_handler(event, context):
    s3_bucket = os.environ["S3_BUCKET_NAME"]
    s3_client = boto3.client("s3")

    # Initialize match_results
    match_results = "No match results provided."
    file_name = f"match_results_{context.aws_request_id}.txt"

    # Check if 'body' exists in the event (if invoked via API Gateway)
    if "body" in event:
        try:
            body = json.loads(event["body"])
            match_results = body.get("match_results", match_results)
        except json.JSONDecodeError:
            match_results = "Invalid JSON in request body."
    else:
        # Direct invocation from EC2
        match_results = event.get("match_results", match_results)

    # Save match results to S3
    try:
        s3_client.put_object(Bucket=s3_bucket, Key=file_name, Body=match_results)
        return {
            "statusCode": 200,
            "body": json.dumps(f"Match results saved as {file_name}"),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error saving match results: {str(e)}"),
        }
