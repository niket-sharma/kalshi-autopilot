"""Test Polymarket wallet connection."""
import logging
from config import settings
from api import PolymarketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🔐 Testing Polymarket Wallet Connection")
print("=" * 60)
print()

try:
    # Initialize client
    print("🔄 Connecting to Polymarket...")
    client = PolymarketClient()
    print(f"✅ Connected!")
    print(f"📍 Wallet: {client.address}")
    print()
    
    # Check balance
    print("💰 Checking USDC balance...")
    balance = client.get_balance()
    print(f"✅ Balance: ${balance:.2f} USDC")
    print()
    
    if balance < 25:
        print("⚠️  WARNING: Balance is low!")
        print(f"   You have ${balance:.2f}, need at least $25 to start trading")
        print("   Fund your wallet with USDC on Polygon network")
        print()
    
    # Get some markets
    print("📊 Fetching high-volume markets...")
    markets = client.get_high_volume_markets(min_volume=5000, limit=5)
    print(f"✅ Found {len(markets)} high-volume markets:")
    print()
    
    for i, market in enumerate(markets, 1):
        print(f"{i}. {market.question[:70]}...")
        print(f"   Volume: ${market.volume:,.0f} | Yes: {market.yes_price:.2%}")
    
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
        print("📝 Currently in TEST MODE (no real trades)")
        print("   To enable live trading: Change MODE=live in .env")
    else:
        print("⚠️  LIVE TRADING ENABLED!")
        print("   Bot will execute real trades with real money")
    
    print()
    print("📝 Next: Run 'python main.py --mode once' to start trading cycle")
    print()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check POLYMARKET_PRIVATE_KEY in .env file")
    print("2. Ensure you have USDC on Polygon network")
    print("3. Verify wallet has been used on Polymarket before")
    print()
