#!/usr/bin/env bash
# ============================================
# Manual Transaction Input Script
# ============================================
# Usage: ./scripts/manual-input.sh <user_id> <amount> <location>
# Example: ./scripts/manual-input.sh user_42 1500.00 Istanbul

set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

# ── Validation ──
if [ $# -lt 3 ]; then
    echo "❌ Usage: $0 <user_id> <amount> <location>"
    echo ""
    echo "Arguments:"
    echo "  user_id   - External user identifier (e.g., user_42)"
    echo "  amount    - Transaction amount (e.g., 1500.00)"
    echo "  location  - City name (e.g., Istanbul, Ankara, Izmir)"
    echo ""
    echo "Environment:"
    echo "  API_URL   - API base URL (default: http://localhost:8000)"
    echo ""
    echo "Examples:"
    echo "  $0 user_42 1500.00 Istanbul"
    echo "  $0 user_7 250.50 Ankara"
    echo "  API_URL=http://api:8000 $0 user_1 999.99 Izmir"
    exit 1
fi

USER_ID="$1"
AMOUNT="$2"
LOCATION="$3"

echo "📤 Sending transaction..."
echo "   User:     ${USER_ID}"
echo "   Amount:   ${AMOUNT} TRY"
echo "   Location: ${LOCATION}"
echo ""

# ── Send request ──
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/api/v1/transactions" \
    -H "Content-Type: application/json" \
    -d "{
        \"user_id\": \"${USER_ID}\",
        \"amount\": ${AMOUNT},
        \"currency\": \"TRY\",
        \"location\": \"${LOCATION}\"
    }")

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$ d')

if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ Transaction created successfully!"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "❌ Failed! HTTP ${HTTP_CODE}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi
