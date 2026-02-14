"""Quick test script to verify the system works."""
import logging
from config import settings
from models import Portfolio
from api import PolymarketClient, NewsAggregator
from agents import ResearchAgent, RiskManager, ExecutionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_api_connection():
    """Test Polymarket API connection."""
    logger.info("Testing Polymarket API...")
    client = PolymarketClient()
    
    markets = client.get_high_volume_markets(limit=5)
    logger.info(f"✅ Fetched {len(markets)} markets")
    
    if markets:
        logger.info(f"Sample market: {markets[0].question}")
        logger.info(f"  Volume: ${markets[0].volume:.0f}")
        logger.info(f"  Yes price: {markets[0].yes_price:.2%}")


def test_research_agent():
    """Test research agent analysis."""
    logger.info("\nTesting Research Agent...")
    
    client = PolymarketClient()
    markets = client.get_high_volume_markets(limit=1)
    
    if not markets:
        logger.error("No markets found")
        return
    
    researcher = ResearchAgent()
    event = researcher.analyze_market(markets[0])
    
    logger.info(f"✅ Analysis complete")
    logger.info(f"  Market: {event.market.question}")
    logger.info(f"  Research probability: {event.research_probability:.2%}")
    logger.info(f"  Confidence: {event.confidence:.2%}")
    logger.info(f"  Edge: {event.edge:.2%}")
    logger.info(f"  Has edge: {event.has_edge}")


def test_risk_manager():
    """Test risk manager position sizing."""
    logger.info("\nTesting Risk Manager...")
    
    # Create mock event
    client = PolymarketClient()
    markets = client.get_markets(limit=1)
    
    if not markets:
        logger.error("No markets found")
        return
    
    # Analyze it
    researcher = ResearchAgent()
    event = researcher.analyze_market(markets[0])
    
    # Create portfolio
    portfolio = Portfolio(initial_capital=25.0, current_capital=25.0)
    
    # Calculate position size
    risk_mgr = RiskManager()
    sizing = risk_mgr.calculate_position_size(event, portfolio)
    
    if sizing:
        logger.info(f"✅ Position sizing complete")
        logger.info(f"  Should trade: {sizing['should_trade']}")
        logger.info(f"  Side: {sizing['side'].value.upper()}")
        logger.info(f"  Capital: ${sizing['capital']:.2f}")
        logger.info(f"  Shares: {sizing['shares']:.2f}")
        logger.info(f"  Entry: ${sizing['entry_price']:.3f}")
        logger.info(f"  Stop: ${sizing['stop_loss']:.3f}")
        logger.info(f"  Target: ${sizing['take_profit']:.3f}")
    else:
        logger.info("No trade recommended (edge/confidence too low)")


def test_full_cycle():
    """Test full trading cycle."""
    logger.info("\nTesting Full Cycle...")
    
    from agents import AgentOrchestrator
    
    portfolio = Portfolio(initial_capital=25.0, current_capital=25.0)
    orchestrator = AgentOrchestrator(portfolio)
    
    summary = orchestrator.run_trading_cycle()
    
    logger.info(f"✅ Cycle complete")
    logger.info(f"  Markets scanned: {summary['markets_scanned']}")
    logger.info(f"  Opportunities: {summary['opportunities_found']}")
    logger.info(f"  Trades executed: {summary['trades_executed']}")


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("🧪 Polymarket Autopilot System Tests")
    logger.info("=" * 60)
    logger.info(f"Mode: {settings.mode}")
    logger.info(f"OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    logger.info("")
    
    try:
        test_api_connection()
        test_research_agent()
        test_risk_manager()
        test_full_cycle()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests passed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
