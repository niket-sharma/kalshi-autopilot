"""Debug Kalshi authentication."""
import logging
from api.kalshi_client import KalshiClient

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

print("Testing Kalshi Authentication Debug\n")

try:
    client = KalshiClient()
    
    print("\n--- Testing Balance Endpoint ---")
    try:
        balance = client.get_balance()
        print(f"✅ Success! Balance: ${balance:.2f}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n--- Testing Markets Endpoint ---")
    try:
        markets = client.get_markets(limit=3)
        print(f"✅ Success! Found {len(markets)} markets")
        if markets:
            print(f"   First market: {markets[0].question[:60]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n--- Testing Positions Endpoint ---")
    try:
        positions = client.get_positions()
        print(f"✅ Success! Found {len(positions)} positions")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
except Exception as e:
    print(f"\n❌ Client initialization failed: {e}")
    import traceback
    traceback.print_exc()
