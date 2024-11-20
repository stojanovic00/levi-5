from typing import List, Optional
import redis
import json
import os
import uuid
from dotenv import load_dotenv

from .player_service import PlayerService, Player
from model.team import Team

from enum import Enum

class TeamErrorType(Enum):
    INVALID_PLAYER_COUNT = "A team must have 5 players"
    TEAM_NAME_ALREADY_EXISTS = "Team name already exists"
    PLAYER_ALREADY_IN_TEAM = "Player is already in an another team"
    PLAYER_NOT_FOUND = "Player not found" # TODO: Return the player ID

teams_set = "teams"

# Load environment variables from .env file
load_dotenv()

class TeamService:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.player_service = PlayerService()

    def create_team(self, teamName, player_ids) -> tuple[Optional[Team], Optional[TeamErrorType]]:
        # Validations
        if len(player_ids) != 5:
            return None, TeamErrorType.INVALID_PLAYER_COUNT

        for team in self.get_all_teams():
            if team.teamName == teamName:
                return None, TeamErrorType.TEAM_NAME_ALREADY_EXISTS


        team_id = str(uuid.uuid4())
        # Find all players by their IDs
        players: List[Player] = []
        for player_id in player_ids:
            player = self.player_service.get_player(player_id)
            if player:
                if player.teamId:
                    return None, TeamErrorType.PLAYER_ALREADY_IN_TEAM

                player.teamId = team_id 
                self.player_service.update_player(player)
                players.append(player)
            else:
                return None, TeamErrorType.PLAYER_NOT_FOUND

        # Create a new team
        new_team = Team(
            id=team_id,
            teamName=teamName,
            players=players
        )

        # Save the team to Redis
        self.redis_client.set(new_team.id, json.dumps(new_team.to_dict()))
        self.redis_client.sadd(teams_set, new_team.id)

        return new_team, None

    def get_team(self, team_id) -> Optional[Team]:
        team_data = self.redis_client.get(team_id)
        if team_data:
            team_dict = json.loads(team_data)
            return Team.from_dict(team_dict)
        return None

    def get_all_teams(self) -> List[Team]:
            teams = []
            for key in self.redis_client.smembers(teams_set):
                team = self.get_team(key)
                if team:
                    teams.append(team)
            return teams
    
    def calculate_mean_elo(self, team: Team) -> float:
        total_elo = 0
        for player in team.players:
            total_elo += player.elo
        return total_elo / 5

    def update_team(self, updated_team: Team):
        # Check if the team exists
        exists = self.get_team(updated_team.id)
        if not exists:
            return None 

        # Save the updated team to Redis
        self.redis_client.set(updated_team.id, json.dumps(updated_team.to_dict()))
        # TODO Check if this is needed
        self.redis_client.sadd(teams_set, updated_team.id)

        return 