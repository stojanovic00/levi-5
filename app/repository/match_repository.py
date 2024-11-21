import redis
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from model.match import Match

# Load environment variables from .env file
load_dotenv()

class MatchRepository:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.matches_set = "matches"

    def save_match(self, new_match: Match):
        self.redis_client.set(new_match.id, json.dumps(new_match.__dict__))
        self.redis_client.sadd(self.matches_set, new_match.id)

    def get_match(self, match_id: str) -> Optional[Match]:
        match_data = self.redis_client.get(match_id)
        if match_data:
            match_dict = json.loads(match_data)
            return Match.from_dict(match_dict)
        return None

    def get_all_matches(self) -> List[Match]:
        matches = []
        for key in self.redis_client.smembers(self.matches_set):
            match = self.get_match(key)
            if match:
                matches.append(match)
        return matches