from flask import Flask, request, jsonify
from service.player_service import PlayerService

app = Flask(__name__)
player_service = PlayerService()


@app.route('/players/create', methods=['POST'])
def create_player():
    request_data = request.get_json()
    new_player = player_service.create_player(request_data['nickname'])

    if new_player:
        return jsonify(new_player.__dict__), 201
    else:
        return jsonify({'message': 'Nickname already exists'}), 409



@app.route('/players/<player_id>', methods=['GET'])
def get_player(player_id):
    player = player_service.get_player(player_id)
    if player:
        return jsonify(player.__dict__), 200
    else:
        return jsonify({'message': 'Player not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=8080)