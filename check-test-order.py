#!/usr/bin/env python3
"""Check status of the test order."""
from api.kalshi_client import KalshiClient
import requests
from datetime import datetime

client = KalshiClient()
test_order_id = 'bd96c0ec-6e2f-44ea-b60f-85e9f87827c1'

print("=" * 80)
print("🔍 TEST ORDER STATUS CHECK")
print("=" * 80)
print(f"Order ID: {test_order_id}")
print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}")
print()

# Check order status
path = f'/trade-api/v2/portfolio/orders/{test_order_id}'
headers = client._get_headers('GET', path)

try:
    response = requests.get(f'{client.base_url}{path}', headers=headers)
    
    if response.status_code == 200:
        order = response.json().get('order', {})
        
        status = order.get('status', 'unknown')
        side = order.get('side', '').upper()
        remaining = order.get('remaining_count', 0)
        filled = order.get('count', 0) - remaining
        yes_price = order.get('yes_price', 0)
        
        print(f"Status: {status.upper()}")
        print(f"Side: {side}")
        print(f"Price: ${yes_price/100:.2f} per contract")
        print(f"Filled: {filled} / {order.get('count', 0)} contracts")
        print(f"Remaining: {remaining} contracts")
        print()
        
        if status == 'resting':
            print("⏳ Order is PENDING (waiting to fill)")
            print("   → Market needs to reach $0.50 or lower")
            print("   → May take hours or never fill")
        elif status == 'filled':
            print("✅ Order FILLED!")
            print("   → Check your Kalshi app Portfolio → Positions")
            print("   → You now have a position in this market")
        elif status == 'canceled':
            print("❌ Order was CANCELED")
        else:
            print(f"❓ Order status: {status}")
        
    elif response.status_code == 404:
        print("❌ Order not found")
        print("   → May have been filled and converted to position")
        print("   → Check Kalshi app Portfolio → Positions")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error checking order: {e}")

print()
print("=" * 80)
print("📱 To verify in Kalshi app:")
print("   1. Open Kalshi app")
print("   2. Go to Portfolio")
print("   3. Check 'Orders' tab (if pending)")
print("   4. Check 'Positions' tab (if filled)")
print("=" * 80)
