import redis
import uuid
import json
import os
from dotenv import load_dotenv
from model.player import Player

# Load environment variables from .env file
load_dotenv()

class PlayerService:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)

    def create_player(self, nickname):
        # Check if the nickname is unique
        for key in self.redis_client.keys():
            player_data = self.redis_client.get(key)
            player_dict = json.loads(player_data)
            if player_dict['nickname'] == nickname:
                return None  

        new_player = Player(
            id=str(uuid.uuid4()),
            nickname=nickname,
            wins=0,
            losses=0,
            elo=0,
            hoursPlayed=0,
            team=None,
            ratingAdjustment=None,
        )
        self.redis_client.set(new_player.id, json.dumps(new_player.__dict__))
        return new_player

    def get_player(self, player_id):
        player_data = self.redis_client.get(player_id)
        if player_data:
            player_dict = json.loads(player_data)
            return Player.from_dict(player_dict)
        return None