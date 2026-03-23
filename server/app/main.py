import asyncio
from collections import defaultdict
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ConfigDict, Field, field_validator


from model import RoomManager


class PlayerRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_name: str = Field(min_length=1, max_length=32)

    @field_validator("player_name")
    @classmethod
    def validate_player_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Player name cannot be empty.")
        return stripped


class PlayerRegistrationResponse(BaseModel):
    room_code: str
    player_id: str
    host_id: str
    websocket_path: str
    room: dict


class ServerRuntime:
    def __init__(self):
        self.rooms = RoomManager()
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self.lock = asyncio.Lock()

    async def register_socket(self, room_code: str, player_id: str, websocket: WebSocket) -> str:
        normalized_code = room_code.upper()
        async with self.lock:
            room = self.rooms.get_room(normalized_code)
            room.get_player(player_id)
            self.connections[room.room_id][player_id] = websocket
            return room.room_id

    async def unregister_socket(self, room_code: str, player_id: str):
        async with self.lock:
            normalized_code = room_code.upper()
            room_connections = self.connections.get(normalized_code)
            if room_connections is None:
                return

            room_connections.pop(player_id, None)
            if not room_connections:
                self.connections.pop(normalized_code, None)

    async def send_room_state(self, room_code: str, player_id: str):
        async with self.lock:
            room = self.rooms.get_room(room_code)
            websocket = self.connections.get(room.room_id, {}).get(player_id)
            if websocket is None:
                return
            payload = {"type": "room_state", "room": room.to_dict(player_id)}

        await websocket.send_json(payload)

    async def broadcast_room_state(self, room_code: str):
        async with self.lock:
            room = self.rooms.get_room(room_code)
            sockets = list(self.connections.get(room.room_id, {}).items())
            payloads = [
                (player_id, websocket, {"type": "room_state", "room": room.to_dict(player_id)})
                for player_id, websocket in sockets
            ]

        stale_players: list[str] = []
        for player_id, websocket, payload in payloads:
            try:
                await websocket.send_json(payload)
            except Exception:
                stale_players.append(player_id)

        for stale_player_id in stale_players:
            await self.unregister_socket(room_code, stale_player_id)


runtime = ServerRuntime()
app = FastAPI(title="Sketchy Connections API")


def to_http_exception(exc: ValueError) -> HTTPException:
    status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=status_code, detail=str(exc))


def build_registration_response(room, player_id: str) -> PlayerRegistrationResponse:
    return PlayerRegistrationResponse(
        room_code=room.room_id,
        player_id=player_id,
        host_id=room.host_id,
        websocket_path=f"/ws/{room.room_id}/{player_id}",
        room=room.to_dict(player_id),
    )


def validate_entry_content(content):
    if isinstance(content, str):
        stripped = content.strip()
        if not stripped:
            raise ValueError("Entry content cannot be empty.")
        return stripped

    if isinstance(content, list):
        return content

    raise ValueError("Entry content must be a string or a list.")


async def handle_client_message(room_code: str, player_id: str, websocket: WebSocket, message: dict):
    if not isinstance(message, dict):
        raise ValueError("WebSocket messages must be JSON objects.")

    message_type = message.get("type")

    if message_type == "sync":
        await runtime.send_room_state(room_code, player_id)
        return False

    if message_type == "start_game":
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.start_game(player_id)
        await runtime.broadcast_room_state(room_code)
        return False

    if message_type == "submit_entry":
        content = validate_entry_content(message.get("content"))
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.submit_entry(player_id, content)
        await runtime.broadcast_room_state(room_code)
        return False

    if message_type == "leave_room":
        should_broadcast = False
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.remove_player(player_id)

            room_connections = runtime.connections.get(room.room_id, {})
            room_connections.pop(player_id, None)
            if not room.players:
                runtime.connections.pop(room.room_id, None)
                runtime.rooms.remove_room(room.room_id)
            else:
                should_broadcast = True

        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
        if should_broadcast:
            await runtime.broadcast_room_state(room_code)
        return True

    raise ValueError(f"Unsupported message type: {message_type}")


@app.get("/")
async def root():
    return {
        "message": "Sketchy Connections backend",
        "http_endpoints": [
            "POST /rooms",
            "POST /rooms/{room_code}/players",
            "GET /rooms/{room_code}",
            "POST /rooms/{room_code}/end"
        ],
        "websocket_endpoint": "/ws/{room_code}/{player_id}",
    }


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/rooms", response_model=PlayerRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_room(request: PlayerRegistrationRequest):
    async with runtime.lock:
        room, host = runtime.rooms.create_room(request.player_name)
        response = build_registration_response(room, host.id)

    return response

@app.post("/rooms/{room_code}/end", status_code=status.HTTP_200_OK)
async def delete_room(room_code: str):
    async with runtime.lock:
        runtime.rooms.remove_room(room_code)

    return {"detail": f"Room {room_code} removed"}

@app.post("/rooms/{room_code}/players", response_model=PlayerRegistrationResponse)
async def join_room(room_code: str, request: PlayerRegistrationRequest):
    try:
        async with runtime.lock:
            room, player = runtime.rooms.join_room(room_code, request.player_name)
            response = build_registration_response(room, player.id)
    except ValueError as exc:
        raise to_http_exception(exc) from exc

    await runtime.broadcast_room_state(response.room_code)
    return response


@app.get("/rooms/{room_code}")
async def get_room(room_code: str, player_id: str | None = Query(default=None)):
    try:
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            payload = room.to_dict(player_id)
    except ValueError as exc:
        raise to_http_exception(exc) from exc

    return payload


@app.websocket("/ws/{room_code}/{player_id}")
async def room_socket(websocket: WebSocket, room_code: str, player_id: str):
    await websocket.accept()

    try:
        normalized_code = await runtime.register_socket(room_code, player_id, websocket)
    except ValueError as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await runtime.broadcast_room_state(normalized_code)

    try:
        while True:
            message = await websocket.receive_json()
            try:
                should_stop = await handle_client_message(normalized_code, player_id, websocket, message)
                if should_stop:
                    break
            except ValueError as exc:
                await websocket.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        await runtime.unregister_socket(normalized_code, player_id)
    finally:
        await runtime.unregister_socket(normalized_code, player_id)
