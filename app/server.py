from flask import Flask, request, jsonify
from model.player import Player
import redis
import uuid
import json

redis_client = redis.Redis(host='localhost', port=6379)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
    

@app.route('/players/create', methods=['POST'])
def create_player():
    request_data = request.get_json()
    new_player = Player(
        id=str(uuid.uuid4()),
        nickname=request_data['nickname'],
        wins=0,
        losses=0,
        elo=0,
        hoursPlayed=0,
        team=None,
        ratingAdjustment=None,
    )

    redis_client.set(new_player.id, json.dumps(new_player.__dict__))

    return jsonify(new_player.__dict__), 201

@app.route('/players/<player_id>', methods=['GET'])
def get_player(player_id):
    player_data = redis_client.get(player_id)
    if player_data:
        player_dict = json.loads(player_data)
        return jsonify(player_dict), 200
    else:
        return jsonify({'message': 'Player not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=8080)