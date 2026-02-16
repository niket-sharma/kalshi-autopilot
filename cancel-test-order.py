#!/usr/bin/env python3
"""Cancel the test order."""
from api.kalshi_client import KalshiClient
import requests

client = KalshiClient()

# The test order ID
order_id = 'bd96c0ec-6e2f-44ea-b60f-85e9f87827c1'

print("🗑️  Canceling test order...")
print(f"Order ID: {order_id}")
print()

# Cancel the order
path = f'/trade-api/v2/portfolio/orders/{order_id}'
headers = client._get_headers('DELETE', path)

response = requests.delete(f'{client.base_url}{path}', headers=headers)

if response.status_code in [200, 204]:
    print("✅ Order canceled successfully!")
    print()
    print("Check your Kalshi app - the order should be gone.")
else:
    print(f"❌ Failed to cancel: {response.status_code}")
    print(f"Response: {response.text}")
