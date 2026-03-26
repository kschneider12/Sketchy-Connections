import random
import string

from sketchy_shared.types import (
    BookData,
    EntryData,
    EntryType,
    GamePhase,
    GameStateData,
    PlayerData,
    RoomData,
    RoomPhase,
)


class GameState:
    def __init__(self, players: list[PlayerData]):
        self.players: list[PlayerData] = players
        self.books: list[BookData] = [BookData(owner_id=player.id) for player in players]
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
        entry = EntryData(author_id=player_id, type=book.next_entry_type, content=content)
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

    def get_current_prompt(self, player_id: str) -> EntryData | None:
        # getting player index so we can find book assignment
        player_index = self._get_player_index(player_id)
        # getting book assignment and returning the last entry for it
        book = self.books[self.assignments[player_index]]
        return book.last_entry

    def get_expected_entry_type(self, player_id: str) -> EntryType:
        player_index = self._get_player_index(player_id)
        book = self.books[self.assignments[player_index]]
        return book.next_entry_type

    def get_all_books_for_results(self) -> list[BookData]:
        # returning entire list of books
        return self.books

    def get_player_name(self, player_id: str) -> str:
        for player in self.players:
            if player.id == player_id:
                return player.name
        raise ValueError(f"Player {player_id} not found.")

    def to_data(self, player_id: str | None = None, *, include_books: bool = False) -> GameStateData:
        current_prompt = (
            self.get_current_prompt(player_id)
            if player_id is not None
            else None
        )
        expected_entry_type = (
            self.get_expected_entry_type(player_id)
            if player_id is not None
            else None
        )

        return GameStateData(
            phase=self.phase,
            round_number=self.round_number,
            current_prompt=current_prompt,
            expected_entry_type=expected_entry_type,
            books=self.books.copy() if include_books else None,
        )

    def to_dict(self, player_id: str | None = None, *, include_books: bool = False) -> dict:
        return self.to_data(player_id=player_id, include_books=include_books).to_dict()

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
        self.players: list[PlayerData] = []

        host = self._create_player(host_name)
        self.host_id: str = host.id

    def add_player(self, name: str) -> PlayerData:
        if self.phase != RoomPhase.LOBBY:
            raise ValueError("Cannot join a game already in progress.")
        return self._create_player(name)

    def remove_player(self, player_id: str):
        if self.phase == RoomPhase.PLAYING:
            raise ValueError("Cannot remove a player while a game is in progress.")

        self.get_player(player_id)
        self.players = [p for p in self.players if p.id != player_id]

        if self.players and player_id == self.host_id:
            self.host_id = self.players[0].id

    def start_game(self, request_id: str):
        if request_id != self.host_id:
            raise ValueError("Only the host can start the game.")
        if self.phase != RoomPhase.LOBBY:
            raise ValueError("Game has already started.")
        #if len(self.players) <= 2:
            #raise ValueError("Need at least 3 players to start.")

        self.game = GameState(self.players)
        self.phase = RoomPhase.PLAYING

    def submit_entry(self, player_id: str, content: str | list):
        assert self.game is not None
        if self.phase != RoomPhase.PLAYING:
            raise ValueError("Game is not in progress.")

        self.game.submit_entry(player_id, content)

        if self.game.all_submitted():
            game_over = self.game.next_round()
            if game_over:
                self.phase = RoomPhase.RESULTS

    def get_player(self, player_id: str) -> PlayerData:
        for player in self.players:
            if player.id == player_id:
                return player
        raise ValueError(f"Player {player_id} not found.")

    def to_data(self, player_id: str | None = None) -> RoomData:
        players = [
            PlayerData(
                id=player.id,
                name=player.name,
                has_submitted=player.has_submitted,
                is_host=player.id == self.host_id,
            )
            for player in self.players
        ]

        game = None
        if self.game is not None:
            game = self.game.to_data(
                player_id=player_id,
                include_books=self.phase == RoomPhase.RESULTS,
            )

        return RoomData(
            room_id=self.room_id,
            phase=self.phase,
            host_id=self.host_id,
            players=players,
            game=game,
        )

    def to_dict(self, player_id: str | None = None) -> dict:
        return self.to_data(player_id=player_id).to_dict()

    def _create_player(self, name: str):
        self._player_counter += 1
        player = PlayerData(id=str(self._player_counter), name=name)
        self.players.append(player)
        return player


class RoomManager:
    def __init__(self):
        self.rooms: dict[str, Room] = {}

    def create_room(self, host_name: str) -> tuple[Room, PlayerData]:
        room_code = self._generate_room_code()
        room = Room(room_code, host_name)
        self.rooms[room_code] = room
        return room, room.get_player(room.host_id)

    def get_room(self, room_code: str) -> Room:
        normalized_code = room_code.upper()
        room = self.rooms.get(normalized_code)
        if room is None:
            raise ValueError(f"Room {normalized_code} not found.")
        return room

    def join_room(self, room_code: str, player_name: str) -> tuple[Room, PlayerData]:
        room = self.get_room(room_code)
        player = room.add_player(player_name)
        return room, player

    def remove_room(self, room_code: str):
        self.rooms.pop(room_code.upper(), None)

    def _generate_room_code(self, length: int = 4) -> str:
        alphabet = string.ascii_uppercase + string.digits

        while True:
            room_code = "".join(random.choices(alphabet, k=length))
            if room_code not in self.rooms:
                return room_code
