import unittest
from service.match_service import MatchService, WIN, LOSS, DRAW
from model.team import Team
from model.player import Player

class TestStatistics(unittest.TestCase):
    def setUp(self):
        self.match_service = MatchService()

    def test_calculate_mean_team_elo(self):
        # Arrange
        players = [
                    Player(id='player1', nickname='Player1', elo=50),
                    Player(id='player2', nickname='Player2', elo=60),
                    Player(id='player3', nickname='Player3', elo=70),
                    Player(id='player4', nickname='Player4', elo=80),
                    Player(id='player5', nickname='Player5', elo=90)
                ]
        team = Team(id='b909d79d-04d3-442d-9b43-29b2a44cc628', teamName='Team1', players=players)

        # Act
        mean_elo = self.match_service.calculate_mean_team_elo(team)

        # Assert
        self.assertEqual(mean_elo, 70)

    def test_get_estimated_elo(self):
        # Arrange & Act
        estimated_elo = self.match_service.get_estimated_elo(current_elo=25, opponent_team_mean_elo=10)
        # Assert
        self.assertAlmostEqual(estimated_elo, 0.521573, places=6)

    def test_get_new_elo_win(self):
        # Arrange & Act
        new_elo = self.match_service.get_new_elo(current_elo=25,estimated_elo=0.521573, ratingAdjustment=30, match_result=WIN)
        # Assert
        self.assertAlmostEqual(new_elo, 39.35, places=2)

    def test_get_new_elo_loss(self):
        # Arrange & Act
        new_elo = self.match_service.get_new_elo(current_elo=25,estimated_elo=0.521573, ratingAdjustment=30, match_result=LOSS)
        # Assert
        self.assertAlmostEqual(new_elo, 9.35, places=2)

    def test_get_new_elo_draw(self):
        # Arrange & Act
        new_elo = self.match_service.get_new_elo(current_elo=25,estimated_elo=0.521573, ratingAdjustment=30, match_result=DRAW)
        # Assert
        self.assertAlmostEqual(new_elo, 24.35, places=2)

    def test_calculate_rating_adjustment(self):
        self.assertEqual(self.match_service.calculate_rating_adjustment(100), 50)
        self.assertEqual(self.match_service.calculate_rating_adjustment(499), 50)
        self.assertEqual(self.match_service.calculate_rating_adjustment(500), 40)
        self.assertEqual(self.match_service.calculate_rating_adjustment(600), 40)
        self.assertEqual(self.match_service.calculate_rating_adjustment(999), 40)
        self.assertEqual(self.match_service.calculate_rating_adjustment(1000), 30)
        self.assertEqual(self.match_service.calculate_rating_adjustment(1500), 30)
        self.assertEqual(self.match_service.calculate_rating_adjustment(2999), 30)
        self.assertEqual(self.match_service.calculate_rating_adjustment(3000), 20)
        self.assertEqual(self.match_service.calculate_rating_adjustment(3500), 20)
        self.assertEqual(self.match_service.calculate_rating_adjustment(4999), 20)
        self.assertEqual(self.match_service.calculate_rating_adjustment(5000), 10)
        self.assertEqual(self.match_service.calculate_rating_adjustment(6000), 10)

if __name__ == '__main__':
    unittest.main()