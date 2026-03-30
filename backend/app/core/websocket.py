import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.core.redis import get_redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._pubsub_task: asyncio.Task | None = None

    async def connect(self, session_code: str, websocket: WebSocket):
        await websocket.accept()
        if session_code not in self.active_connections:
            self.active_connections[session_code] = set()
        self.active_connections[session_code].add(websocket)

    def disconnect(self, session_code: str, websocket: WebSocket):
        if session_code in self.active_connections:
            self.active_connections[session_code].remove(websocket)
            if not self.active_connections[session_code]:
                del self.active_connections[session_code]

    async def broadcast(self, session_code: str, message: dict):
        # We broadcast locally to all connections for this session
        if session_code in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[session_code]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)
            
            for dead in dead_connections:
                self.disconnect(session_code, dead)

    async def pubsub_listener(self):
        """Listens to Redis for broadcast events from other instances."""
        redis = get_redis()
        if not redis:
            print("Redis not available, pubsub listener skipped.")
            return

        pubsub = redis.pubsub()
        await pubsub.subscribe("session_updates")
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    session_code = data.get("session_code")
                    payload = data.get("payload")
                    if session_code and payload:
                        await self.broadcast(session_code, payload)
        except Exception as e:
            print(f"PubSub listener error: {e}")
        finally:
            await pubsub.unsubscribe("session_updates")

    async def trigger_update(self, session_code: str, update_type: str, data: dict = None):
        """Triggers an update by publishing to Redis AND broadcasting locally."""
        # Broadcast locally for the current instance
        payload = {
            "type": update_type,
            "data": data or {}
        }
        await self.broadcast(session_code, payload)

        # Publish to Redis for other instances
        redis = get_redis()
        if redis:
            message = {
                "session_code": session_code,
                "payload": payload
            }
            try:
                await redis.publish("session_updates", json.dumps(message))
            except Exception as e:
                print(f"Redis publish error: {e}")

manager = ConnectionManager()
