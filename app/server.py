from flask import Flask, make_response, request, jsonify
from service.player_service import PlayerService
from service.team_service import Error, ErrorType, TeamService
from service.match_service import MatchService

app = Flask(__name__)
player_service = PlayerService()
team_service = TeamService()
match_service = MatchService()

# PLAYERS

@app.route('/players/create', methods=['POST'])
def create_player():
    request_data = request.get_json()

    try:
        new_player = player_service.create_player(request_data['nickname'])
        return jsonify(new_player.to_dict()), 200
    except Error as e:
        if e.error_type == ErrorType.NICKNAME_ALREADY_EXISTS:
            return jsonify({'message': e.message}), 409
        else:
            return jsonify({'message': "Unknown error"}), 520

@app.route('/players/<player_id>', methods=['GET'])
def get_player(player_id):

    try:
        player = player_service.get_player(player_id)
        return jsonify(player.to_dict()), 200
    except Error as e:
        if e.error_type == ErrorType.PLAYER_NOT_FOUND:
            return jsonify({'message': e.message}), 404
        else:
            return jsonify({'message': "Unknown error"}), 520

@app.route('/players', methods=['GET'])
def get_all_players():
    players = player_service.get_all_players()
    return jsonify([player.to_dict() for player in players]), 200


# TEAMS

@app.route('/teams', methods=['POST'])
def create_team():
    request_data = request.get_json()

    try:
        new_team = team_service.create_team(request_data['teamName'], request_data['players'])
        return jsonify(new_team.to_dict()), 200
    except Error as e:
        if e.error_type == ErrorType.INVALID_PLAYER_COUNT:
            return jsonify({'message': e.message}), 400
        elif e.error_type == ErrorType.PLAYER_NOT_FOUND:
            return jsonify({'message': e.message}), 404
        elif e.error_type == ErrorType.TEAM_NAME_ALREADY_EXISTS:
            return jsonify({'message': e.message}), 409
        elif e.error_type == ErrorType.PLAYER_ALREADY_IN_TEAM:
            return jsonify({'message': e.message}), 409
        else:
            return jsonify({'message': "Unknown error"}), 520

@app.route('/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    try:
        team = team_service.get_team(team_id)
        return jsonify(team.to_dict()), 200
    except Error as e:
        if e.error_type == ErrorType.TEAM_NOT_FOUND:
            return jsonify({'message': e.message}), 404
        else:
            return jsonify({'message': "Unknown error"}), 520

@app.route('/teams', methods=['GET'])
def get_all_teams():
    teams = team_service.get_all_teams()
    return jsonify([team.to_dict() for team in teams]), 200

# MATCHES

@app.route('/matches', methods=['POST'])
def record_match():
    request_data = request.get_json()

    try:
        match_service.record_match(request_data['team1Id'], request_data['team2Id'], request_data['winningTeamId'], request_data['duration'])
        return make_response('', 200)
    except Error as e:
        if e.error_type == ErrorType.MATCH_DURATION_LESS_THAN_ONE:
            return jsonify({'message': e.message}), 400
        if e.error_type == ErrorType.TEAM_NOT_FOUND:
            return jsonify({'message': e.message}), 404
        else:
            return jsonify({'message': "Unknown error"}), 520

@app.route('/matches/<match_id>', methods=['GET'])
def get_match(match_id):

    try:
        match = match_service.get_match(match_id)
        return jsonify(match.to_dict()), 200
    except Error as e:
        if e.error_type == ErrorType.MATCH_NOT_FOUND:
            return jsonify({'message': e.message}), 404
        else:
            return jsonify({'message': "Unknown error"}), 520

@app.route('/matches', methods=['GET'])
def get_all_matches():
    matches = match_service.get_all_matches()
    return jsonify([match.to_dict() for match in matches]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)