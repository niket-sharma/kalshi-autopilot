"""Agent Orchestrator - Coordinates multi-agent workflow."""
from typing import List
from models import Portfolio, Event
from api import PolymarketClient
from .research_agent import ResearchAgent
from .risk_manager import RiskManager
from .execution_agent import ExecutionAgent
from config import settings
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates the multi-agent trading workflow."""
    
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        
        # Initialize agents
        self.market_client = PolymarketClient()
        self.researcher = ResearchAgent()
        self.risk_manager = RiskManager()
        self.executor = ExecutionAgent()
        
        logger.info("🤖 Agent Orchestrator initialized")
        logger.info(f"📊 Portfolio: ${self.portfolio.equity:.2f}")
        logger.info(f"🎯 Mode: {settings.mode.upper()}")
    
    def run_trading_cycle(self) -> dict:
        """Run one complete trading cycle.
        
        Workflow:
        1. Scan markets for opportunities
        2. Research & analyze events
        3. Calculate position sizing
        4. Execute trades
        5. Monitor existing positions
        
        Returns:
            Cycle summary
        """
        logger.info("=" * 60)
        logger.info("🔄 Starting trading cycle")
        logger.info("=" * 60)
        
        summary = {
            "markets_scanned": 0,
            "opportunities_found": 0,
            "trades_executed": 0,
            "positions_monitored": 0,
            "positions_closed": 0
        }
        
        # Step 1: Monitor existing positions first
        logger.info("\n📊 Step 1: Monitoring existing positions...")
        actions = self.executor.monitor_positions(self.portfolio)
        summary["positions_monitored"] = len(self.portfolio.open_positions)
        summary["positions_closed"] = len(actions)
        
        if actions:
            for action in actions:
                logger.info(f"  → {action}")
        
        # Step 2: Check if we can open new positions
        if len(self.portfolio.open_positions) >= settings.max_concurrent_positions:
            logger.info(f"\n⚠️  Max concurrent positions reached ({settings.max_concurrent_positions})")
            logger.info("Skipping market scan")
            return summary
        
        # Step 3: Scan markets for opportunities
        logger.info("\n🔍 Step 2: Scanning markets...")
        markets = self.market_client.get_high_volume_markets(
            min_volume=5000,  # Minimum $5k volume
            limit=20
        )
        summary["markets_scanned"] = len(markets)
        logger.info(f"  Found {len(markets)} high-volume markets")
        
        # Step 4: Research & analyze events
        logger.info("\n🧠 Step 3: Analyzing markets...")
        opportunities = []
        
        for market in markets:
            try:
                event = self.researcher.analyze_market(market)
                
                # Check if this is a trade opportunity
                if event.has_edge and event.is_confident:
                    logger.info(
                        f"  ✅ Opportunity: {market.question[:60]}... "
                        f"(Edge: {event.edge:.2%}, Conf: {event.confidence:.2%})"
                    )
                    opportunities.append(event)
                else:
                    logger.debug(
                        f"  ❌ No edge: {market.question[:60]}... "
                        f"(Edge: {event.edge:.2%}, Conf: {event.confidence:.2%})"
                    )
                    
            except Exception as e:
                logger.error(f"  Error analyzing market: {e}")
                continue
        
        summary["opportunities_found"] = len(opportunities)
        logger.info(f"\n🎯 Found {len(opportunities)} opportunities")
        
        # Step 5: Execute trades
        if opportunities:
            logger.info("\n💰 Step 4: Executing trades...")
            
            # Sort by edge * confidence (best opportunities first)
            opportunities.sort(
                key=lambda e: (e.edge or 0) * (e.confidence or 0),
                reverse=True
            )
            
            for event in opportunities:
                # Check if we can still open positions
                if len(self.portfolio.open_positions) >= settings.max_concurrent_positions:
                    logger.info("  Max positions reached, stopping")
                    break
                
                # Calculate position size
                sizing = self.risk_manager.calculate_position_size(event, self.portfolio)
                
                if sizing and sizing["should_trade"]:
                    # Create position
                    position = self.risk_manager.create_position(event, sizing)
                    
                    # Execute trade
                    success = self.executor.execute_trade(position, self.portfolio)
                    
                    if success:
                        summary["trades_executed"] += 1
        
        # Final status
        logger.info("\n" + "=" * 60)
        logger.info("📈 Cycle Complete - Portfolio Status:")
        status = self.executor.get_portfolio_status(self.portfolio)
        logger.info(f"  Equity: ${status['equity']:.2f}")
        logger.info(f"  Total P&L: ${status['total_pnl']:.2f} ({status['total_pnl_pct']:.1f}%)")
        logger.info(f"  Open Positions: {status['open_positions']}")
        logger.info(f"  Available Capital: ${status['available']:.2f}")
        logger.info(f"  Drawdown: {status['drawdown']:.1f}%")
        logger.info("=" * 60)
        
        return summary
