import boto3
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from model.match import Match

# Load environment variables from .env file
load_dotenv()

class MatchRepository:
    def __init__(self):
        # self.dynamodb = boto3.resource('dynamodb')
        # Check if running locally
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url='http://localhost:8000',  # Local DynamoDB endpoint
            region_name='eu-central-1',  # Specify your region
            aws_access_key_id='local',  # Dummy credentials for local DynamoDB
            aws_secret_access_key='local'
        )
        self.table_name =  'Matches'
        self.table = self.dynamodb.Table(self.table_name)

    def save_match(self, new_match: Match):
        self.table.put_item(Item=new_match.to_dict())


    def get_match(self, match_id: str) -> Optional[Match]:
        response = self.table.get_item(Key={'id': match_id})
        if 'Item' in response:
            return Match.from_dict(response['Item'])
        return None

    def get_all_matches(self) -> List[Match]:
        response = self.table.scan()
        matches = [Match.from_dict(item) for item in response.get('Items', [])]
        return matches

    def delete_all(self):
        response = self.table.scan()
        with self.table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(Key={'id': item['id']})