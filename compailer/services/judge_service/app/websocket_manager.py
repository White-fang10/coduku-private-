from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_leaderboard_subs: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, client_id: str, user_id: str):
        """Register WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"✅ WebSocket connected: {client_id} (user: {user_id})")
    
    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Unregister WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"❌ WebSocket disconnected: {user_id}")
    
    async def broadcast_submission_result(self, submission_data: dict):
        """Broadcast submission result to all connected clients"""
        message = json.dumps({
            "type": "submission_result",
            "data": submission_data
        })
        
        # Broadcast to all users watching leaderboard
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def broadcast_leaderboard_update(self, leaderboard_data: dict):
        """Broadcast leaderboard updates in real-time"""
        message = json.dumps({
            "type": "leaderboard_update",
            "data": leaderboard_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            msg_json = json.dumps(message)
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(msg_json)
                except:
                    pass

manager = ConnectionManager()
