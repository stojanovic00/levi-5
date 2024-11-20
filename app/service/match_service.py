import redis
import json
import os
import uuid
from dotenv import load_dotenv
from typing import Optional, Tuple
from .team_service import TeamService
from .player_service import PlayerService

# Load environment variables from .env file
# TODO maybe delete
load_dotenv()

team_service = TeamService()
player_service = PlayerService()

class MatchService:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)

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
            return False


        team1 = team_service.get_team(team1Id)
        team2 = team_service.get_team(team2Id)

        team1_mean_elo = team_service.calculate_mean_elo(team1)
        team2_mean_elo = team_service.calculate_mean_elo(team2)

        if team1 is None or team2 is None:
            return False
            
        # Updaing the players stats
        # check when K is calulcated before or after adding hours

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

            player_service.update_player(player)

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

            player_service.update_player(player)
        

        team_service.update_team(team1)
        team_service.update_team(team2)

        return True