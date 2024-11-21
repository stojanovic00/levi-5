from enum import Enum

class ErrorType(Enum):
    # PLAYER
    PLAYER_NOT_FOUND = "PLAYER_NOT_FOUND"
    NICKNAME_ALREADY_EXISTS = "NICKNAME_ALREADY_EXISTS"

    # TEAM
    INVALID_PLAYER_COUNT = "INVALID_PLAYER_COUNT"
    TEAM_NAME_ALREADY_EXISTS = "TEAM_NAME_ALREADY_EXISTS"
    PLAYER_ALREADY_IN_TEAM = "PLAYER_ALREADY_IN_TEAM"
    TEAM_NOT_FOUND = "TEAM_NOT_FOUND"

    # MATCH
    MATCH_DURATION_LESS_THAN_ONE = "MATCH_DURATION_LESS_THAN_ONE"
    MATCH_NOT_FOUND = "MATCH_NOT_FOUND"

class Error(Exception):
    def __init__(self, error_type: ErrorType, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(self.message)