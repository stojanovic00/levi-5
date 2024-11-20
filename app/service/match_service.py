from dotenv import load_dotenv
from typing import Optional, Tuple
from .team_service import TeamService
from .player_service import PlayerService
from .errors import Error, ErrorType



class MatchService:
    def __init__(self):
        self.team_service = TeamService()
        self.player_service = PlayerService()

    def get_estimated_elo(self, current_elo: float, opponent_team_mean_elo: float) -> float:
           return 1 / (1 + 10 ** ((opponent_team_mean_elo - current_elo) / 400)) 

    def get_new_elo(self, current_elo: float, estimated_elo: float, ratingAdjustment: int, match_result: float) -> float:
          return current_elo + ratingAdjustment * (match_result - estimated_elo) 

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


        team1 = self.team_service.get_team(team1Id)
        team2 = self.team_service.get_team(team2Id)

        if team1 is None:
            raise Error(ErrorType.TEAM_NOT_FOUND, "Team 1 not found")
        if team2 is None:
            raise Error(ErrorType.TEAM_NOT_FOUND, "Team 2 not found")

        team1_mean_elo = self.team_service.calculate_mean_elo(team1)
        team2_mean_elo = self.team_service.calculate_mean_elo(team2)

            
        for player in team1.players:
            # ELO
            estimated_elo = self.get_estimated_elo(player.elo, team2_mean_elo)
            player.ratingAdjustment = self.calculate_rating_adjustment(player.hoursPlayed)

            # Hours
            player.hoursPlayed += duration

            # Wins, Losses, ELO
            if winningTeamId == team1Id:
                player.wins += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, 1)
            elif winningTeamId != None:
                player.losses += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, 0)
            else:
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, 0.5)

            self.player_service.update_player(player)

        for player in team2.players:
            # ELO
            estimated_elo = self.get_estimated_elo(player.elo, team1_mean_elo)
            player.ratingAdjustment = self.calculate_rating_adjustment(player.hoursPlayed)

            # Hours
            player.hoursPlayed += duration

            # Wins, Losses, ELO
            if winningTeamId == team2Id:
                player.wins += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, 1)
            elif winningTeamId != None:
                player.losses += 1
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, 0)
            else:
                player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, 0.5)

            self.player_service.update_player(player)
        

        self.team_service.update_team(team1)
        self.team_service.update_team(team2)

        return