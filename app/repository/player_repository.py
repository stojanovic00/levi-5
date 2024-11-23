import redis
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from model.player import Player
import boto3

# Load environment variables from .env file
load_dotenv()

class PlayerRepository:
    def __init__(self):
        # TODO: Switch to deployment later
        # self.dynamodb = boto3.resource('dynamodb') not tested
        self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:8000', 
                region_name='eu-central-1', 
                aws_access_key_id='local',  
                aws_secret_access_key='local'
            )
        self.table_name = "Players"
        self.table = self.dynamodb.Table(self.table_name)

    def save_player(self, new_player: Player):
            self.table.put_item(Item=new_player.to_dict())

    # def get_player(self, player_id: str) -> Optional[Player]:
    #     player_data = self.redis_client.get(player_id)
    #     if player_data:
    #         player_dict = json.loads(player_data)
    #         return Player.from_dict(player_dict)
    #     return None

# def get_player(self, player_id: str) -> Optional[Player]:
#     try:
#         response = self.table.get_item(Key={'id': player_id})
#         if 'Item' in response:
#             return Player.from_dict(response['Item'])
#     except self.dynamodb.meta.client.exceptions.ResourceNotFoundException as e:
#         print(f"Error: {e}")
#         print(f"Table {self.table_name} not found. Please ensure the table exists.")
#     return None


    # TODO: handle errors, (code above)
    def get_player(self, player_id: str) -> Optional[Player]:
        response = self.table.get_item(Key={'id': player_id})
        if 'Item' in response:
            return Player.from_dict(response['Item'])
        return None

    # def get_all_players(self) -> List[Player]:
    #     players = []
    #     for key in self.redis_client.smembers(self.players_set):
    #         player = self.get_player(key)
    #         if player:
    #             players.append(player)
    #     return players

    # def get_all_players(self) -> List[Player]:
    #     try:
    #         response = self.table.scan()
    #         players = [Player.from_dict(item) for item in response.get('Items', [])]
    #         return players
    #     except self.dynamodb.meta.client.exceptions.ResourceNotFoundException as e:
    #         print(f"Error: {e}")
    #         print(f"Table {self.table_name} not found. Please ensure the table exists.")
    #     return []

    def get_all_players(self) -> List[Player]:
        response = self.table.scan()
        players = [Player.from_dict(item) for item in response.get('Items', [])]
        return players


    def delete_all(self):
        response = self.table.scan()
        with self.table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(Key={'id': item['id']})