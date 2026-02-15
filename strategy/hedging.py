"""Hedging system for low-confidence positions.

Inspired by OctagonAI/kalshi-deep-trading-bot:
- Auto-hedge trades with confidence < 60%
- Configurable hedge ratio (default 25%)
- Provides downside protection
"""
from typing import Dict, Optional
from models import Position
import logging

logger = logging.getLogger(__name__)


class HedgingManager:
    """Manages automatic hedging for risk protection."""
    
    def __init__(
        self,
        min_confidence_for_hedging: float = 0.60,
        default_hedge_ratio: float = 0.25,
        max_hedge_amount: float = 50.0
    ):
        """Initialize hedging manager.
        
        Args:
            min_confidence_for_hedging: Only hedge below this confidence
            default_hedge_ratio: Portion of position to hedge (0.25 = 25%)
            max_hedge_amount: Maximum dollar amount for hedge
        """
        self.min_confidence = min_confidence_for_hedging
        self.default_ratio = default_hedge_ratio
        self.max_hedge = max_hedge_amount
        
        logger.info(f"🛡️ Hedging Manager initialized")
        logger.info(f"   Min confidence for hedging: {min_confidence_for_hedging:.0%}")
        logger.info(f"   Default hedge ratio: {default_hedge_ratio:.0%}")
        logger.info(f"   Max hedge amount: ${max_hedge_amount:.2f}")
    
    def should_hedge(self, confidence: float, position_size: float) -> bool:
        """Check if position should be hedged.
        
        Args:
            confidence: Model confidence (0.0 - 1.0)
            position_size: Dollar amount of position
            
        Returns:
            True if position should be hedged
        """
        # Only hedge low-confidence trades
        if confidence >= self.min_confidence:
            return False
        
        # Don't hedge very small positions (not worth it)
        if position_size < 10.0:
            return False
        
        return True
    
    def calculate_hedge(
        self, 
        position_size: float, 
        confidence: float,
        custom_ratio: Optional[float] = None
    ) -> Dict:
        """Calculate hedge parameters for a position.
        
        Args:
            position_size: Dollar amount of main position
            confidence: Model confidence (0.0 - 1.0)
            custom_ratio: Optional custom hedge ratio
            
        Returns:
            Dict with hedge details:
            {
                'should_hedge': bool,
                'hedge_size': float,
                'hedge_ratio': float,
                'reasoning': str
            }
        """
        # Check if hedging is needed
        if not self.should_hedge(confidence, position_size):
            return {
                'should_hedge': False,
                'hedge_size': 0.0,
                'hedge_ratio': 0.0,
                'reasoning': f"Confidence {confidence:.0%} > {self.min_confidence:.0%}"
            }
        
        # Use custom ratio or default
        hedge_ratio = custom_ratio if custom_ratio else self.default_ratio
        
        # Calculate hedge size
        hedge_size = position_size * hedge_ratio
        
        # Cap at max hedge amount
        if hedge_size > self.max_hedge:
            hedge_size = self.max_hedge
            actual_ratio = hedge_size / position_size
            logger.warning(
                f"   Hedge capped at ${self.max_hedge:.2f} "
                f"(ratio: {actual_ratio:.0%} vs target: {hedge_ratio:.0%})"
            )
            hedge_ratio = actual_ratio
        
        # Build reasoning
        confidence_gap = self.min_confidence - confidence
        reasoning = (
            f"Low confidence ({confidence:.0%}) detected. "
            f"Gap: {confidence_gap:.0%}. "
            f"Hedging {hedge_ratio:.0%} of position for downside protection."
        )
        
        logger.info(
            f"   🛡️ Hedge calculated: ${hedge_size:.2f} ({hedge_ratio:.0%} of ${position_size:.2f})"
        )
        
        return {
            'should_hedge': True,
            'hedge_size': hedge_size,
            'hedge_ratio': hedge_ratio,
            'reasoning': reasoning
        }
    
    def create_hedge_order(
        self,
        market_id: str,
        main_side: str,
        hedge_params: Dict
    ) -> Optional[Dict]:
        """Create hedge order parameters.
        
        Args:
            market_id: Market identifier
            main_side: 'YES' or 'NO' for main position
            hedge_params: Output from calculate_hedge()
            
        Returns:
            Order dict or None if no hedge needed
        """
        if not hedge_params.get('should_hedge'):
            return None
        
        # Opposite side for hedge
        hedge_side = 'NO' if main_side == 'YES' else 'YES'
        
        order = {
            'market_id': market_id,
            'side': hedge_side,
            'amount': hedge_params['hedge_size'],
            'is_hedge': True,
            'hedge_ratio': hedge_params['hedge_ratio'],
            'reasoning': hedge_params['reasoning']
        }
        
        logger.info(f"   📋 Hedge order created: {hedge_side} for ${order['amount']:.2f}")
        
        return order
    
    def calculate_hedged_pnl(
        self,
        main_position: float,
        hedge_position: float,
        outcome: str,
        main_side: str
    ) -> Dict:
        """Calculate P&L for a hedged position.
        
        Args:
            main_position: Dollar amount of main bet
            hedge_position: Dollar amount of hedge bet
            outcome: 'YES' or 'NO' (market resolution)
            main_side: 'YES' or 'NO' (our main bet side)
            
        Returns:
            Dict with P&L breakdown
        """
        # Determine winners
        main_wins = (outcome == main_side)
        hedge_wins = not main_wins
        
        # Calculate payouts
        main_payout = main_position if main_wins else 0.0
        hedge_payout = hedge_position if hedge_wins else 0.0
        
        # Total cost
        total_cost = main_position + hedge_position
        
        # Net P&L
        total_payout = main_payout + hedge_payout
        net_pnl = total_payout - total_cost
        
        # ROI
        roi = (net_pnl / total_cost) if total_cost > 0 else 0.0
        
        return {
            'main_payout': main_payout,
            'hedge_payout': hedge_payout,
            'total_cost': total_cost,
            'total_payout': total_payout,
            'net_pnl': net_pnl,
            'roi': roi,
            'protected_downside': hedge_payout > 0
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = HedgingManager()
    
    # Test case 1: Low confidence trade
    print("\n--- Test Case 1: Low Confidence (50%) ---")
    hedge_params = manager.calculate_hedge(
        position_size=100.0,
        confidence=0.50
    )
    print(f"Should hedge: {hedge_params['should_hedge']}")
    print(f"Hedge size: ${hedge_params['hedge_size']:.2f}")
    print(f"Reasoning: {hedge_params['reasoning']}")
    
    # Create hedge order
    hedge_order = manager.create_hedge_order(
        market_id="MARKET-123",
        main_side="YES",
        hedge_params=hedge_params
    )
    print(f"Hedge order: {hedge_order}")
    
    # Calculate hedged P&L
    print("\nIf market resolves YES (main bet wins):")
    pnl_yes = manager.calculate_hedged_pnl(100.0, 25.0, 'YES', 'YES')
    print(f"Net P&L: ${pnl_yes['net_pnl']:.2f} (ROI: {pnl_yes['roi']:.1%})")
    
    print("\nIf market resolves NO (hedge wins):")
    pnl_no = manager.calculate_hedged_pnl(100.0, 25.0, 'NO', 'YES')
    print(f"Net P&L: ${pnl_no['net_pnl']:.2f} (ROI: {pnl_no['roi']:.1%})")
    print(f"Protected downside: {pnl_no['protected_downside']}")
    
    # Test case 2: High confidence trade
    print("\n--- Test Case 2: High Confidence (80%) ---")
    hedge_params_2 = manager.calculate_hedge(
        position_size=100.0,
        confidence=0.80
    )
    print(f"Should hedge: {hedge_params_2['should_hedge']}")
    print(f"Reasoning: {hedge_params_2['reasoning']}")
