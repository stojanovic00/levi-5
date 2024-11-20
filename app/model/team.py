from typing import List
from .player import Player


class Team:
    def __init__(self, id, teamName, players=[]):
        self.id = id
        self.teamName = teamName
        self.players: List[Player] = players 

    @classmethod
    def from_dict(cls, data) -> 'Team':
        players = [Player.from_dict(player) for player in data.get('players', [])]
        return cls(
            id=data['id'],
            teamName=data['teamName'],
            players=players
        )

    def to_dict(self):
        players = [player.to_dict() for player in self.players]
        return {
            'id': self.id,
            'teamName': self.teamName,
            'players': players
            }

