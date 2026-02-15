"""Test Kalshi API connection with your credentials."""
import logging
from config import settings
from api.kalshi_client import KalshiClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("=" * 60)
print("🔐 Testing Kalshi API Connection")
print("=" * 60)
print()

try:
    # Show what we're connecting to
    print(f"📧 Email: {settings.kalshi_api_key}")
    print(f"🌐 Mode: {settings.mode.upper()}")
    if settings.is_test_mode:
        print(f"📍 API: https://demo-api.kalshi.co (DEMO)")
    else:
        print(f"📍 API: https://trading-api.kalshi.com (LIVE)")
    print()
    
    # Initialize client (will auto-login)
    print("🔄 Logging in to Kalshi...")
    client = KalshiClient()
    print(f"✅ Login successful!")
    print()
    
    # Check balance
    print("💰 Checking account balance...")
    balance = client.get_balance()
    print(f"✅ Balance: ${balance:.2f}")
    print()
    
    if balance < 25:
        print("⚠️  WARNING: Balance is low!")
        print(f"   You have ${balance:.2f}, need at least $25 to start trading")
        print("   Deposit funds at https://kalshi.com")
        print()
    
    # Get some markets
    print("📊 Fetching top markets...")
    markets = client.get_markets(limit=5, active_only=True)
    print(f"✅ Found {len(markets)} active markets:")
    print()
    
    for i, market in enumerate(markets, 1):
        print(f"{i}. {market.question[:70]}...")
        print(f"   Volume: ${market.volume:,.0f} | Yes: {market.yes_price:.1%}")
    
    print()
    
    # Check positions
    print("📋 Checking open positions...")
    positions = client.get_positions()
    print(f"✅ Open positions: {len(positions)}")
    print()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("🚀 Your bot is ready to trade!")
    print(f"💰 Starting capital: ${balance:.2f}")
    print(f"🎯 Mode: {settings.mode.upper()}")
    print()
    
    if settings.is_test_mode:
        print("📝 Currently in TEST MODE")
        print("   ✓ Safe paper trading")
        print("   ✓ No real money at risk")
        print("   To enable live trading: Change MODE=live in .env")
    else:
        print("⚠️  LIVE TRADING ENABLED!")
        print("   Bot will execute real trades with real money")
        print("   Make sure you're ready before running the bot!")
    
    print()
    print("📝 Next steps:")
    print("   1. python main.py --mode once     (run one trading cycle)")
    print("   2. python main.py --mode continuous  (run 24/7)")
    print()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check credentials in .env file")
    print("2. Verify account exists at https://kalshi.com")
    print("3. Make sure account is verified (KYC complete)")
    print("4. Try demo mode first: MODE=test in .env")
    print()
    import traceback
    traceback.print_exc()
