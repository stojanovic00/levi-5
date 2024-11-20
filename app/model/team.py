import uuid

class Team:
    def __init__(self, id, teamName, players=None):
        self.id = id
        self.teamName = teamName
        self.players = players if players is not None else []

    @classmethod
    def from_dict(cls, data):
        team = cls(
            id=data['id'],
            teamName=data['teamName'],
            players=data.get('players', [])
        )

        return team

