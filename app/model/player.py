class Player:
    def __init__(self, id, nickname, wins=0, losses=0, elo=0, hoursPlayed=0, teamId=None, ratingAdjustment=50):
        self.id: str = id
        self.nickname: str = nickname
        self.wins: int = wins
        self.losses: int = losses
        self.elo: int = elo
        self.hoursPlayed:int = hoursPlayed
        self.teamId: str = teamId
        self.ratingAdjustment: int = ratingAdjustment

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            nickname=data['nickname'],
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            elo=data.get('elo', 0),
            hoursPlayed=data.get('hoursPlayed', 0),
            teamId=data.get('teamId'),
            ratingAdjustment=data.get('ratingAdjustment')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'wins': int(self.wins),
            'losses': int(self.losses),
            'elo': int(self.elo),
            'hoursPlayed': int(self.hoursPlayed),
            'teamId': self.teamId,
            'ratingAdjustment': int(self.ratingAdjustment) if self.ratingAdjustment is not None else None
        }
