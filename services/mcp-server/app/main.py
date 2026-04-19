"""
MCP Server — Main Entry Point
Starts the MCP server with SSE transport for network access.
"""

import asyncio
import logging

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.server import mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# SSE transport
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    """Handle SSE connections from MCP clients."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


async def handle_health(request: Request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "mcp-server",
        "version": "1.0.0",
    })


async def startup():
    """Application startup."""
    logger.info("🚀 Starting MCP Server...")
    await init_db()
    await init_redis()
    logger.info("✅ MCP Server is ready")


async def shutdown():
    """Application shutdown."""
    logger.info("🛑 Shutting down MCP Server...")
    await close_redis()
    await close_db()


# Starlette app with SSE transport
app = Starlette(
    debug=True,
    routes=[
        Route("/health", handle_health),
        Route("/sse", handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.mcp_host,
        port=settings.mcp_port,
        reload=False,
    )
