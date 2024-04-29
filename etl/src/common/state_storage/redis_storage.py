import logging
import redis.asyncio as redis
from types import TracebackType
from typing import Any, Final, Optional, Type
from typing_extensions import Self

from common.state_storage.base_storage import BaseStorage


class RedisStorage(BaseStorage):
    STATE_KEY: Final[str] = "state"

    def __init__(self, redis_url: str) -> None:
        self._logger = logging.getLogger(__name__)
        self._redis_url = redis_url
        self._redis = None

    async def __aenter__(self) -> Self:
        self._logger.debug("Trying to connect to redis db...")
        self._redis = await redis.from_url(self._redis_url)
        await self._redis.ping()
        self._logger.debug("Connected to redis db successfully.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._logger.debug("closing connection to Redis")
        await self._redis.close()
        self._redis = None
        self._logger.debug("connection to Redis closed.")

    async def save_state(self, state: dict[str, Any]) -> None:
        """Save state in storage"""

        self._logger.debug("saving state: %s to Redis", state)
        await self._redis.hset(self.STATE_KEY, mapping=state)
        self._logger.debug("state saved successfully.")

    async def retrieve_state(self) -> dict[str, Any]:
        """Get state from storage"""

        self._logger.debug("Retrieving '%s' state from Redis...", self.STATE_KEY)
        state = await self._redis.hgetall(self.STATE_KEY)
        self._logger.debug("Retrieved '%s' state successfully. State: <%s>", self.STATE_KEY, state)
        return state