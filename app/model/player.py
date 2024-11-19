class Player:
    def __init__(self, id, nickname, wins=0, losses=0, elo=0, hoursPlayed=0, team=None, ratingAdjustment=None):
        self.id = id
        self.nickname = nickname
        self.wins = wins
        self.losses = losses
        self.elo = elo
        self.hoursPlayed = hoursPlayed
        self.team = team
        self.ratingAdjustment = ratingAdjustment

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            nickname=data['nickname'],
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            elo=data.get('elo', 0),
            hoursPlayed=data.get('hoursPlayed', 0),
            team=data.get('team'),
            ratingAdjustment=data.get('ratingAdjustment'))