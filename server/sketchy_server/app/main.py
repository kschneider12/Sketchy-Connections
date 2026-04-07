"""FastAPI application entrypoint for the Sketchy Connections backend.

This module exposes:
- HTTP endpoints for room creation, room lookup, and room membership.
- A WebSocket endpoint for real-time room state synchronization.

The server is authoritative for room and game state. Clients interact with the
HTTP API to create/join rooms, then keep a WebSocket open to receive room
updates and send gameplay actions.
"""

import asyncio
import time
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.logger import logging
from pydantic import BaseModel, ConfigDict, Field, field_validator

from sketchy_server.model import RoomManager
from sketchy_shared.types import PlayerRegistrationData


logger = logging.getLogger('uvicorn.error')

class PlayerRegistrationRequest(BaseModel):
    """Request body for creating a player or joining a room."""

    model_config = ConfigDict(extra="forbid")

    player_name: str = Field(min_length=1, max_length=32)

    @field_validator("player_name")
    @classmethod
    def validate_player_name(cls, value: str) -> str:
        """Ensures player name is not empty"""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Player name cannot be empty.")
        return stripped


class PlayerRegistrationResponse(BaseModel):
    """Serialized room join/create response returned to the client."""

    room_code: str
    player_id: str
    host_id: str
    websocket_path: str
    room: dict


class ServerRuntime:
    """Owns in-memory room state and active WebSocket connections.

    rooms: Authoritative in-memory room manager.
    connections: Mapping of room code -> player id -> live WebSocket.
    lock: Global async lock protecting room and connection mutations.
    """

    def __init__(self, *, room_prune_interval_seconds: int = 30, empty_room_ttl_seconds: int = 120):
        self.rooms = RoomManager()
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self.lock = asyncio.Lock()
        self.room_prune_interval_seconds = room_prune_interval_seconds
        self.empty_room_ttl_seconds = empty_room_ttl_seconds
        self._rooms_empty_since: dict[str, float] = {}

    def _remove_room_locked(self, room_code: str):
        """Delete a room and all associated runtime bookkeeping.

        Caller must hold ``self.lock``.
        """

        normalized_code = room_code.upper()
        self.connections.pop(normalized_code, None)
        self._rooms_empty_since.pop(normalized_code, None)
        self.rooms.remove_room(normalized_code)

    async def register_socket(self, room_code: str, player_id: str, websocket: WebSocket) -> str:
        """Register a player's WebSocket after validating room and player ids."""

        normalized_code = room_code.upper()
        async with self.lock:
            room = self.rooms.get_room(normalized_code)
            room.get_player(player_id)
            self.connections[room.room_id][player_id] = websocket
            self._rooms_empty_since.pop(room.room_id, None)
            return room.room_id

    async def unregister_socket(self, room_code: str, player_id: str):
        """Remove a player's WebSocket connection from the runtime registry."""

        async with self.lock:
            normalized_code = room_code.upper()
            room_connections = self.connections.get(normalized_code)
            if room_connections is None:
                return

            room_connections.pop(player_id, None)
            if not room_connections:
                self.connections.pop(normalized_code, None)

                if normalized_code in self.rooms.rooms:
                    self._rooms_empty_since.setdefault(normalized_code, time.monotonic())

    async def prune_empty_rooms(self) -> list[str]:
        """Remove rooms that have been without active sockets past the TTL."""

        now = time.monotonic()
        removed_rooms: list[str] = []

        async with self.lock:
            active_room_codes = set(self.rooms.rooms.keys())

            for room_code in list(self._rooms_empty_since):
                if room_code not in active_room_codes:
                    self._rooms_empty_since.pop(room_code, None)

            for room_code in active_room_codes:
                if self.connections.get(room_code):
                    self._rooms_empty_since.pop(room_code, None)
                    continue

                empty_since = self._rooms_empty_since.setdefault(room_code, now)
                if now - empty_since < self.empty_room_ttl_seconds:
                    continue

                self._remove_room_locked(room_code)
                removed_rooms.append(room_code)

        return removed_rooms

    async def send_room_state(self, room_code: str, player_id: str):
        """Send the latest room snapshot to a single connected player."""

        async with self.lock:
            room = self.rooms.get_room(room_code)
            websocket = self.connections.get(room.room_id, {}).get(player_id)
            if websocket is None:
                return
            payload = {"type": "room_state", "room": room.to_dict(player_id)}

        await websocket.send_json(payload)

    async def broadcast_room_state(self, room_code: str):
        """Broadcast the latest room snapshot to all connected players in a room.

        Any sockets that fail during send are treated as stale and removed from
        the connection registry.
        """

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


async def room_pruner():
    """Background task that periodically clears inactive empty rooms."""

    try:
        while True:
            await asyncio.sleep(runtime.room_prune_interval_seconds)
            removed_rooms = await runtime.prune_empty_rooms()
            if len(removed_rooms) > 0:
                logger.info(f"Pruned {len(removed_rooms)} inactive rooms")
    except asyncio.CancelledError:
        return


@app.on_event("startup")
async def startup():
    """Start background runtime maintenance tasks."""

    app.state.room_pruner_task = asyncio.create_task(room_pruner())


@app.on_event("shutdown")
async def shutdown():
    """Stop background runtime maintenance tasks."""

    room_pruner_task = getattr(app.state, "room_pruner_task", None)
    if room_pruner_task is None:
        return

    room_pruner_task.cancel()
    try:
        await room_pruner_task
    except asyncio.CancelledError:
        pass


def to_http_exception(exc: ValueError) -> HTTPException:
    """Translate domain-level validation errors into HTTP responses."""

    if "not found" in str(exc).lower():
        status_code = status.HTTP_404_NOT_FOUND
    elif "unauthorized" in str(exc).lower():
        status_code = status.HTTP_401_UNAUTHORIZED
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return HTTPException(status_code=status_code, detail=str(exc))


def build_registration_response(room, player_id: str) -> PlayerRegistrationResponse:
    """Build the standard room registration payload for create/join endpoints."""

    registration = PlayerRegistrationData(
        room_code=room.room_id,
        player_id=player_id,
        host_id=room.host_id,
        websocket_path=f"/ws/{room.room_id}/{player_id}",
        room=room.to_data(player_id),
    )

    return PlayerRegistrationResponse(
        room_code=registration.room_code,
        player_id=registration.player_id,
        host_id=registration.host_id,
        websocket_path=registration.websocket_path,
        room=registration.room.to_dict(),
    )


def validate_entry_content(content):
    """Validate websocket submission payloads for prompt/drawing content."""

    if isinstance(content, str):
        stripped = content.strip()
        if not stripped:
            raise ValueError("Entry content cannot be empty.")
        return stripped

    if isinstance(content, list):
        return content

    raise ValueError("Entry content must be a string or a list.")


async def handle_client_message(
        room_code: str,
        player_id: str,
        websocket: WebSocket,
        message: dict
):
    """Dispatch a single client WebSocket message.

    Supported message types:
    - ``sync``: send the caller the latest room state.
    - ``start_game``: ask the host to move the room from lobby to playing.
    - ``submit_entry``: submit a prompt/guess/drawing payload for the round.
    - ``leave_room``: remove the player from the room and close the socket.

    Returns:
        ``True`` if the caller should stop reading from the socket because the
        connection has been intentionally closed, otherwise ``False``.
    """

    if not isinstance(message, dict):
        raise ValueError("WebSocket messages must be JSON objects.")

    message_type = message.get("type")

    if websocket.client:
        client = websocket.client
        logger.info(f"{client.host}:{client.port} - \"WebSocket {websocket.url.path}\" [{message_type}]")

    if message_type == "sync":
        await runtime.send_room_state(room_code, player_id)
        return False

    if message_type == "start_game":
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.start_game(player_id)
            logger.info(f"Game started: {room.to_dict()}")
        await runtime.broadcast_room_state(room_code)
        return False

    if message_type == "submit_entry":
        content = validate_entry_content(message.get("content"))
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.submit_entry(player_id, content)
            assert room.game is not None
        await runtime.broadcast_room_state(room_code)
        return False

    if message_type == "incr_book":
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.book_idx += 1

        await runtime.broadcast_room_state(room_code)
        return False

    if message_type == "set_options":
        draw_time = int(message.get("draw_time"))
        prompt_time = int(message.get("prompt_time"))
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.draw_time = draw_time
            room.prompt_time = prompt_time

        await runtime.broadcast_room_state(room_code)
        return False

    if message_type == "leave_room":
        should_broadcast = False
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            room.remove_player(player_id)

            room_connections = runtime.connections.get(room.room_id, {})
            room_connections.pop(player_id, None)
            if not room.players or len(room.players) == 0:
                room_id = room.room_id
                runtime._remove_room_locked(room_id)
            else:
                should_broadcast = True

        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
        if should_broadcast:
            await runtime.broadcast_room_state(room_code)
        return True

    raise ValueError(f"Unsupported message type: {message_type}")


@app.get("/")
async def root():
    """Return a lightweight index of backend capabilities."""

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
    """Basic liveness endpoint for local checks and container health probes."""

    return {"ok": True}


@app.post("/rooms", response_model=PlayerRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_room(request: PlayerRegistrationRequest):
    """Create a new room and register the requesting player as the host."""

    async with runtime.lock:
        room, host = runtime.rooms.create_room(request.player_name)
        response = build_registration_response(room, host.id)

    return response

@app.post("/rooms/{room_code}/end", status_code=status.HTTP_200_OK)
async def delete_room(room_code: str, player_id: str | None = Query(default=None)):
    """Delete a room by code.

    Only the host can delete a room
    """

    async with runtime.lock:
        if runtime.rooms.get_room(room_code).host_id == player_id:
            runtime._remove_room_locked(room_code)
        else:
            raise to_http_exception(ValueError("unauthorized"))

    return {"detail": f"Room {room_code} removed"}

@app.post("/rooms/{room_code}/players", response_model=PlayerRegistrationResponse)
async def join_room(room_code: str, request: PlayerRegistrationRequest):
    """Join an existing room and return the caller's initial room snapshot."""

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
    """Fetch the latest room snapshot over HTTP.

    The optional ``player_id`` tailors the embedded game payload so the caller
    can receive player-specific state such as the current prompt.
    """

    try:
        async with runtime.lock:
            room = runtime.rooms.get_room(room_code)
            payload = room.to_dict(player_id)
    except ValueError as exc:
        raise to_http_exception(exc) from exc

    return payload


@app.websocket("/ws/{room_code}/{player_id}")
async def room_socket(websocket: WebSocket, room_code: str, player_id: str):
    """Handle a live room WebSocket session for a single player.

    On connect, the server validates the room/player pair, registers the socket,
    and immediately broadcasts the updated room state. Thereafter the socket is
    used for real-time actions and room updates until the client disconnects or
    explicitly leaves the room.
    """

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
                should_stop = await handle_client_message(
                    normalized_code,
                    player_id,
                    websocket,
                    message
                )
                if should_stop:
                    break
            except ValueError as exc:
                await websocket.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        await runtime.unregister_socket(normalized_code, player_id)
    finally:
        await runtime.unregister_socket(normalized_code, player_id)
