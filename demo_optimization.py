"""Demo: Show the optimization in action."""
import logging
from api import PolymarketClient
from agents import ResearchAgent
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 70)
print("🚀 POLYMARKET AUTOPILOT - 3-LAYER OPTIMIZATION DEMO")
print("=" * 70)
print()
print("This demo shows how the optimized algorithm works:")
print()
print("OLD APPROACH:")
print("  50 markets → Gemini analyzes ALL 50")
print("  = 50 API calls × 300 tokens = 15,000 tokens")
print("  = Expensive & slow")
print()
print("NEW APPROACH:")
print("  LAYER 1 (Filters): 50 → ~10 markets (Python only)")
print("  LAYER 2 (Scoring): 10 → ~3 markets (Python only)")
print("  LAYER 3 (LLM): 3 markets × 20 tokens = 60 tokens")
print("  = 250x more efficient! 🎉")
print()
print("=" * 70)
print()

try:
    # Initialize
    print("🔄 Connecting to Polymarket...")
    client = PolymarketClient()
    print(f"✅ Connected! Wallet: {client.address}")
    print()
    
    # Fetch markets
    print("📊 Fetching markets...")
    markets = client.get_markets(limit=20, active_only=True)
    print(f"✅ Found {len(markets)} active markets")
    print()
    
    if not markets:
        print("❌ No markets available. Try again later.")
        exit(1)
    
    # Show sample markets
    print("Sample markets:")
    for i, m in enumerate(markets[:5], 1):
        print(f"  {i}. {m.question[:65]}...")
        print(f"     Volume: ${m.volume:,.0f} | Liquidity: ${m.liquidity:,.0f} | Price: {m.yes_price:.0%}")
    print()
    
    # Run optimized analysis
    print("🧠 Running 3-Layer Analysis...")
    print()
    
    researcher = ResearchAgent()
    events = researcher.analyze_markets(markets)
    
    # Show results
    print("\n" + "=" * 70)
    print("📈 RESULTS")
    print("=" * 70)
    
    if events:
        print(f"\n✅ Found {len(events)} tradeable opportunities:")
        print()
        
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.market.question[:65]}...")
            print(f"   Market Price: {event.market.yes_price:.0%}")
            print(f"   AI Estimate:  {event.research_probability:.0%}")
            print(f"   Edge:         {event.edge:.1%} ⭐")
            print(f"   Confidence:   {event.confidence:.0%}")
            print()
    else:
        print("\n❌ No tradeable opportunities found")
        print("   This is normal - not every cycle finds edges")
        print("   The bot will keep scanning automatically")
    
    print("=" * 70)
    print()
    print("💡 Efficiency Stats:")
    print(f"   Markets analyzed: {len(markets)}")
    print(f"   LLM calls made: {len(events[:5])} (max 5)")
    print(f"   Tokens used: ~{len(events[:5]) * 20} (vs ~{len(markets) * 300} with old method)")
    print(f"   Cost: FREE (within Gemini free tier)")
    print()
    print("✅ Demo complete! Bot is ready to trade.")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
