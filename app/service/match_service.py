import uuid
from dotenv import load_dotenv
from typing import List, Optional, Tuple

from model.team import Team
from model.match import Match
from .team_service import TeamService
from .player_service import PlayerService
from repository.match_repository import MatchRepository
from .errors import Error, ErrorType


TEAM_SIZE = 5
# Constants for match results
WIN = 1.0
LOSS = 0.0
DRAW = 0.5

class MatchService:
    def __init__(self):
        self.team_service = TeamService()
        self.player_service = PlayerService()
        self.match_repository = MatchRepository()

    def calculate_mean_team_elo(self, team: Team) -> float:
        total_elo = 0
        for player in team.players:
            total_elo += player.elo
        return total_elo / 5

    def get_estimated_elo(self, current_elo: float, opponent_team_mean_elo: float) -> float:
           return float(1 / (1 + 10 ** ((opponent_team_mean_elo - current_elo) / 400)))

    def get_new_elo(self, current_elo: float, estimated_elo: float, ratingAdjustment: int, match_result: float) -> float:
        if ratingAdjustment is None:
                ratingAdjustment = 50
        current_elo = float(current_elo)
        estimated_elo = float(estimated_elo)
        ratingAdjustment = float(ratingAdjustment)
        match_result = float(match_result)
        return current_elo + (ratingAdjustment * (match_result - estimated_elo))
    def calculate_rating_adjustment(self, hours: int) -> int:
        if hours < 500:
            return 50
        elif 500 <= hours < 1000:
            return 40
        elif 1000 <= hours < 3000:
            return 30
        elif 3000 <= hours < 5000:
            return 20
        else:
            return 10

    def record_match(self, team1Id: str, team2Id: str, winningTeamId: str | None, duration: int):

        if duration < 1:
            raise Error(ErrorType.MATCH_DURATION_LESS_THAN_ONE, "Duration can't be less than 1 hour")

        if team1Id == team2Id:
            raise Error(ErrorType.SAME_TEAM_ID, "Teams must be different")
        
        if winningTeamId != None and winningTeamId != team1Id and winningTeamId != team2Id:
            raise Error(ErrorType.WINNER_NOT_STATED, "Winning team must be one of the teams playing")
        
        team1 = self.team_service.get_team(team1Id)
        team2 = self.team_service.get_team(team2Id)

        if team1 is None:
            raise Error(ErrorType.TEAM_NOT_FOUND, "Team 1 not found")
        if team2 is None:
            raise Error(ErrorType.TEAM_NOT_FOUND, "Team 2 not found")

        if len(team1.players) != len(team2.players) or len(team1.players) == 0:
            raise Error(
            ErrorType.INVALID_TEAM_SIZE,
            "Both teams must have the same number of players, and the number must be greater than 0"
        )
        team1_mean_elo = self.calculate_mean_team_elo(team1)
        team2_mean_elo = self.calculate_mean_team_elo(team2)

   
        for player in team1.players:
            # ELO
            estimated_elo = self.get_estimated_elo(player.elo, team2_mean_elo)
            # Hours
            player.hoursPlayed += duration

            # Wins, Losses, ELO, Rating Adjustment
            if winningTeamId == team1Id:
                player.wins += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, WIN)
            elif winningTeamId != None:
                player.losses += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, LOSS)
            else:
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, DRAW)

            # Rating Adjustment recaluclation after added hours
            player.ratingAdjustment = self.calculate_rating_adjustment(player.hoursPlayed)
            self.player_service.update_player(player)

        for player in team2.players:
            # ELO
            estimated_elo = self.get_estimated_elo(player.elo, team1_mean_elo)

            # Hours
            player.hoursPlayed += duration

            # Wins, Losses, ELO, Rating Adjustment
            if winningTeamId == team2Id:
                player.wins += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, WIN)
            elif winningTeamId != None:
                player.losses += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, LOSS)
            else:
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, DRAW)

            # Rating Adjustment recaluclation after added hours
            player.ratingAdjustment = self.calculate_rating_adjustment(player.hoursPlayed)
            self.player_service.update_player(player)
        

        self.team_service.update_team(team1)
        self.team_service.update_team(team2)

        # Save match to database
        self.match_repository.save_match(Match(str(uuid.uuid4()), team1Id, team2Id, winningTeamId, duration))
        
        return

    def get_match(self, match_id):
        match = self.match_repository.get_match(match_id)
        if match:
            return match
        raise Error(ErrorType.MATCH_NOT_FOUND, f"match with ID '{match_id}' not found")

    def get_all_matches(self) -> List[Match]:
        return self.match_repository.get_all_matches()
