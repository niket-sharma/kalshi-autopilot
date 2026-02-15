"""Layer 1: Pure Python market filters - No LLM calls."""
from models import Market
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketFilter:
    """Fast pre-filtering to eliminate obviously bad markets."""
    
    def __init__(
        self,
        min_liquidity: float = 5000,
        min_volume: float = 10000,
        min_days_to_close: int = 2,
        max_price: float = 0.85,
        min_price: float = 0.15,
        max_spread: float = 0.05
    ):
        self.min_liquidity = min_liquidity
        self.min_volume = min_volume
        self.min_days_to_close = min_days_to_close
        self.max_price = max_price
        self.min_price = min_price
        self.max_spread = max_spread
        
    def filter_markets(self, markets: List[Market]) -> List[Market]:
        """Apply all filters and return passing markets.
        
        Args:
            markets: List of markets to filter
            
        Returns:
            Filtered list of markets
        """
        filtered = []
        stats = {
            'total': len(markets),
            'passed': 0,
            'failed_liquidity': 0,
            'failed_volume': 0,
            'failed_time': 0,
            'failed_price_extreme': 0,
            'failed_spread': 0
        }
        
        for market in markets:
            result, reason = self._check_market(market)
            if result:
                filtered.append(market)
                stats['passed'] += 1
            else:
                stats[f'failed_{reason}'] += 1
        
        # Log statistics
        logger.info(f"📊 Filter Results: {stats['passed']}/{stats['total']} markets passed")
        logger.debug(f"   Filters: {stats}")
        
        return filtered
    
    def _check_market(self, market: Market) -> tuple[bool, str]:
        """Check if a single market passes all filters.
        
        Returns:
            (passed: bool, failure_reason: str)
        """
        # 1. Liquidity check
        if market.liquidity < self.min_liquidity:
            return False, "liquidity"
        
        # 2. Volume check
        if market.volume < self.min_volume:
            return False, "volume"
        
        # 3. Time-to-close check
        if market.end_date:
            days_left = (market.end_date - datetime.utcnow()).days
            if days_left < self.min_days_to_close:
                return False, "time"
        
        # 4. Price extremes (avoid consensus markets)
        yes_price = market.yes_price or 0.5
        if yes_price > self.max_price or yes_price < self.min_price:
            return False, "price_extreme"
        
        # 5. Spread check (if we have bid/ask data)
        # Note: We'll skip this for now since basic API doesn't provide bid/ask
        # Can add later with order book data
        
        return True, "passed"
    
    def get_filter_stats(self, markets: List[Market]) -> Dict[str, any]:
        """Get detailed statistics about markets."""
        if not markets:
            return {}
        
        stats = {
            'count': len(markets),
            'avg_liquidity': sum(m.liquidity for m in markets) / len(markets),
            'avg_volume': sum(m.volume for m in markets) / len(markets),
            'avg_price': sum(m.yes_price or 0.5 for m in markets) / len(markets),
            'price_distribution': {
                'low': len([m for m in markets if (m.yes_price or 0.5) < 0.3]),
                'mid': len([m for m in markets if 0.3 <= (m.yes_price or 0.5) <= 0.7]),
                'high': len([m for m in markets if (m.yes_price or 0.5) > 0.7])
            }
        }
        
        return stats
