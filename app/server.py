import json
from flask import Flask, make_response, request, jsonify
from service.player_service import PlayerService
from service.team_service import TeamErrorType, TeamService
from service.match_service import MatchService

app = Flask(__name__)
player_service = PlayerService()
team_service = TeamService()
match_service = MatchService()

# PLAYERS

@app.route('/players/create', methods=['POST'])
def create_player():
    request_data = request.get_json()
    new_player = player_service.create_player(request_data['nickname'])

    if new_player:
        return jsonify(new_player.to_dict()), 200
    else:
        return jsonify({'message': 'Nickname already exists'}), 409

@app.route('/players/<player_id>', methods=['GET'])
def get_player(player_id):
    player = player_service.get_player(player_id)
    if player:
        return jsonify(player.to_dict()), 200
    else:
        return jsonify({'message': 'Player not found'}), 404

@app.route('/players', methods=['GET'])
def get_all_players():
    players = player_service.get_all_players()
    return jsonify([player.to_dict() for player in players]), 200


# TEAMS

@app.route('/teams', methods=['POST'])
def create_team():
    request_data = request.get_json()
    team_name = request_data['teamName']
    player_ids = request_data['players']

    new_team, err_type = team_service.create_team(team_name, player_ids)
    if new_team:
        return jsonify(new_team.to_dict()), 200
    else:
        if err_type == TeamErrorType.INVALID_PLAYER_COUNT:
            return jsonify({'message': err_type.value}), 400 
        elif err_type == TeamErrorType.TEAM_NAME_ALREADY_EXISTS or err_type == TeamErrorType.PLAYER_ALREADY_IN_TEAM:
            return jsonify({'message': err_type.value}), 409
        elif err_type == TeamErrorType.PLAYER_NOT_FOUND:
            return jsonify({'message': err_type.value}), 404
        else:
            return jsonify({'message': "Unknown error"}), 400

@app.route('/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    team = team_service.get_team(team_id)
    if team:
        return jsonify(team.to_dict()), 200
    else:
        return jsonify({'message': 'Team not found'}), 404

@app.route('/teams', methods=['GET'])
def get_all_teams():
    teams = team_service.get_all_teams()
    return jsonify([team.to_dict() for team in teams]), 200

# MATCHES

@app.route('/matches', methods=['POST'])
def record_match():
    request_data = request.get_json()
    succ = match_service.record_match(request_data['team1Id'], request_data['team2Id'], request_data['winningTeamId'], request_data['duration'])
    if succ:
        return make_response('', 200)
    else:
        return jsonify({'message': 'Error recording match'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)