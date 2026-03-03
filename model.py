from dataclasses import dataclass, field
from enum import Enum


class RoomPhase(Enum):
    LOBBY = "lobby"
    PLAYING = "playing"
    RESULTS = "results"


class GamePhase(Enum):
    WRITING = "writing"
    DRAWING = "drawing"
    GUESSING = "guessing"


class EntryType(Enum):
    DRAWING = "drawing"
    PROMPT = "prompt"


@dataclass
class Entry:
    author_id: str
    type: EntryType
    content: str | list


@dataclass
class Book:
    owner_id: str
    entries: list[Entry] = field(default_factory=list)

    @property
    def next_entry_type(self) -> EntryType:
        if len(self.entries) == 0:
            return EntryType.PROMPT
        last = self.entries[-1].type
        if last is EntryType.DRAWING:
            return EntryType.PROMPT
        else:
            return EntryType.DRAWING

    @property
    def last_entry(self) -> Entry | None:
        if len(self.entries) == 0:
            return None
        else:
            return self.entries[-1]


@dataclass
class Player:
    id: str
    name: str
    has_submitted: bool = False


class GameState:
    def __init__(self, players: list[Player]):
        self.players: list[Player] = players
        self.books: list[Book] = [Book(owner_id=p.id) for p in players]
        self.phase: GamePhase = GamePhase.WRITING
        self.round_number: int = 1
        self.assignments: list[int] = list(range(len(players)))

    def submit_entry(self, player_id: str, content: str | list):
        player_index = self._get_player_index(player_id)
        player = self.players[player_index]

        if player.has_submitted:
            raise ValueError(f"Player {player_id} has already submitted this round.")

        # takes the players index l oznvoisdnvooks at its assignment and then pulls
        # the book that it is in the index of the books
        book = self.books[self.assignments[player_index]]
        entry = Entry(author_id=player_id, type=book.next_entry_type, content=content)
        book.entries.append(entry)
        player.has_submitted = True

    def all_submitted(self) -> bool:
        return all(p.has_submitted for p in self.players)

    def next_round(self) -> bool:
        self.round_number += 1

        if self.round_number > len(self.players):
            return True

        if self.round_number % 2 == 0:
            self.phase = GamePhase.DRAWING
        else:
            self.phase = GamePhase.GUESSING

        self._rotate_books()
        return False

    def get_current_prompt(self, player_id: str) -> Entry | None:
        # getting player index so we can find book assignment
        player_index = self._get_player_index(player_id)
        # getting book assignment and returning the last entry for it
        book = self.books[self.assignments[player_index]]
        return book.last_entry

    def get_all_books_for_results(self) -> list[Book]:
        # returning entire list of books
        return self.books

    def get_player_name(self, player_id: str) -> str:
        for player in self.players:
            if player.id == player_id:
                return player.name
        raise ValueError(f"Player {player_id} not found.")

    def _rotate_books(self):
        n = len(self.players)
        self.assignments = [(i + self.round_number - 1) % n for i in range(n)]
        for player in self.players:
            player.has_submitted = False

    def _get_player_index(self, player_id: str) -> int:
        for i, p in enumerate(self.players):
            if p.id == player_id:
                return i
        raise ValueError(f"Player {player_id} not found.")


class Room:
    def __init__(self, room_code: str, host_name: str):
        self._player_counter = 0
        self.room_id: str = room_code
        self.game: GameState | None = None
        self.phase: RoomPhase = RoomPhase.LOBBY
        self.players: list[Player] = []

        host = self._create_player(host_name)
        self.host_id: str = host.id

    def add_player(self, name: str) -> Player:
        if self.phase != RoomPhase.LOBBY:
            raise ValueError("Cannot join a game already in progress.")
        return self._create_player(name)

    def remove_player(self, player_id: str):
        self.players = [p for p in self.players if p.id != player_id]

    def start_game(self, request_id: str):
        if request_id != self.host_id:
            raise ValueError("Only the host can start the game.")
        if self.phase != RoomPhase.LOBBY:
            raise ValueError("Game has already started.")
        if len(self.players) <= 2:
            raise ValueError("Need at least 2 players to start.")

        self.game = GameState(self.players)
        self.phase = RoomPhase.PLAYING

    def submit_entry(self, player_id: str, content: str | list):
        if self.phase != RoomPhase.PLAYING:
            raise ValueError("Game is not in progress.")

        self.game.submit_entry(player_id, content)

        if self.game.all_submitted():
            game_over = self.game.next_round()
            if game_over:
                self.phase = RoomPhase.RESULTS

    def _create_player(self, name: str):
        self._player_counter += 1
        player = Player(id=str(self._player_counter), name=name)
        self.players.append(player)
        return player
