import uuid

from typing import List, Optional
from dotenv import load_dotenv

from model.team import Team
from repository.team_repository import TeamRepository
from repository.player_repository import PlayerRepository
from .player_service import PlayerService, Player
from .errors import Error, ErrorType
from typing import Tuple

TEAM_SIZE = 5

class TeamService:
    def __init__(self):
        self.player_service = PlayerService()
        self.player_repoistory = PlayerRepository()
        self.team_repository = TeamRepository()

    def create_team(self, teamName, player_ids) -> Team:
        # Validations
        if len(player_ids) != TEAM_SIZE:
            raise Error(ErrorType.INVALID_PLAYER_COUNT, f"team must have {TEAM_SIZE} players")

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

    def leave_team(self, player_id) -> Optional[Player]:
        player = self.player_service.get_player(player_id)

        if player.teamId == None:
            return player

        team = self.team_repository.get_team(player.teamId)

        team.players = [p for p in team.players if p.id != player_id]
        player.teamId = None
        self.team_repository.save_team(team)
        self.player_repoistory.save_player(player)
        return player


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

    def generate_teams(self, team_size: int) -> List[Team]:
        # Validate input
        if team_size <= 0:
            raise Error(ErrorType.INVALID_TEAM_SIZE, "teamSize must be greater than 0")
        
        # Fetch players without a team
        all_players = [player for player in self.player_service.get_all_players() if player.teamId is None]

        # Validate enough players are available
        if len(all_players) < 2 * team_size:
            raise Error(ErrorType.NOT_ENOUGH_PLAYERS, f"Not enough players without teams. Need {2 * team_size}, found {len(all_players)}.")

        # Sort players by ELO in descending order
        sorted_players = sorted(all_players, key=lambda x: x.elo, reverse=True)

        # Distribute players into two teams
        team1_players, team2_players = self._distribute_players(sorted_players, team_size)

        # Create unique IDs for the teams
        team1_id = str(uuid.uuid4())
        team2_id = str(uuid.uuid4())

        # Assign team IDs to players
        for player in team1_players:
            player.teamId = team1_id
            self.player_service.update_player(player)

        for player in team2_players:
            player.teamId = team2_id
            self.player_service.update_player(player)

        # Create and save the teams
        team1 = Team(id=team1_id, teamName=str(uuid.uuid4()), players=team1_players)
        team2 = Team(id=team2_id, teamName=str(uuid.uuid4()), players=team2_players)

        self.team_repository.save_team(team1)
        self.team_repository.save_team(team2)

        return [team1, team2]

    def _distribute_players(self, players: List[Player], team_size: int) -> Tuple[List[Player], List[Player]]:
        team1 = []
        team2 = []
        n= team_size*2
        for i in range(team_size):
            if i % 2 == 0:  # Alternate between first and last positions
                team1.append(players[i])           # Team 1 gets i-th player
                team1.append(players[n - i - 1])   # and last-i-th player
            else:
                team2.append(players[i])           # Team 2 gets i-th player
                team2.append(players[n - i - 1])   # and last-i-th player
        if team_size % 2 ==1:
            team2.append(team1.pop())

        return team1, team2