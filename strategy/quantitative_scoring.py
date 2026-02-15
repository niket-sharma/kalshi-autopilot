"""Layer 2: Quantitative scoring - No LLM calls."""
from models import Market
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class QuantitativeScorer:
    """Calculate objective scores for markets based on data."""
    
    def __init__(
        self,
        min_score: float = 50.0,
        liquidity_weight: float = 0.25,
        volume_weight: float = 0.25,
        uncertainty_weight: float = 0.50
    ):
        self.min_score = min_score
        self.liquidity_weight = liquidity_weight
        self.volume_weight = volume_weight
        self.uncertainty_weight = uncertainty_weight
        
    def score_markets(self, markets: List[Market]) -> List[Tuple[Market, float]]:
        """Score markets and return sorted by score.
        
        Args:
            markets: List of markets to score
            
        Returns:
            List of (market, score) tuples, sorted by score descending
        """
        scored = []
        
        for market in markets:
            score = self._calculate_score(market)
            if score >= self.min_score:
                scored.append((market, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"📈 Scored {len(scored)}/{len(markets)} markets above threshold ({self.min_score})")
        
        return scored
    
    def _calculate_score(self, market: Market) -> float:
        """Calculate composite score for a market.
        
        Scoring components:
        1. Liquidity score (0-25): Higher liquidity = better
        2. Volume score (0-25): Higher volume = more activity
        3. Uncertainty score (0-50): Prices near 50% = maximum uncertainty/opportunity
        
        Returns:
            Score (0-100)
        """
        score = 0.0
        
        # 1. Liquidity score (0-25)
        # Scale: $0 = 0, $50k+ = 25
        liquidity_score = min(market.liquidity / 50000, 1.0) * 25
        score += liquidity_score * self.liquidity_weight / 0.25
        
        # 2. Volume score (0-25)
        # Scale: $0 = 0, $100k+ = 25
        volume_score = min(market.volume / 100000, 1.0) * 25
        score += volume_score * self.volume_weight / 0.25
        
        # 3. Uncertainty score (0-50)
        # Maximum score at 50%, decreases toward 0% or 100%
        yes_price = market.yes_price or 0.5
        
        # Distance from 50% (0.0 to 0.5)
        distance_from_midpoint = abs(yes_price - 0.5)
        
        # Convert to score: 0% distance = 50 points, 50% distance = 0 points
        uncertainty_score = (1 - distance_from_midpoint * 2) * 50
        score += uncertainty_score * self.uncertainty_weight / 0.50
        
        return score
    
    def get_market_features(self, market: Market) -> Dict[str, float]:
        """Extract quantitative features from a market.
        
        Returns:
            Dict of feature name -> value
        """
        yes_price = market.yes_price or 0.5
        
        features = {
            # Basic metrics
            'liquidity': market.liquidity,
            'volume': market.volume,
            'yes_price': yes_price,
            'no_price': 1 - yes_price,
            
            # Derived metrics
            'uncertainty': 1 - abs(yes_price - 0.5) * 2,  # 0-1, higher = more uncertain
            'price_distance_from_fair': abs(yes_price - 0.5),
            
            # Market quality
            'volume_to_liquidity_ratio': market.volume / market.liquidity if market.liquidity > 0 else 0,
            
            # Binary classification features
            'is_coin_flip': 0.4 <= yes_price <= 0.6,  # Near 50/50
            'is_likely_yes': yes_price > 0.7,
            'is_likely_no': yes_price < 0.3,
        }
        
        return features
    
    def detect_momentum(self, market: Market, historical_prices: List[float]) -> Dict[str, float]:
        """Detect price momentum (if historical data available).
        
        Args:
            market: Market to analyze
            historical_prices: List of prices over time (oldest to newest)
            
        Returns:
            Momentum metrics
        """
        if len(historical_prices) < 2:
            return {
                'momentum': 0.0,
                'volatility': 0.0,
                'trend': 'unknown'
            }
        
        # Calculate simple momentum
        recent_change = historical_prices[-1] - historical_prices[-2]
        
        # Calculate volatility (standard deviation)
        mean = sum(historical_prices) / len(historical_prices)
        variance = sum((p - mean) ** 2 for p in historical_prices) / len(historical_prices)
        volatility = variance ** 0.5
        
        # Determine trend
        if recent_change > 0.05:
            trend = 'bullish'
        elif recent_change < -0.05:
            trend = 'bearish'
        else:
            trend = 'sideways'
        
        return {
            'momentum': recent_change,
            'volatility': volatility,
            'trend': trend
        }
