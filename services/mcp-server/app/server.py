"""
MCP Server — Server Definition & Tool Registration
Defines the MCP server with tools for AI agents to query fraud data.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from app.core.database import get_session, init_db
from app.core.redis import init_redis, get_redis

logger = logging.getLogger(__name__)

# Create MCP Server instance
mcp_server = Server("fraud-detection-mcp")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Register available MCP tools."""
    return [
        Tool(
            name="get_recent_frauds",
            description=(
                "Get recent fraud alerts from the e-commerce fraud detection platform. "
                "Returns a list of fraud alerts with details including user ID, "
                "transaction amount, location, risk level, and violated rules."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 24)",
                        "default": 24,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of alerts to return (default: 20)",
                        "default": 20,
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "Filter by risk level: low, medium, high, critical",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                },
            },
        ),
        Tool(
            name="check_user_status",
            description=(
                "Check the risk status and transaction history of a specific user "
                "in the fraud detection platform. Returns risk level, total transactions, "
                "fraud flags, recent activity, and last known location."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The external user ID to check (e.g., 'user_42')",
                    },
                },
                "required": ["user_id"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls from AI agents."""
    if name == "get_recent_frauds":
        return await _get_recent_frauds(arguments)
    elif name == "check_user_status":
        return await _check_user_status(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _get_recent_frauds(arguments: dict) -> list[TextContent]:
    """Fetch recent fraud alerts from the database."""
    hours = arguments.get("hours", 24)
    limit = arguments.get("limit", 20)
    risk_level = arguments.get("risk_level")

    try:
        async with get_session() as session:
            from sqlalchemy import text

            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

            query = """
                SELECT
                    fa.id, fa.risk_level, fa.violated_rules, fa.details,
                    fa.is_resolved, fa.created_at,
                    t.amount, t.location, t.currency,
                    u.external_id as user_external_id
                FROM fraud_alerts fa
                JOIN transactions t ON fa.transaction_id = t.id
                JOIN users u ON fa.user_id = u.id
                WHERE fa.created_at >= :cutoff
            """
            params = {"cutoff": cutoff, "limit": limit}

            if risk_level:
                query += " AND fa.risk_level = :risk_level"
                params["risk_level"] = risk_level

            query += " ORDER BY fa.created_at DESC LIMIT :limit"

            result = await session.execute(text(query), params)
            rows = result.fetchall()

            if not rows:
                return [TextContent(
                    type="text",
                    text=f"No fraud alerts found in the last {hours} hours."
                )]

            alerts = []
            for row in rows:
                alerts.append({
                    "alert_id": str(row[0]),
                    "risk_level": row[1],
                    "violated_rules": row[2],
                    "is_resolved": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "amount": float(row[6]),
                    "location": row[7],
                    "currency": row[8],
                    "user_id": row[9],
                })

            response = {
                "total_alerts": len(alerts),
                "time_window_hours": hours,
                "alerts": alerts,
            }

            return [TextContent(
                type="text",
                text=json.dumps(response, indent=2, default=str)
            )]

    except Exception as e:
        logger.error(f"Error in get_recent_frauds: {e}")
        return [TextContent(type="text", text=f"Error fetching fraud alerts: {str(e)}")]


async def _check_user_status(arguments: dict) -> list[TextContent]:
    """Check user risk status and transaction history."""
    user_id = arguments.get("user_id")

    if not user_id:
        return [TextContent(type="text", text="Error: user_id is required")]

    try:
        async with get_session() as session:
            from sqlalchemy import text

            # Get user info
            user_result = await session.execute(
                text(
                    "SELECT id, external_id, risk_level, total_transactions, "
                    "total_fraud_flags, created_at FROM users WHERE external_id = :eid"
                ),
                {"eid": user_id},
            )
            user_row = user_result.fetchone()

            if not user_row:
                return [TextContent(
                    type="text",
                    text=f"User '{user_id}' not found in the system."
                )]

            db_user_id = user_row[0]

            # Get recent transactions
            tx_result = await session.execute(
                text(
                    "SELECT amount, currency, location, status, created_at "
                    "FROM transactions WHERE user_id = :uid "
                    "ORDER BY created_at DESC LIMIT 10"
                ),
                {"uid": str(db_user_id)},
            )
            recent_txs = [
                {
                    "amount": float(row[0]),
                    "currency": row[1],
                    "location": row[2],
                    "status": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                }
                for row in tx_result.fetchall()
            ]

            # Get recent fraud alerts
            alert_result = await session.execute(
                text(
                    "SELECT risk_level, violated_rules, created_at "
                    "FROM fraud_alerts WHERE user_id = :uid "
                    "ORDER BY created_at DESC LIMIT 5"
                ),
                {"uid": str(db_user_id)},
            )
            recent_alerts = [
                {
                    "risk_level": row[0],
                    "violated_rules": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                }
                for row in alert_result.fetchall()
            ]

            # Calculate fraud rate
            total_tx = user_row[3]
            total_flags = user_row[4]
            fraud_rate = (total_flags / total_tx * 100) if total_tx > 0 else 0

            response = {
                "user_id": user_id,
                "risk_level": user_row[2],
                "total_transactions": total_tx,
                "total_fraud_flags": total_flags,
                "fraud_rate_percent": round(fraud_rate, 2),
                "member_since": user_row[5].isoformat() if user_row[5] else None,
                "recent_transactions": recent_txs,
                "recent_fraud_alerts": recent_alerts,
            }

            return [TextContent(
                type="text",
                text=json.dumps(response, indent=2, default=str)
            )]

    except Exception as e:
        logger.error(f"Error in check_user_status: {e}")
        return [TextContent(type="text", text=f"Error checking user status: {str(e)}")]
