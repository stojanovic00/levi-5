import redis
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from model.player import Player

# Load environment variables from .env file
load_dotenv()

class PlayerRepository:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.players_set = "players"

    def save_player(self, new_player: Player):
        self.redis_client.set(new_player.id, json.dumps(new_player.__dict__))
        self.redis_client.sadd(self.players_set, new_player.id)

    def get_player(self, player_id: str) -> Optional[Player]:
        player_data = self.redis_client.get(player_id)
        if player_data:
            player_dict = json.loads(player_data)
            return Player.from_dict(player_dict)
        return None

    def get_all_players(self) -> List[Player]:
        players = []
        for key in self.redis_client.smembers(self.players_set):
            player = self.get_player(key)
            if player:
                players.append(player)
        return players