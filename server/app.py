import random
import string
import threading

from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

from model import Room


app = Flask(__name__)

rooms: dict[str, Room] = {}
rooms_lock = threading.RLock()


def _new_room_id(length: int = 4) -> str:
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(100):
        candidate = "".join(random.choice(alphabet) for _ in range(length))
        with rooms_lock:
            if candidate not in rooms:
                return candidate
    abort(500, "Could not create room id.")


def _require_json() -> dict:
    if not request.is_json:
        abort(400, "Expected JSON body.")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400, "Bad JSON body.")
    return payload


def _require_str(payload: dict, key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        abort(400, f"'{key}' is required.")
    return value.strip()


def _serialize_room(room: Room) -> dict:
    return {
        "roomId": room.room_id,
        "hostId": room.host_id,
        "players": [{"id": p.id, "name": p.name} for p in room.players],
    }


@app.errorhandler(HTTPException)
def _handle_http_error(err: HTTPException):
    return jsonify({"error": err.description}), err.code


@app.get("/")
def index():
    return jsonify(
        {
            "service": "Sketchy Connections (barebones rooms)",
            "routes": [
                "POST /rooms",
                "POST /rooms/<room_id>/join",
                "POST /rooms/<room_id>/leave",
            ],
        }
    )


@app.post("/rooms")
def create_room():
    payload = _require_json()
    host_name = _require_str(payload, "hostName")
    custom_id = payload.get("roomId")
    room_id = _new_room_id()
    if isinstance(custom_id, str) and custom_id.strip():
        room_id = custom_id.strip().upper()

    with rooms_lock:
        if room_id in rooms:
            abort(409, "Room id already exists.")
        room = Room(room_id, host_name)
        rooms[room_id] = room

    return jsonify({"room": _serialize_room(room), "playerId": room.host_id}), 201


@app.post("/rooms/<room_id>/join")
def join_room(room_id: str):
    payload = _require_json()
    player_name = _require_str(payload, "name")
    room_id = room_id.upper()

    with rooms_lock:
        room = rooms.get(room_id)
        if room is None:
            abort(404, "Room not found.")
        try:
            player = room.add_player(player_name)
        except ValueError as exc:
            abort(400, str(exc))

    return jsonify({"room": _serialize_room(room), "playerId": player.id})


@app.post("/rooms/<room_id>/leave")
def leave_room(room_id: str):
    payload = _require_json()
    player_id = _require_str(payload, "playerId")
    room_id = room_id.upper()

    with rooms_lock:
        room = rooms.get(room_id)
        if room is None:
            abort(404, "Room not found.")

        player_exists = any(p.id == player_id for p in room.players)
        if not player_exists:
            abort(404, "Player not found in room.")

        room.remove_player(player_id)

        if len(room.players) == 0:
            rooms.pop(room_id, None)
            return jsonify({"roomId": room_id, "deleted": True})

        if room.host_id == player_id:
            room.host_id = room.players[0].id

    return jsonify({"room": _serialize_room(room), "deleted": False})


