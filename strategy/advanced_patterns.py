"""Advanced trading patterns based on research of successful Polymarket bots.

This module implements proven strategies from:
- Official Polymarket agents repo
- Top performing trading bots
- Prediction market academic research
"""

from models import Market, Event
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AdvancedPatternDetector:
    """Detects profitable patterns based on proven Polymarket strategies."""
    
    def __init__(self):
        self.patterns = {
            'mispricing': MispricingDetector(),
            'momentum': MomentumDetector(),
            'reversal': ReversalDetector(),
            'arbitrage': ArbitrageDetector(),
            'event_driven': EventDrivenDetector()
        }
    
    def analyze_all_patterns(self, market: Market, context: Dict) -> Dict[str, any]:
        """Run all pattern detectors and combine signals.
        
        Args:
            market: Market to analyze
            context: Additional context (news, historical data, etc.)
            
        Returns:
            Dict with pattern signals and combined score
        """
        signals = {}
        
        for pattern_name, detector in self.patterns.items():
            signal = detector.detect(market, context)
            signals[pattern_name] = signal
        
        # Combine signals with weights
        combined_score = self._combine_signals(signals)
        
        return {
            'signals': signals,
            'combined_score': combined_score,
            'top_pattern': max(signals.items(), key=lambda x: x[1]['confidence'])[0],
            'should_trade': combined_score > 70
        }
    
    def _combine_signals(self, signals: Dict) -> float:
        """Combine multiple pattern signals into single score.
        
        Uses weighted average based on pattern reliability.
        """
        weights = {
            'mispricing': 0.35,  # Most reliable
            'arbitrage': 0.25,   # Second most reliable
            'momentum': 0.20,    # Trend following
            'event_driven': 0.15,  # News impact
            'reversal': 0.05     # Contrarian (risky)
        }
        
        score = 0.0
        for pattern, weight in weights.items():
            if pattern in signals:
                score += signals[pattern]['score'] * weight
        
        return score


class MispricingDetector:
    """Detect markets where price doesn't reflect true probability.
    
    Based on research: Markets often misprice when:
    - Low liquidity (few informed traders)
    - Recent news not yet priced in
    - Complex events (hard to evaluate)
    """
    
    def detect(self, market: Market, context: Dict) -> Dict:
        score = 0.0
        reasons = []
        
        # Pattern 1: Low liquidity + extreme price = potential mispricing
        if market.liquidity < 10000 and (market.yes_price < 0.20 or market.yes_price > 0.80):
            score += 30
            reasons.append("Low liquidity with extreme price")
        
        # Pattern 2: High volume spike without price change = information lag
        if context.get('volume_spike') and context.get('low_price_change'):
            score += 25
            reasons.append("Volume spike without price adjustment")
        
        # Pattern 3: Similar events priced differently
        if 'similar_markets' in context:
            price_variance = self._check_similar_market_prices(market, context['similar_markets'])
            if price_variance > 0.15:  # More than 15% variance
                score += 20
                reasons.append(f"Price variance with similar markets: {price_variance:.0%}")
        
        # Pattern 4: Resolved similar events suggest different probability
        if 'historical_outcomes' in context:
            historical_edge = self._compare_to_history(market, context['historical_outcomes'])
            score += min(historical_edge * 100, 25)
            if historical_edge > 0.10:
                reasons.append(f"Historical data suggests {historical_edge:.0%} edge")
        
        return {
            'score': min(score, 100),
            'confidence': min(score / 100, 1.0),
            'reasons': reasons,
            'pattern': 'mispricing'
        }
    
    def _check_similar_market_prices(self, market: Market, similar: List[Market]) -> float:
        """Check if similar markets have different prices."""
        if not similar:
            return 0.0
        
        avg_price = sum(m.yes_price or 0.5 for m in similar) / len(similar)
        return abs((market.yes_price or 0.5) - avg_price)
    
    def _compare_to_history(self, market: Market, historical: List[Dict]) -> float:
        """Compare current price to historical outcome rate."""
        if not historical:
            return 0.0
        
        # Calculate actual outcome rate from similar historical events
        yes_outcomes = sum(1 for h in historical if h['outcome'] == 'YES')
        historical_probability = yes_outcomes / len(historical)
        
        return abs(historical_probability - (market.yes_price or 0.5))


class MomentumDetector:
    """Detect strong trends in market prices.
    
    Momentum strategy: Trade with the trend
    - Rising prices → likely to continue rising
    - Falling prices → likely to continue falling
    """
    
    def detect(self, market: Market, context: Dict) -> Dict:
        score = 0.0
        reasons = []
        
        # Need historical price data
        if 'price_history' not in context or len(context['price_history']) < 5:
            return {'score': 0, 'confidence': 0, 'reasons': ['No price history'], 'pattern': 'momentum'}
        
        prices = context['price_history']
        
        # Pattern 1: Consistent price direction over multiple periods
        direction_changes = sum(1 for i in range(1, len(prices)) 
                               if (prices[i] - prices[i-1]) * (prices[i-1] - prices[i-2]) < 0)
        
        if direction_changes == 0:  # No direction changes = strong trend
            score += 40
            trend = "upward" if prices[-1] > prices[0] else "downward"
            reasons.append(f"Strong {trend} trend with no reversals")
        
        # Pattern 2: Accelerating momentum
        recent_change = prices[-1] - prices[-2]
        previous_change = prices[-2] - prices[-3]
        
        if abs(recent_change) > abs(previous_change) * 1.5:  # Accelerating
            score += 30
            reasons.append("Accelerating momentum")
        
        # Pattern 3: Volume confirmation
        if 'volume_history' in context:
            if context['volume_history'][-1] > sum(context['volume_history'][:-1]) / len(context['volume_history'][:-1]):
                score += 20
                reasons.append("High volume confirms trend")
        
        # Calculate momentum strength
        total_change = abs(prices[-1] - prices[0])
        score += min(total_change * 100, 10)  # Up to 10 points for magnitude
        
        return {
            'score': min(score, 100),
            'confidence': min(score / 100, 1.0),
            'reasons': reasons,
            'pattern': 'momentum',
            'direction': 'bullish' if prices[-1] > prices[0] else 'bearish'
        }


class ReversalDetector:
    """Detect markets likely to reverse direction.
    
    Mean reversion strategy: Markets tend to return to fair value
    - Overextended trends → likely to reverse
    - Extreme prices → likely to correct
    """
    
    def detect(self, market: Market, context: Dict) -> Dict:
        score = 0.0
        reasons = []
        
        price = market.yes_price or 0.5
        
        # Pattern 1: Extreme price levels (>90% or <10%)
        if price > 0.90:
            score += 25
            reasons.append("Extremely high price (>90%) - potential reversal")
        elif price < 0.10:
            score += 25
            reasons.append("Extremely low price (<10%) - potential reversal")
        
        # Pattern 2: Recent rapid movement suggests overextension
        if 'price_history' in context and len(context['price_history']) >= 3:
            prices = context['price_history']
            recent_change = prices[-1] - prices[-3]
            
            if abs(recent_change) > 0.20:  # 20% move in short time
                score += 30
                reasons.append(f"Rapid price change ({recent_change:.0%}) suggests overextension")
        
        # Pattern 3: Low liquidity at extreme price = thin orderbook
        if (price > 0.85 or price < 0.15) and market.liquidity < 5000:
            score += 20
            reasons.append("Low liquidity at extreme price - vulnerable to reversal")
        
        # Pattern 4: Volume declining while price trending = weakening trend
        if 'volume_history' in context and len(context['volume_history']) >= 3:
            vols = context['volume_history']
            if vols[-1] < vols[-2] < vols[-3]:  # Declining volume
                score += 15
                reasons.append("Declining volume suggests trend exhaustion")
        
        return {
            'score': min(score, 100),
            'confidence': min(score / 100, 1.0),
            'reasons': reasons,
            'pattern': 'reversal'
        }


class ArbitrageDetector:
    """Detect arbitrage opportunities across markets/platforms.
    
    Cross-platform arbitrage:
    - Same event on Polymarket vs Kalshi vs PredictIt
    - Related events with logical price constraints
    """
    
    def detect(self, market: Market, context: Dict) -> Dict:
        score = 0.0
        reasons = []
        
        # Pattern 1: Cross-platform price differences
        if 'kalshi_price' in context:
            kalshi_price = context['kalshi_price']
            poly_price = market.yes_price or 0.5
            
            price_diff = abs(poly_price - kalshi_price)
            if price_diff > 0.05:  # 5% arbitrage opportunity
                score += 50
                reasons.append(f"Cross-platform arbitrage: {price_diff:.0%} difference")
        
        # Pattern 2: Correlated markets with price inconsistency
        if 'correlated_markets' in context:
            for correlated in context['correlated_markets']:
                # Example: "Team A wins" and "Team B loses" should sum to ~1.0
                expected_sum = correlated.get('expected_sum', 1.0)
                actual_sum = (market.yes_price or 0.5) + correlated['price']
                
                if abs(actual_sum - expected_sum) > 0.10:
                    score += 30
                    reasons.append(f"Correlated market inconsistency: {abs(actual_sum - expected_sum):.0%}")
        
        # Pattern 3: Time-based arbitrage (same event, different resolution dates)
        if 'time_series_markets' in context:
            # Earlier resolution should have higher certainty
            for ts_market in context['time_series_markets']:
                if ts_market['days_to_resolution'] < market.days_until_close:
                    if abs(ts_market['price'] - (market.yes_price or 0.5)) > 0.15:
                        score += 20
                        reasons.append("Time-series pricing inconsistency")
        
        return {
            'score': min(score, 100),
            'confidence': min(score / 100, 1.0),
            'reasons': reasons,
            'pattern': 'arbitrage'
        }


class EventDrivenDetector:
    """Detect markets likely to move on upcoming events.
    
    Event-driven strategy:
    - News announcements
    - Scheduled events (earnings, debates, matches)
    - Information releases
    """
    
    def detect(self, market: Market, context: Dict) -> Dict:
        score = 0.0
        reasons = []
        
        # Pattern 1: Recent breaking news
        if context.get('breaking_news'):
            news_age_hours = context.get('news_age_hours', 24)
            if news_age_hours < 2:  # Very recent news
                score += 40
                reasons.append("Breaking news in last 2 hours")
            elif news_age_hours < 12:
                score += 25
                reasons.append("Recent news in last 12 hours")
        
        # Pattern 2: Scheduled event approaching
        if market.end_date:
            hours_to_event = (market.end_date - datetime.utcnow()).total_seconds() / 3600
            
            if 1 < hours_to_event < 48:  # 1-48 hours before event
                score += 30
                reasons.append(f"Event in {hours_to_event:.0f} hours - high information flow expected")
        
        # Pattern 3: Social media sentiment spike
        if context.get('social_sentiment_spike'):
            score += 20
            reasons.append("Social media activity spike detected")
        
        # Pattern 4: Expert/influencer commentary
        if context.get('expert_mentions'):
            score += 15
            reasons.append("Expert commentary detected")
        
        return {
            'score': min(score, 100),
            'confidence': min(score / 100, 1.0),
            'reasons': reasons,
            'pattern': 'event_driven'
        }
