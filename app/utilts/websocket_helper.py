
from fastapi import WebSocket
from typing import List


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def broadcast(self, message: dict):
#         for connection in self.active_connections:
#             await connection.send_json(message)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        print("📢 Broadcast called")
        print("Connections:", len(self.active_connections))
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                print("📤 SENT TO CLIENT")
            except Exception:
                print("❌ SEND FAILED:")
                disconnected.append(connection)

        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()