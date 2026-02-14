"""Execution Agent - Places orders and manages positions."""
from typing import Optional, List, Dict
from models import Position, Portfolio, PositionStatus
from api import PolymarketClient
from config import settings
import logging

logger = logging.getLogger(__name__)


class ExecutionAgent:
    """Agent that executes trades and manages positions."""
    
    def __init__(self):
        self.client = PolymarketClient()
        
    def execute_trade(
        self, 
        position: Position, 
        portfolio: Portfolio
    ) -> bool:
        """Execute a trade (open position).
        
        Args:
            position: Position to open
            portfolio: Current portfolio
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(
            f"Executing trade: {position.side.value.upper()} "
            f"{position.shares:.2f} shares of {position.question[:50]}..."
        )
        
        # Check if we can open this position
        if not portfolio.can_open_position(position.capital_allocated):
            logger.warning("Cannot open position - portfolio limits reached")
            return False
        
        # Place order via Polymarket API
        order_result = self.client.place_order(
            market_id=position.market_id,
            side="BUY",  # Always buying (either YES or NO shares)
            size=position.shares,
            price=position.entry_price
        )
        
        if order_result:
            # Add position to portfolio
            portfolio.add_position(position)
            logger.info(f"✅ Position opened successfully - ID: {position.id}")
            return True
        else:
            logger.error("❌ Failed to place order")
            return False
    
    def monitor_positions(self, portfolio: Portfolio) -> List[str]:
        """Monitor open positions and check exit conditions.
        
        Args:
            portfolio: Current portfolio
            
        Returns:
            List of actions taken
        """
        actions = []
        
        # Get current prices for all markets
        market_prices = {}
        for position in portfolio.open_positions:
            market = self.client.get_market_by_id(position.market_id)
            if market:
                if position.side.value == "yes":
                    market_prices[position.market_id] = market.yes_price
                else:
                    market_prices[position.market_id] = market.no_price
        
        # Update portfolio with current prices
        portfolio.update_position_prices(market_prices)
        
        # Check each position for exit conditions
        for position in portfolio.open_positions:
            # Check stop loss
            if position.check_stop_loss():
                logger.warning(
                    f"🛑 Stop loss hit for {position.question[:50]}... "
                    f"@ ${position.current_price:.3f}"
                )
                self._close_position(position, portfolio, "stop_loss")
                actions.append(f"Stopped out: {position.id}")
                
            # Check take profit
            elif position.check_take_profit():
                logger.info(
                    f"🎯 Take profit hit for {position.question[:50]}... "
                    f"@ ${position.current_price:.3f}"
                )
                self._close_position(position, portfolio, "take_profit")
                actions.append(f"Profit taken: {position.id}")
        
        return actions
    
    def _close_position(
        self, 
        position: Position, 
        portfolio: Portfolio, 
        reason: str
    ) -> bool:
        """Close a position.
        
        Args:
            position: Position to close
            portfolio: Portfolio
            reason: Reason for closing
            
        Returns:
            True if successful
        """
        if position.current_price is None:
            logger.error("Cannot close position - no current price")
            return False
        
        logger.info(f"Closing position {position.id} - Reason: {reason}")
        
        # Place sell order
        order_result = self.client.place_order(
            market_id=position.market_id,
            side="SELL",
            size=position.shares,
            price=position.current_price
        )
        
        if order_result:
            # Close position in portfolio
            pnl = portfolio.close_position(position.id, position.current_price)
            
            logger.info(
                f"✅ Position closed - P&L: ${pnl:.2f} ({position.pnl_percent:.1f}%)"
            )
            
            # Maybe compound profits
            if settings.auto_compound and pnl > 0:
                logger.info(f"💰 Compounding profit: ${pnl:.2f}")
                # Profits already added to current_capital in portfolio.close_position()
            
            return True
        else:
            logger.error("❌ Failed to close position")
            return False
    
    def get_portfolio_status(self, portfolio: Portfolio) -> Dict:
        """Get current portfolio status summary.
        
        Args:
            portfolio: Portfolio
            
        Returns:
            Status dict
        """
        return {
            "equity": portfolio.equity,
            "capital": portfolio.current_capital,
            "allocated": portfolio.total_allocated,
            "available": portfolio.available_capital,
            "total_pnl": portfolio.total_pnl,
            "total_pnl_pct": portfolio.total_pnl_percent,
            "unrealized_pnl": portfolio.total_unrealized_pnl,
            "realized_pnl": portfolio.total_realized_pnl,
            "open_positions": len(portfolio.open_positions),
            "closed_positions": len(portfolio.closed_positions),
            "drawdown": portfolio.drawdown,
            "today_pnl": portfolio.get_today_pnl()
        }
