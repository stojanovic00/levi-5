import uuid
from dotenv import load_dotenv
from typing import List, Optional

from model.team import Team
from model.match import Match
from .team_service import TeamService
from .player_service import PlayerService
from repository.match_repository import MatchRepository
from .errors import Error, ErrorType

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
        """Calculate the mean Elo of a team."""
        if not team.players:
            raise Error(ErrorType.INVALID_TEAM_SIZE, "Team must have players")
        return sum(player.elo for player in team.players) / len(team.players)

    def get_estimated_elo(self, current_elo: float, opponent_mean_elo: float) -> float:
        """Calculate the expected Elo score for a player."""
        return 1 / (1 + 10 ** ((opponent_mean_elo - current_elo) / 400))

    def calculate_rating_adjustment(self, hours: int) -> int:
        """Determine the K-factor (rating adjustment) based on hours played."""
        if hours < 500:
            return 50
        elif hours < 1000:
            return 40
        elif hours < 3000:
            return 30
        elif hours < 5000:
            return 20
        else:
            return 10

    def get_new_elo(self, current_elo: float, estimated_elo: float, rating_adjustment: int, match_result: float) -> float:
        """Calculate the new Elo for a player."""
        new_elo = float(current_elo) + float(rating_adjustment) * (float(match_result) - float(estimated_elo))
        return new_elo

    def record_match(self, team1Id: str, team2Id: str, winningTeamId: Optional[str], duration: int):
        """Record a match and update players' statistics."""
        if duration < 1:
            raise Error(ErrorType.MATCH_DURATION_LESS_THAN_ONE, "Match duration must be at least 1 hour")

        if team1Id == team2Id:
            raise Error(ErrorType.SAME_TEAM_ID, "Teams must be different")

        if winningTeamId not in [team1Id, team2Id, None]:
            raise Error(ErrorType.WINNER_NOT_STATED, "Winning team must be one of the teams or the match must be a draw")

        # Fetch teams
        team1 = self.team_service.get_team(team1Id)
        team2 = self.team_service.get_team(team2Id)

        if not team1:
            raise Error(ErrorType.TEAM_NOT_FOUND, "Team 1 not found")
        if not team2:
            raise Error(ErrorType.TEAM_NOT_FOUND, "Team 2 not found")

        if len(team1.players) != len(team2.players) or len(team1.players) == 0:
            raise Error(ErrorType.INVALID_TEAM_SIZE, "Both teams must have the same number of players and be non-empty")

        # Calculate mean Elo for teams
        team1_mean_elo = self.calculate_mean_team_elo(team1)
        team2_mean_elo = self.calculate_mean_team_elo(team2)

        # Update players in both teams
        for player in team1.players:
            self.update_player_stats(player, team2_mean_elo, winningTeamId == team1Id, winningTeamId is None, duration)

        for player in team2.players:
            self.update_player_stats(player, team1_mean_elo, winningTeamId == team2Id, winningTeamId is None, duration)

        # Save teams and match
        self.team_service.update_team(team1)
        self.team_service.update_team(team2)
        match = Match(str(uuid.uuid4()), team1Id, team2Id, winningTeamId, duration)
        self.match_repository.save_match(match)

    def update_player_stats(self, player, opponent_mean_elo, is_winner, is_draw, duration):
        """Update individual player's statistics."""
        estimated_elo = self.get_estimated_elo(player.elo, opponent_mean_elo)
        player.hoursPlayed += duration
        player.ratingAdjustment = self.calculate_rating_adjustment(player.hoursPlayed)

        if is_winner:
            player.wins += 1
            match_result = WIN
        elif is_draw:
            match_result = DRAW  # This handles the case when it's a draw
        else:
            player.losses += 1
            match_result = LOSS

        player.elo = self.get_new_elo(player.elo, estimated_elo, player.ratingAdjustment, match_result)
        self.player_service.update_player(player)


    def get_match(self, match_id: str) -> Match:
        """Retrieve a match by its ID."""
        match = self.match_repository.get_match(match_id)
        if not match:
            raise Error(ErrorType.MATCH_NOT_FOUND, f"Match with ID '{match_id}' not found")
        return match

    def get_all_matches(self) -> List[Match]:
        """Retrieve all recorded matches."""
        return self.match_repository.get_all_matches()
