"""
API Gateway — WebSocket Endpoint
Provides real-time updates to the frontend via WebSocket connections.
Consumes fraud alerts from RabbitMQ and pushes them to connected clients.
"""

import asyncio
import json
import logging
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

# Connected WebSocket clients
connected_clients: Set[WebSocket] = set()


async def broadcast_message(message: dict) -> None:
    """Broadcast a message to all connected WebSocket clients."""
    if not connected_clients:
        return

    dead_clients = set()
    json_message = json.dumps(message, default=str)

    for client in connected_clients:
        try:
            await client.send_text(json_message)
        except Exception:
            dead_clients.add(client)

    # Clean up disconnected clients
    connected_clients.difference_update(dead_clients)


@router.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    """WebSocket endpoint for real-time transaction and fraud alert updates.

    Clients connect here to receive:
    - New transaction notifications
    - Fraud alert notifications
    - Transaction status updates
    """
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"🔌 WebSocket client connected. Total: {len(connected_clients)}")

    try:
        while True:
            # Keep connection alive; also accept client messages if needed
            data = await websocket.receive_text()
            # Client can send commands like {"type": "ping"}
            if data:
                try:
                    parsed = json.loads(data)
                    if parsed.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except json.JSONDecodeError:
                    pass
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        logger.info(f"🔌 WebSocket client disconnected. Total: {len(connected_clients)}")
