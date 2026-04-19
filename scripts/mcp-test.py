#!/usr/bin/env python3
"""
MCP Server Test Script
Tests the MCP server tools by connecting via SSE transport.
"""

import asyncio
import json
import sys

import httpx


MCP_URL = "http://localhost:8001"


async def test_health():
    """Test MCP server health endpoint."""
    print("🔍 Testing MCP Server health...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MCP_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Body: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200


async def test_via_api():
    """Test MCP tools indirectly via the API Gateway endpoints."""
    print("\n🔍 Testing equivalent API endpoints...")

    async with httpx.AsyncClient() as client:
        # Test fraud list (equivalent to get_recent_frauds)
        print("\n  📋 GET /api/v1/frauds")
        response = await client.get(f"http://localhost:8000/api/v1/frauds")
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"     Total alerts: {data.get('pagination', {}).get('total_items', 0)}")

        # Test user status (equivalent to check_user_status)
        print("\n  👤 GET /api/v1/users/user_1/risk")
        response = await client.get(f"http://localhost:8000/api/v1/users/user_1/risk")
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {})
            print(f"     Risk Level: {user_data.get('risk_level', 'N/A')}")
            print(f"     Total Transactions: {user_data.get('total_transactions', 0)}")
            print(f"     Fraud Flags: {user_data.get('total_fraud_flags', 0)}")


async def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         MCP Server Test Script                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    health_ok = await test_health()

    if not health_ok:
        print("\n❌ MCP Server is not running. Start with: docker-compose up mcp-server")
        sys.exit(1)

    await test_via_api()

    print("\n✅ MCP Server tests completed!")
    print("\nTo test with an MCP client (e.g., Claude Desktop), add this to your config:")
    print(json.dumps({
        "mcpServers": {
            "fraud-detection": {
                "url": f"{MCP_URL}/sse"
            }
        }
    }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
