from typing import Dict, List, Any
import asyncio


class Notifier:
    def __init__(self):
        self.connections: Dict[str, List[asyncio.Queue]] = {}

    async def connect(self, user_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        if user_id not in self.connections:
            self.connections[user_id] = []
        self.connections[user_id].append(queue)
        return queue

    def disconnect(self, user_id: str, queue: asyncio.Queue):
        if user_id in self.connections:
            self.connections[user_id].remove(queue)
            if not self.connections[user_id]:
                del self.connections[user_id]

    async def push(self, user_id: str, message: Any):
        """Push message to all SSE connections for this user."""
        if user_id in self.connections:
            for queue in list(self.connections[user_id]):
                await queue.put(message)


notifier = Notifier()
