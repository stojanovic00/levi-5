import boto3
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from model.team import Team

# Load environment variables from .env file
load_dotenv()

class TeamRepository:
    def __init__(self):
        # self.dynamodb = boto3.resource('dynamodb')
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url='http://localhost:8000',  # Local DynamoDB endpoint
            region_name='eu-central-1',  # Specify your region
            aws_access_key_id='local',  # Dummy credentials for local DynamoDB
            aws_secret_access_key='local'
        )
        
        self.table_name =  'Teams'
        self.table = self.dynamodb.Table(self.table_name)

    def save_team(self, team: Team):
        self.table.put_item(Item=team.to_dict())

    def get_team(self, team_id: str) -> Optional[Team]:
        response = self.table.get_item(Key={'id': team_id})
        if 'Item' in response:
            return Team.from_dict(response['Item'])
        return None

    def get_all_teams(self) -> List[Team]:
        response = self.table.scan()
        teams = [Team.from_dict(item) for item in response.get('Items', [])]
        return teams

    def delete_all(self):
        response = self.table.scan()
        with self.table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(Key={'id': item['id']})