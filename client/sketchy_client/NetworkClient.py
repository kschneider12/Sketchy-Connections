from __future__ import annotations

import asyncio
from concurrent.futures import TimeoutError as FutureTimeoutError
from copy import deepcopy
import threading
from typing import Any
from urllib.parse import urljoin

import aiohttp

from sketchy_shared.types import PlayerRegistrationData


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
        self._loop: asyncio.AbstractEventLoop | None = None
        self._session: aiohttp.ClientSession | None = None

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
            raise NetworkClientError(f"Failed to start network client: {self._startup_error}") from self._startup_error

    def create_room(self, player_name: str) -> PlayerRegistrationData:
        """Create a room and register the caller as host."""

        return self._run_coroutine(self._create_room(player_name))

    def join_room(self, player_name: str, room_code: str) -> PlayerRegistrationData:
        """Join an existing room."""

        return self._run_coroutine(self._join_room(player_name, room_code))

    def get_registration(self) -> PlayerRegistrationData | None:
        """Return the most recent room registration"""

        if self._registration is None:
            return None
        return deepcopy(self._registration)

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

        self._shutdown_complete = True
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

    async def _create_room(self, player_name: str) -> PlayerRegistrationData:
        payload = await self._request_json(
            "POST",
            "/rooms",
            json_payload={"player_name": player_name},
        )
        self._registration = PlayerRegistrationData.from_dict(payload)
        return deepcopy(self._registration)

    async def _join_room(self, player_name: str, room_code: str) -> PlayerRegistrationData:
        payload = await self._request_json(
            "POST",
            f"/rooms/{room_code}",
            json_payload={"player_name": player_name}
        )
        self._registration = PlayerRegistrationData.from_dict(payload)
        return deepcopy(self._registration)


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
        except NetworkClientError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise NetworkClientError(f"Request failed: {exc}") from exc

    async def _read_json_or_text(self, response: aiohttp.ClientResponse) -> dict[str, Any] | str:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return await response.json()
        return await response.text()

    def _build_http_url(self, path: str) -> str:
        return urljoin(f"{self._base_url}/", path.lstrip("/"))

    def _require_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise NetworkClientError("HTTP session is not available.")
        return self._session
