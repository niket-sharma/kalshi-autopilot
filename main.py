"""Main entry point for Polymarket Autopilot."""
import argparse
import logging
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import settings
from models import Portfolio
from agents import AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autopilot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PolymarketAutopilot:
    """Main autopilot controller."""
    
    def __init__(self, initial_capital: float = None):
        """Initialize autopilot.
        
        Args:
            initial_capital: Starting capital (uses settings if None)
        """
        capital = initial_capital or settings.initial_capital
        
        # Create portfolio
        self.portfolio = Portfolio(
            initial_capital=capital,
            current_capital=capital
        )
        
        # Create orchestrator
        self.orchestrator = AgentOrchestrator(self.portfolio)
        
        logger.info("🚀 Polymarket Autopilot started")
        logger.info(f"💵 Initial capital: ${capital:.2f}")
        logger.info(f"🎯 Mode: {settings.mode.upper()}")
        
        if settings.is_test_mode:
            logger.warning("⚠️  Running in TEST MODE - No real trades will be executed")
    
    def run_once(self):
        """Run one trading cycle."""
        try:
            summary = self.orchestrator.run_trading_cycle()
            
            logger.info("\n📊 Cycle Summary:")
            logger.info(f"  Markets scanned: {summary['markets_scanned']}")
            logger.info(f"  Opportunities: {summary['opportunities_found']}")
            logger.info(f"  Trades executed: {summary['trades_executed']}")
            logger.info(f"  Positions monitored: {summary['positions_monitored']}")
            logger.info(f"  Positions closed: {summary['positions_closed']}")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def run_continuous(self, interval_minutes: int = 30):
        """Run continuously with scheduled intervals.
        
        Args:
            interval_minutes: Minutes between cycles
        """
        logger.info(f"🔄 Running continuously (every {interval_minutes} minutes)")
        
        # Run immediately once
        self.run_once()
        
        # Set up scheduler
        scheduler = BlockingScheduler()
        scheduler.add_job(
            self.run_once,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='trading_cycle',
            name='Polymarket Trading Cycle'
        )
        
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n👋 Shutting down Polymarket Autopilot")
            self.print_final_stats()
    
    def print_final_stats(self):
        """Print final statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 FINAL STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Initial Capital: ${self.portfolio.initial_capital:.2f}")
        logger.info(f"Final Equity: ${self.portfolio.equity:.2f}")
        logger.info(f"Total P&L: ${self.portfolio.total_pnl:.2f} ({self.portfolio.total_pnl_percent:.1f}%)")
        logger.info(f"Realized P&L: ${self.portfolio.total_realized_pnl:.2f}")
        logger.info(f"Unrealized P&L: ${self.portfolio.total_unrealized_pnl:.2f}")
        logger.info(f"Total Trades: {len(self.portfolio.positions)}")
        logger.info(f"Open Positions: {len(self.portfolio.open_positions)}")
        logger.info(f"Closed Positions: {len(self.portfolio.closed_positions)}")
        logger.info("=" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Polymarket Autopilot - Autonomous AI Trading')
    parser.add_argument(
        '--mode',
        choices=['once', 'continuous'],
        default='once',
        help='Run once or continuously (default: once)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Minutes between cycles in continuous mode (default: 30)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=None,
        help='Initial capital (overrides .env setting)'
    )
    
    args = parser.parse_args()
    
    # Create autopilot
    autopilot = PolymarketAutopilot(initial_capital=args.capital)
    
    # Run
    if args.mode == 'once':
        autopilot.run_once()
        autopilot.print_final_stats()
    else:
        autopilot.run_continuous(interval_minutes=args.interval)


if __name__ == "__main__":
    main()
