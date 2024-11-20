import redis
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from model.team import Team
from model.player import Player

# Load environment variables from .env file
load_dotenv()

class TeamRepository:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.teams_set = "teams"

    def save_team(self, team: Team):
        self.redis_client.set(team.id, json.dumps(team.to_dict()))
        self.redis_client.sadd(self.teams_set, team.id)

    def get_team(self, team_id: str) -> Optional[Team]:
        team_data = self.redis_client.get(team_id)
        if team_data:
            team_dict = json.loads(team_data)
            return Team.from_dict(team_dict)
        return None

    def get_all_teams(self) -> List[Team]:
        teams = []
        for key in self.redis_client.smembers(self.teams_set):
            team = self.get_team(key)
            if team:
                teams.append(team)
        return teams