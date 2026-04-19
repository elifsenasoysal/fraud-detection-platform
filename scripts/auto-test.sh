#!/usr/bin/env bash
# ============================================
# Automated Test Script
# ============================================
# Generates random transactions with configurable anomaly scenarios
#
# Usage: ./scripts/auto-test.sh [options]
# Options:
#   --duration=<seconds>         Script run duration (default: 60)
#   --rate=<requests_per_second> Requests per second (default: 5)
#   --anomaly-chance=<percent>   Anomaly probability % (default: 15)
#   --users=<count>              Number of random users (default: 10)

set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

# ── Default parameters ──
DURATION=60
RATE=5
ANOMALY_CHANCE=15
USER_COUNT=10

# ── Parse arguments ──
for arg in "$@"; do
    case $arg in
        --duration=*)   DURATION="${arg#*=}" ;;
        --rate=*)       RATE="${arg#*=}" ;;
        --anomaly-chance=*) ANOMALY_CHANCE="${arg#*=}" ;;
        --users=*)      USER_COUNT="${arg#*=}" ;;
        --help|-h)
            echo "Fraud Detection Platform — Automated Test Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --duration=<seconds>          Run duration (default: 60)"
            echo "  --rate=<requests_per_second>  Requests per second (default: 5)"
            echo "  --anomaly-chance=<percent>    Anomaly probability % (default: 15)"
            echo "  --users=<count>               Number of users (default: 10)"
            echo ""
            echo "Environment:"
            echo "  API_URL                       API base URL (default: http://localhost:8000)"
            echo ""
            echo "Examples:"
            echo "  $0 --duration=30 --rate=10 --anomaly-chance=20"
            echo "  $0 --duration=120 --rate=2 --anomaly-chance=50"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

# ── City list ──
CITIES=("Istanbul" "Ankara" "Izmir" "Antalya" "Bursa" "Trabzon" "Gaziantep" "Konya" "Adana" "Diyarbakir" "Samsun" "Mersin" "Eskisehir" "Kayseri" "Van" "Erzurum" "Malatya")

# ── Utility functions ──
random_city() {
    echo "${CITIES[$((RANDOM % ${#CITIES[@]}))]}"
}

random_user() {
    echo "user_$((RANDOM % USER_COUNT + 1))"
}

random_amount() {
    # Normal: 50-2000 TRY
    echo "$((RANDOM % 1950 + 50)).$((RANDOM % 100))"
}

anomaly_amount() {
    # Anomaly: 5000-50000 TRY (abnormally high)
    echo "$((RANDOM % 45000 + 5000)).$((RANDOM % 100))"
}

send_transaction() {
    local user_id="$1"
    local amount="$2"
    local location="$3"
    local is_anomaly="$4"

    local marker=""
    if [ "$is_anomaly" = "true" ]; then
        marker=" 🚨 ANOMALY"
    fi

    curl -s -o /dev/null -w "%{http_code}" -X POST "${API_URL}/api/v1/transactions" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": \"${user_id}\",
            \"amount\": ${amount},
            \"currency\": \"TRY\",
            \"location\": \"${location}\"
        }" &

    echo "  → ${user_id} | ${amount} TRY | ${location}${marker}"
}

# ── Header ──
echo "╔══════════════════════════════════════════════════════════╗"
echo "║    Fraud Detection Platform — Automated Test Script     ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Duration:       ${DURATION}s"
echo "║  Rate:           ${RATE} req/s"
echo "║  Anomaly Chance: ${ANOMALY_CHANCE}%"
echo "║  Users:          ${USER_COUNT}"
echo "║  API URL:        ${API_URL}"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Statistics ──
TOTAL_SENT=0
TOTAL_ANOMALIES=0
START_TIME=$(date +%s)
SLEEP_INTERVAL=$(echo "scale=4; 1 / ${RATE}" | bc)

# ── Main loop ──
echo "🚀 Starting test run..."
echo ""

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))

    if [ "$ELAPSED" -ge "$DURATION" ]; then
        break
    fi

    # Determine if this is an anomaly
    ROLL=$((RANDOM % 100))
    IS_ANOMALY="false"
    USER=$(random_user)
    AMOUNT=$(random_amount)
    LOCATION=$(random_city)

    if [ "$ROLL" -lt "$ANOMALY_CHANCE" ]; then
        IS_ANOMALY="true"
        TOTAL_ANOMALIES=$((TOTAL_ANOMALIES + 1))

        # Choose anomaly type
        ANOMALY_TYPE=$((RANDOM % 3))

        case $ANOMALY_TYPE in
            0)
                # Velocity anomaly: rapid-fire transactions from same user
                BURST_USER=$(random_user)
                for i in $(seq 1 7); do
                    send_transaction "$BURST_USER" "$(random_amount)" "$(random_city)" "true"
                    TOTAL_SENT=$((TOTAL_SENT + 1))
                done
                continue
                ;;
            1)
                # Amount anomaly: unusually high amount
                AMOUNT=$(anomaly_amount)
                ;;
            2)
                # Location anomaly: same user, different distant cities rapidly
                LOC_USER=$(random_user)
                send_transaction "$LOC_USER" "$(random_amount)" "Istanbul" "true"
                sleep 0.5
                send_transaction "$LOC_USER" "$(random_amount)" "Van" "true"
                TOTAL_SENT=$((TOTAL_SENT + 2))
                continue
                ;;
        esac
    fi

    send_transaction "$USER" "$AMOUNT" "$LOCATION" "$IS_ANOMALY"
    TOTAL_SENT=$((TOTAL_SENT + 1))

    sleep "$SLEEP_INTERVAL"
done

# Wait for background curl processes to finish
wait

# ── Summary ──
END_TIME=$(date +%s)
ACTUAL_DURATION=$((END_TIME - START_TIME))

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    TEST COMPLETE                        ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Duration:              ${ACTUAL_DURATION}s"
echo "║  Total Transactions:    ${TOTAL_SENT}"
echo "║  Anomaly Attempts:      ${TOTAL_ANOMALIES}"
echo "║  Avg Rate:              $(echo "scale=1; ${TOTAL_SENT} / ${ACTUAL_DURATION}" | bc) req/s"
echo "╚══════════════════════════════════════════════════════════╝"
