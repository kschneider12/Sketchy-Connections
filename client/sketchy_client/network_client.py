from __future__ import annotations

import asyncio
from concurrent.futures import TimeoutError as FutureTimeoutError
import threading
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import aiohttp

from shared.sketchy_shared.types import PlayerRegistrationData, RoomData, PlayerData


class NetworkClientError(RuntimeError):
    """Raised when the lightweight HTTP client cannot reach the backend."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class NetworkClient:
    """Async event driven loop.

    Events can be registered to the internal loop, and processed concurrently when possible.
    ``_run_coroutine`` registers an event to be triggered
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000", *, request_timeout: float = 10.0):
        self._base_url = base_url.rstrip("/")
        self._request_timeout = request_timeout

        self._registration: PlayerRegistrationData | None = None
        self.player: PlayerData = PlayerData()
        self.room: RoomData = RoomData()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._session: aiohttp.ClientSession | None = None
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._listener_task : asyncio.Task[None] | None = None

        self._startup_error: Exception | None = None
        self._ready = threading.Event()
        self._shutdown_complete = False
        self._closed = False

        self._thread = threading.Thread(
            target=self._run_loop,
            name="NetworkClientLoop",
            daemon=True,
        )
        self._thread.start()
        self._ready.wait()

        if self._startup_error is not None:
            raise NetworkClientError(
                f"Failed to start network client: {self._startup_error}"
            ) from self._startup_error

    def create_room(self, player_name: str) -> None:
        """Create a room and register the caller as host."""

        return self._run_coroutine(self._create_room(player_name))

    def join_room(self, player_name: str, room_code: str) -> None:
        """Join an existing room."""

        return self._run_coroutine(self._join_room(player_name, room_code))

    def start_game(self) -> None:
        "Start the game"

        return self._run_coroutine(self._start_game())

    def close(self):
        """Close the underlying aiohttp session and stop the worker loop."""

        if self._closed:
            return

        if self._loop is not None and self._loop.is_running():
            try:
                self._run_coroutine(self._async_shutdown(), timeout=5)
            finally:
                self._loop.call_soon_threadsafe(self._loop.stop)
                self._thread.join(timeout=5)

        self._closed = True

    def __enter__(self) -> "NetworkClient":
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _run_loop(self):
        """Start main eventloop.

        This will run until notified to shut_down
        """
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._async_start())
        except Exception as exc:
            self._startup_error = exc
            self._ready.set()
            loop.close()
            return

        self._ready.set()

        try:
            loop.run_forever()
        finally:
            if not self._shutdown_complete:
                loop.run_until_complete(self._async_shutdown())
            loop.close()

    async def _async_start(self):
        timeout = aiohttp.ClientTimeout(total=self._request_timeout)
        self._session = aiohttp.ClientSession(timeout=timeout)

    async def _async_shutdown(self):
        if self._shutdown_complete:
            return

        if self._listener_task is not None:
            self._listener_task.cancel()

        self._shutdown_complete = True
        await self._close_websocket()
        if self._session is not None and not self._session.closed:
            await self._session.close()

    def _run_coroutine(self, coroutine, *, timeout: float | None = None):
        if self._closed:
            raise NetworkClientError("Network client is already closed.")
        if self._loop is None:
            raise NetworkClientError("Network client loop is not available.")
        if threading.current_thread() is self._thread:
            raise NetworkClientError("Network client methods cannot be called from its internal event loop thread.")

        # Submit the ccoroutine to the loop
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)

        try:
            return future.result(timeout=timeout or self._request_timeout)
        except FutureTimeoutError as exc:
            future.cancel()
            raise NetworkClientError("Network operation timed out.") from exc



    async def _create_room(self, player_name: str) -> None:
        payload = await self._request_json(
            "POST",
            "/rooms",
            json_payload={"player_name": player_name},
        )
        registration = PlayerRegistrationData.from_dict(payload)

        await self._connect_websocket(registration.websocket_path)
        await self._start_websocket_listener()

        self._registration = registration
        self.room = self._registration.room
        self.player.name = player_name
        self.player.id = self._registration.player_id
        self.player.is_host = True

    async def _join_room(self, player_name: str, room_code: str) -> None:
        payload = await self._request_json(
            "POST",
            f"/rooms/{room_code}/players",
            json_payload={"player_name": player_name}
        )
        registration = PlayerRegistrationData.from_dict(payload)

        await self._connect_websocket(registration.websocket_path)
        await self._start_websocket_listener()

        self._registration = registration
        self.room = self._registration.room
        self.player.name = player_name
        self.player.id = self._registration.player_id
        self.player.is_host = False


    async def _start_game(self) -> None:
        await self._send_message({"type": "start_game"})

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        session = self._require_session()
        url = self._build_http_url(path)

        try:
            async with session.request(method, url, json=json_payload) as response:
                payload = await self._read_json_or_text(response)

                if response.status >= 400:
                    detail = payload.get("detail") if isinstance(payload, dict) else str(payload)
                    raise NetworkClientError(
                        detail or f"HTTP {response.status}",
                        status_code=response.status,
                        payload=payload if isinstance(payload, dict) else {"detail": str(payload)},
                    )

                if not isinstance(payload, dict):
                    raise NetworkClientError("Expected a JSON object response from the server.")

                return payload
        except (aiohttp.ClientError, asyncio.TimeoutError, NetworkClientError) as exc:
            raise NetworkClientError(f"Request failed: {exc}") from exc

    async def _read_json_or_text(self, response: aiohttp.ClientResponse) -> dict[str, Any] | str:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return await response.json()
        return await response.text()

    def _build_http_url(self, path: str) -> str:
        return urljoin(f"{self._base_url}/", path.lstrip("/"))

    def _build_websocket_url(self, path: str) -> str:
        http_url = self._build_http_url(path)
        parsed = urlparse(http_url)
        websocket_scheme = "wss" if parsed.scheme == "https" else "ws"
        return urlunparse(parsed._replace(scheme=websocket_scheme))

    async def _connect_websocket(self, websocket_path: str) -> None:
        session = self._require_session()
        await self._close_websocket()
        websocket_url = self._build_websocket_url(websocket_path)

        try:
            self._websocket = await session.ws_connect(websocket_url)
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise NetworkClientError(f"WebSocket connection failed: {exc}") from exc

    async def _listen_to_websocket(self) -> None:
        websocket = self._require_websocket()

        try:
            async for message in websocket:
                if message.type is aiohttp.WSMsgType.TEXT:
                    payload = message.json()
                    if not isinstance(payload, dict):
                        continue

                    message_type = payload.get("type")
                    if message_type == "room_state":
                        room_payload = payload.get("room")
                        if not isinstance(room_payload, dict):
                            continue

                        room = RoomData.from_dict(room_payload)
                        self.room = room
                        if self._registration is not None:
                            self._registration.room = room
                        continue

                    if message_type == "error":
                        error_message = payload.get("message", "Server sent a websocket error.")
                        raise NetworkClientError(str(error_message))

                if message.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    break

                if message.type is aiohttp.WSMsgType.ERROR:
                    raise NetworkClientError("WebSocket listener encountered an error.")
        finally:
            if self._websocket is websocket and websocket.closed:
                self._websocket = None

    async def _close_websocket(self) -> None:
        if self._websocket is None:
            return

        websocket = self._websocket
        self._websocket = None

        if not websocket.closed:
            await websocket.close()

    async def _send_message(self, data: Any) -> None:
        websocket = self._require_websocket()
        try:
            await websocket.send_json(data)
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            await self._stop_websocket_listener()
            raise NetworkClientError(f"Failed to send websocket data: {exc}") from exc

    async def _stop_websocket_listener(self) -> None:
        listener_task = getattr(self, "_listener_task", None)
        if listener_task is None:
            return

        self._listener_task = None
        listener_task.cancel()

        try:
            await listener_task
        except asyncio.CancelledError:
            pass

    async def _start_websocket_listener(self) -> None:
        await self._stop_websocket_listener()

        self._listener_task = asyncio.create_task(self._listen_to_websocket())

        await self._send_message({"type": "sync"})

    def _require_websocket(self) -> aiohttp.ClientWebSocketResponse:
        if self._websocket is None or self._websocket.closed:
            raise NetworkClientError("WebSocket connection is not available.")
        return self._websocket

    def _require_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise NetworkClientError("HTTP session is not available.")
        return self._session
