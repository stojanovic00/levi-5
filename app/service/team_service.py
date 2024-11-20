import uuid

from typing import List, Optional
from dotenv import load_dotenv

from model.team import Team
from repository.team_repository import TeamRepository
from .player_service import PlayerService, Player
from .errors import Error, ErrorType

class TeamService:
    def __init__(self):
        self.player_service = PlayerService()
        self.team_repository = TeamRepository()

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

        self.team_repository.save_team(new_team)
        return new_team

    def get_team(self, team_id) -> Optional[Team]:
        team = self.team_repository.get_team(team_id)
        if team:
            return team
        raise Error(ErrorType.TEAM_NOT_FOUND, "team with ID '{team_id}' not found".format(team_id=team_id))

    def get_all_teams(self) -> List[Team]:
        return self.team_repository.get_all_teams()
    

    def update_team(self, updated_team: Team):
        exists = self.team_repository.get_team(updated_team.id)
        if not exists:
            raise Error(ErrorType.TEAM_NOT_FOUND, "team with ID '{team_id}' not found".format(team_id=updated_team.id))

        self.team_repository.save_team(updated_team)
        return 