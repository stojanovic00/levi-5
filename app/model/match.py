from typing import Optional

class Match:
    def __init__(self, id: str, team1Id: str, team2Id: str, winningTeamId: Optional[str], duration: int):
        self.id = id
        self.team1Id = team1Id
        self.team2Id = team2Id
        self.winningTeamId = winningTeamId
        self.duration = duration

    @classmethod
    def from_dict(cls, data: dict) -> 'Match':
        return cls(
            id=data['id'],
            team1Id=data['team1Id'],
            team2Id=data['team2Id'],
            winningTeamId=data.get('winningTeamId'),
            duration=data['duration']
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'team1Id': self.team1Id,
            'team2Id': self.team2Id,
            'winningTeamId': self.winningTeamId,
            'duration': self.duration
        }
