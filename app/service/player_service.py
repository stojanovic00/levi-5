import redis
import uuid
import json
import os

from typing import List
from enum import Enum
from dotenv import load_dotenv

from model.player import Player
from .errors import Error, ErrorType


# Redis set for players
players_set = "players"
# Load environment variables from .env file
load_dotenv()

class PlayerService:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)

    def create_player(self, nickname) -> Player:
        # Check if the nickname is unique
        for player in self.get_all_players():
            if player.nickname == nickname:
                raise Error(ErrorType.NICKNAME_ALREADY_EXISTS, f"nickname '{nickname}' is already taken")

        new_player = Player(
            id=str(uuid.uuid4()),
            nickname=nickname,
            wins=0,
            losses=0,
            elo=0,
            hoursPlayed=0,
            teamId=None,
            ratingAdjustment=None,
        )

        self.redis_client.set(new_player.id, json.dumps(new_player.__dict__))
        self.redis_client.sadd(players_set, new_player.id)
        return new_player

    def get_player(self, player_id):
        player_data = self.redis_client.get(player_id)
        if player_data:
            player_dict = json.loads(player_data)
            return Player.from_dict(player_dict)
        raise Error(ErrorType.PLAYER_NOT_FOUND, f"player with ID {player_id} not found")
    
    def get_all_players(self) -> List[Player]:
        players = []
        for key in self.redis_client.smembers(players_set):
            player = self.get_player(key)
            if player:
                players.append(player)
        return players

    def update_player(self, updated_player: Player):
        # Check if the player exists
        exists = self.get_player(updated_player.id)
        if not exists:
            raise Error(ErrorType.PLAYER_NOT_FOUND, f"player with ID {updated_player.id} not found")

        # Save the updated player to Redis
        self.redis_client.set(updated_player.id, json.dumps(updated_player.to_dict()))
        self.redis_client.sadd(players_set, updated_player.id)

        return 

    