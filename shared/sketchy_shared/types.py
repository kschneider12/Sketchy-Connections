from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoomPhase(str, Enum):
    LOBBY = "lobby"
    PLAYING = "playing"
    RESULTS = "results"


class GamePhase(str, Enum):
    WRITING = "writing"
    DRAWING = "drawing"
    GUESSING = "guessing"


class EntryType(str, Enum):
    DRAWING = "drawing"
    PROMPT = "prompt"


@dataclass(slots=True)
class PlayerData:
    id: str = ""
    name: str = ""
    has_submitted: bool = False
    is_host: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "has_submitted": self.has_submitted,
            "is_host": self.is_host,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlayerData":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            has_submitted=bool(data.get("has_submitted", False)),
            is_host=bool(data.get("is_host", False)),
        )


@dataclass(slots=True)
class EntryData:
    author_id: str
    type: EntryType
    content: str | list[Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "author_id": self.author_id,
            "type": self.type.value,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntryData":
        return cls(
            author_id=str(data["author_id"]),
            type=EntryType(data["type"]),
            content=data["content"],
        )


@dataclass(slots=True)
class BookData:
    owner_id: str
    entries: list[EntryData] = field(default_factory=list)

    @property
    def next_entry_type(self) -> EntryType:
        if len(self.entries) == 0:
            return EntryType.PROMPT

        last = self.entries[-1].type
        if last is EntryType.DRAWING:
            return EntryType.PROMPT
        return EntryType.DRAWING

    @property
    def last_entry(self) -> EntryData | None:
        if len(self.entries) == 0:
            return None
        return self.entries[-1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "owner_id": self.owner_id,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BookData":
        return cls(
            owner_id=str(data["owner_id"]),
            entries=[EntryData.from_dict(entry) for entry in data.get("entries", [])],
        )


@dataclass(slots=True)
class GameStateData:
    phase: GamePhase
    round_number: int
    current_prompt: EntryData | None = None
    expected_entry_type: EntryType | None = None
    books: list[BookData] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "phase": self.phase.value,
            "round_number": self.round_number,
            "current_prompt": self.current_prompt.to_dict() if self.current_prompt else None,
            "expected_entry_type": self.expected_entry_type.value if self.expected_entry_type else None,
        }

        if self.books is not None:
            payload["books"] = [book.to_dict() for book in self.books]

        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameStateData":
        current_prompt = data.get("current_prompt")
        expected_entry_type = data.get("expected_entry_type")
        books = data.get("books")

        return cls(
            phase=GamePhase(data["phase"]),
            round_number=int(data["round_number"]),
            current_prompt=EntryData.from_dict(current_prompt) if isinstance(current_prompt, dict) else None,
            expected_entry_type=EntryType(expected_entry_type) if expected_entry_type else None,
            books=[BookData.from_dict(book) for book in books] if isinstance(books, list) else None,
        )


@dataclass(slots=True)
class RoomData:
    room_id: str = ""
    phase: RoomPhase = RoomPhase.LOBBY
    host_id: str = ""
    players: list[PlayerData] = field(default_factory=list)
    game: GameStateData | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "phase": self.phase.value,
            "host_id": self.host_id,
            "players": [player.to_dict() for player in self.players],
            "game": self.game.to_dict() if self.game is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RoomData":
        game = data.get("game")
        return cls(
            room_id=str(data["room_id"]),
            phase=RoomPhase(data["phase"]),
            host_id=str(data["host_id"]),
            players=[PlayerData.from_dict(player) for player in data.get("players", [])],
            game=GameStateData.from_dict(game) if isinstance(game, dict) else None,
        )


@dataclass(slots=True)
class PlayerRegistrationData:
    room_code: str
    player_id: str
    host_id: str
    websocket_path: str
    room: RoomData

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_code": self.room_code,
            "player_id": self.player_id,
            "host_id": self.host_id,
            "websocket_path": self.websocket_path,
            "room": self.room.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlayerRegistrationData":
        return cls(
            room_code=str(data["room_code"]),
            player_id=str(data["player_id"]),
            host_id=str(data["host_id"]),
            websocket_path=str(data["websocket_path"]),
            room=RoomData.from_dict(data["room"]),
        )
