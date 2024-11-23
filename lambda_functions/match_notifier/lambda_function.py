import json
import boto3
import os


def lambda_handler(event, context):
    sns_topic_arn = os.environ["SNS_TOPIC_ARN"]
    sns_client = boto3.client("sns")

    # Extract match details from the event
    match_details = event.get("match_details", "No match details provided.")

    # Publish message to SNS
    response = sns_client.publish(
        TopicArn=sns_topic_arn, Message=match_details, Subject="New Match Details"
    )

    return {"statusCode": 200, "body": json.dumps("Message sent to SNS")}
