from collections.abc import Awaitable, Callable
from types import CoroutineType
from typing import Any, final

from websockets.asyncio.client import ClientConnection, connect


class BrokerClient:

    url: str
    name: str
    args: dict[str, Any] | None

    client: ClientConnection

    def __init__(
        self,
        url: str,
        name: str,
        args: dict[str, Any] | None,
    ) -> None:
        self.url = url
        self.name = name
        self.args = args

    async def connect(self):
        pass

    async def onListen(self):
        pass

    async def close(self):
        pass
