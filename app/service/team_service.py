import redis
import json
import os
import uuid

from typing import List, Optional
from dotenv import load_dotenv

from .player_service import PlayerService, Player
from .errors import Error, ErrorType
from model.team import Team

teams_set = "teams"
# Load environment variables from .env file
load_dotenv()

class TeamService:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.player_service = PlayerService()

    def create_team(self, teamName, player_ids) -> Team:
        # Validations
        if len(player_ids) != 5:
            raise Error(ErrorType.INVALID_PLAYER_COUNT, "team must have 5 players")

        for team in self.get_all_teams():
            if team.teamName == teamName:
                raise Error(ErrorType.TEAM_NAME_ALREADY_EXISTS, f"team with name '{team.teamName}' already exists")


        team_id = str(uuid.uuid4())
        # Find all players by their IDs and add them to the team
        players: List[Player] = []
        for player_id in player_ids:
            player = self.player_service.get_player(player_id)
            if player:
                if player.teamId:
                    raise Error(ErrorType.PLAYER_ALREADY_IN_TEAM, "player with ID '{player_id}' is already in a team".format(player_id=player_id))

                player.teamId = team_id 
                self.player_service.update_player(player)
                players.append(player)
            else:
                raise Error(ErrorType.PLAYER_NOT_FOUND, "player with ID '{player_id}' not found".format(player_id=player_id))

        # Create a new team
        new_team = Team(
            id=team_id,
            teamName=teamName,
            players=players
        )

        # Save the team to Redis
        self.redis_client.set(new_team.id, json.dumps(new_team.to_dict()))
        self.redis_client.sadd(teams_set, new_team.id)

        return new_team

    def get_team(self, team_id) -> Optional[Team]:
        team_data = self.redis_client.get(team_id)
        if team_data:
            team_dict = json.loads(team_data)
            return Team.from_dict(team_dict)
        raise Error(ErrorType.TEAM_NOT_FOUND, "team with ID '{team_id}' not found".format(team_id=team_id))

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
        exists = self.get_team(updated_team.id)
        if not exists:
            raise Error(ErrorType.TEAM_NOT_FOUND, "team with ID '{team_id}' not found".format(team_id=updated_team.id))

        # Save the updated team to Redis
        self.redis_client.set(updated_team.id, json.dumps(updated_team.to_dict()))
        # TODO Check if this is needed
        self.redis_client.sadd(teams_set, updated_team.id)

        return 