import uuid

from typing import List
from enum import Enum
from dotenv import load_dotenv

from model.player import Player
from repository.player_repository import PlayerRepository
from repository.team_repository import TeamRepository
from repository.match_repository import MatchRepository
from .errors import Error, ErrorType



class PlayerService:
    def __init__(self):
        self.player_repository = PlayerRepository()
        self.team_repository = TeamRepository()
        self.match_repository = MatchRepository()

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

        self.player_repository.save_player(new_player)
        return new_player

    def get_player(self, player_id):
        player = self.player_repository.get_player(player_id)
        if player:
            return player
        raise Error(ErrorType.PLAYER_NOT_FOUND, f"player with ID '{player_id}' not found")
    
    def get_all_players(self) -> List[Player]:
        return self.player_repository.get_all_players()

    def update_player(self, updated_player: Player):
        exists = self.get_player(updated_player.id)
        if not exists:
            raise Error(ErrorType.PLAYER_NOT_FOUND, f"player with ID {updated_player.id} not found")

        self.player_repository.save_player(updated_player)
        return 

    def delete_all(self):
        self.match_repository.delete_all()
        self.team_repository.delete_all()
        self.player_repository.delete_all()
        return

    