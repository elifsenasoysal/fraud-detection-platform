#!/usr/bin/env python3
"""
Seed Data Script
Populates the database with sample users and transactions for demo purposes.
"""

import json
import random
import time
import sys

import httpx

API_URL = "http://localhost:8000"

CITIES = [
    "Istanbul", "Ankara", "Izmir", "Antalya", "Bursa",
    "Trabzon", "Gaziantep", "Konya", "Adana", "Diyarbakir",
    "Samsun", "Mersin", "Eskisehir", "Kayseri",
]

USERS = [f"user_{i}" for i in range(1, 21)]


def create_transaction(client: httpx.Client, user_id: str, amount: float, location: str):
    """Send a single transaction to the API."""
    try:
        response = client.post(
            f"{API_URL}/api/v1/transactions",
            json={
                "user_id": user_id,
                "amount": amount,
                "currency": "TRY",
                "location": location,
            },
            timeout=10,
        )
        status = "✅" if response.status_code == 201 else "❌"
        print(f"  {status} {user_id} | {amount:.2f} TRY | {location}")
        return response.status_code == 201
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("🌱 Seeding database with sample data...")
    print(f"   API URL: {API_URL}")
    print(f"   Users: {len(USERS)}")
    print()

    client = httpx.Client()
    success = 0
    total = 0

    # Phase 1: Normal transactions (builds user history)
    print("📦 Phase 1: Creating normal transactions (building user history)...")
    for _ in range(50):
        user = random.choice(USERS)
        amount = round(random.uniform(50, 2000), 2)
        location = random.choice(CITIES)

        if create_transaction(client, user, amount, location):
            success += 1
        total += 1
        time.sleep(0.1)

    print()
    print("⚠️  Phase 2: Creating anomaly scenarios...")

    # Phase 2: Velocity anomaly
    print("\n  🔴 Velocity anomaly: user_1 rapid-fire...")
    for _ in range(8):
        amount = round(random.uniform(100, 500), 2)
        if create_transaction(client, "user_1", amount, "Istanbul"):
            success += 1
        total += 1
        time.sleep(0.05)

    # Phase 3: Amount anomaly
    print("\n  🔴 Amount anomaly: user_5 high amount...")
    if create_transaction(client, "user_5", 45000.00, "Ankara"):
        success += 1
    total += 1

    # Phase 4: Location anomaly
    print("\n  🔴 Location anomaly: user_3 impossible travel...")
    if create_transaction(client, "user_3", 500.00, "Istanbul"):
        success += 1
    total += 1
    time.sleep(0.5)
    if create_transaction(client, "user_3", 750.00, "Van"):
        success += 1
    total += 1

    client.close()

    print()
    print(f"✅ Seeding complete: {success}/{total} transactions successful")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--url":
        API_URL = sys.argv[2]
    main()
