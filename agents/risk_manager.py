"""Risk Manager - Calculates position sizes and manages risk."""
from typing import Optional, Dict
from models import Event, Portfolio, Position, PositionSide
from config import settings
import logging
import uuid

logger = logging.getLogger(__name__)


class RiskManager:
    """Agent that manages risk and calculates position sizes."""
    
    def __init__(self):
        pass
    
    def calculate_position_size(
        self, 
        event: Event, 
        portfolio: Portfolio
    ) -> Optional[Dict]:
        """Calculate optimal position size using Kelly Criterion.
        
        Args:
            event: Event with analysis
            portfolio: Current portfolio
            
        Returns:
            Position sizing recommendation or None if no trade
        """
        # Step 1: Check if we should trade
        if not self._should_trade(event, portfolio):
            return None
        
        # Step 2: Determine side (YES or NO)
        side = self._determine_side(event)
        
        # Step 3: Calculate Kelly fraction
        kelly_fraction = self._calculate_kelly(event, side)
        
        # Step 4: Apply safety limits
        position_fraction = self._apply_limits(kelly_fraction)
        
        # Step 5: Calculate capital allocation
        capital = portfolio.equity * position_fraction
        
        # Step 6: Calculate shares and prices
        entry_price = event.market.yes_price if side == PositionSide.YES else event.market.no_price
        shares = capital / entry_price if entry_price > 0 else 0
        
        # Step 7: Calculate stop loss and take profit
        stop_loss, take_profit = self._calculate_exit_levels(entry_price, side)
        
        recommendation = {
            "should_trade": True,
            "side": side,
            "capital": capital,
            "shares": shares,
            "entry_price": entry_price,
            "kelly_fraction": kelly_fraction,
            "position_fraction": position_fraction,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "edge": event.edge,
            "confidence": event.confidence
        }
        
        logger.info(
            f"Position recommendation: {side.value.upper()} "
            f"{shares:.2f} shares @ ${entry_price:.3f} "
            f"(${capital:.2f}, {position_fraction:.1%} of portfolio)"
        )
        
        return recommendation
    
    def _should_trade(self, event: Event, portfolio: Portfolio) -> bool:
        """Determine if we should trade this event."""
        # Check if event has sufficient edge
        if not event.has_edge:
            logger.debug(f"Insufficient edge: {event.edge:.2%} < {settings.min_edge_threshold:.2%}")
            return False
        
        # Check if we're confident enough
        if not event.is_confident:
            logger.debug(f"Insufficient confidence: {event.confidence:.2%} < {settings.min_confidence:.2%}")
            return False
        
        # Check if market has enough liquidity
        if event.market.liquidity < 1000:  # Minimum $1k liquidity
            logger.debug(f"Insufficient liquidity: ${event.market.liquidity:.0f}")
            return False
        
        # Check portfolio can handle new position
        test_capital = portfolio.equity * 0.10  # Rough estimate
        if not portfolio.can_open_position(test_capital):
            logger.debug("Portfolio cannot open new position (limits reached)")
            return False
        
        return True
    
    def _determine_side(self, event: Event) -> PositionSide:
        """Determine which side to take (YES or NO)."""
        # If our probability > market price, buy YES
        # If our probability < market price, buy NO
        
        if event.research_probability > event.market.yes_price:
            return PositionSide.YES
        else:
            return PositionSide.NO
    
    def _calculate_kelly(self, event: Event, side: PositionSide) -> float:
        """Calculate Kelly Criterion fraction.
        
        Kelly formula: f = (bp - q) / b
        where:
        - b = odds received on the bet (payout)
        - p = probability of winning
        - q = probability of losing (1 - p)
        """
        if side == PositionSide.YES:
            # Buying YES
            p = event.research_probability  # Our probability of YES
            market_price = event.market.yes_price
        else:
            # Buying NO
            p = 1 - event.research_probability  # Our probability of NO
            market_price = event.market.no_price
        
        if market_price >= 1.0 or market_price <= 0:
            return 0.0
        
        # Payout odds
        b = (1 - market_price) / market_price
        
        # Kelly fraction
        q = 1 - p
        kelly = (b * p - q) / b
        
        # Ensure non-negative
        kelly = max(0.0, kelly)
        
        logger.debug(f"Kelly calculation: p={p:.2%}, market={market_price:.2%}, b={b:.2f}, kelly={kelly:.2%}")
        
        return kelly
    
    def _apply_limits(self, kelly_fraction: float) -> float:
        """Apply safety limits to Kelly fraction."""
        # Use fractional Kelly (1/2 Kelly or 1/4 Kelly for safety)
        fraction = kelly_fraction * 0.5  # Half Kelly
        
        # Apply maximum position size limit
        fraction = min(fraction, settings.max_position_size)
        
        # Apply minimum (don't bother with tiny positions)
        if fraction < 0.02:  # Less than 2%
            return 0.0
        
        return fraction
    
    def _calculate_exit_levels(
        self, 
        entry_price: float, 
        side: PositionSide
    ) -> tuple[float, float]:
        """Calculate stop loss and take profit levels."""
        if side == PositionSide.YES:
            # For YES positions
            stop_loss = entry_price * (1 - settings.stop_loss_pct)
            take_profit = entry_price * (1 + settings.take_profit_pct)
        else:
            # For NO positions
            stop_loss = entry_price * (1 + settings.stop_loss_pct)
            take_profit = entry_price * (1 - settings.take_profit_pct)
        
        # Clamp to [0, 1] for probability prices
        stop_loss = max(0.01, min(0.99, stop_loss))
        take_profit = max(0.01, min(0.99, take_profit))
        
        return stop_loss, take_profit
    
    def create_position(
        self, 
        event: Event, 
        sizing: Dict
    ) -> Position:
        """Create a Position object from sizing recommendation."""
        position = Position(
            id=str(uuid.uuid4()),
            market_id=event.market.id,
            question=event.market.question,
            side=sizing["side"],
            shares=sizing["shares"],
            entry_price=sizing["entry_price"],
            capital_allocated=sizing["capital"],
            stop_loss=sizing["stop_loss"],
            take_profit=sizing["take_profit"]
        )
        
        return position
