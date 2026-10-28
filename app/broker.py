import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator


class InMemoryBroker:
    """Single-process pub/sub. Each subscriber gets its own bounded queue.

    If a subscriber falls behind, its oldest message is dropped, so one slow
    client can never block the feed.
    """

    def __init__(self, max_queue: int = 1000) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[str]]] = defaultdict(set)
        self._max_queue = max_queue

    async def publish(self, channel: str, message: str) -> None:
        for queue in list(self._subscribers[channel]):
            if queue.full():
                queue.get_nowait()  # drop the oldest message
            queue.put_nowait(message)

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=self._max_queue)
        self._subscribers[channel].add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._subscribers[channel].discard(queue)

    def subscriber_count(self, channel: str) -> int:
        return len(self._subscribers[channel])

    async def close(self) -> None:
        self._subscribers.clear()