from .match_notifier_function import invoke_match_notifier
from .match_saver_function import invoke_match_saver


match_saver_event_payload = {
    "match_results": "Team A vs Team B - Winner: Team A - Duration: 90 minutes"
}

match_notifier_event_payload = {"match_details": "Team A vs Team B - Winner: Team A"}


invoke_match_saver(match_saver_event_payload)
invoke_match_notifier(match_notifier_event_payload)
