"""Pattern-based strategy that uses advanced detection with minimal LLM.

This combines proven Polymarket strategies with targeted LLM usage:
- Claude's logic: All pattern detection and scoring
- Gemini's role: Simple fact confirmation (yes/no, extract data)
"""

from models import Market
from .advanced_patterns import AdvancedPatternDetector
from .minimal_llm import MinimalLLMAnalyzer
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PatternBasedStrategy:
    """Smart strategy using pattern detection + minimal LLM confirmation."""
    
    def __init__(self):
        self.pattern_detector = AdvancedPatternDetector()
        self.llm = MinimalLLMAnalyzer()
        
        logger.info("🎯 Pattern-Based Strategy initialized")
        logger.info("   Uses: Advanced pattern detection + Gemini confirmation")
    
    def analyze_market(self, market: Market, news: Optional[str] = None) -> Dict:
        """Analyze market using patterns + minimal LLM.
        
        Workflow:
        1. Pattern detection (Claude's logic in Python)
        2. Gemini confirms simple facts (breaking news? yes/no)
        3. Combine signals for final decision
        
        Args:
            market: Market to analyze
            news: Optional news headline
            
        Returns:
            Analysis dict with probability, confidence, edge
        """
        logger.debug(f"Analyzing: {market.question[:50]}...")
        
        # Build context for pattern detection
        context = self._build_context(market, news)
        
        # Step 1: Run all pattern detectors (CLAUDE'S LOGIC)
        pattern_analysis = self.pattern_detector.analyze_all_patterns(market, context)
        
        logger.debug(f"  Pattern score: {pattern_analysis['combined_score']:.0f}/100")
        logger.debug(f"  Top pattern: {pattern_analysis['top_pattern']}")
        
        # Step 2: If patterns suggest opportunity, use Gemini for simple confirmations
        if pattern_analysis['combined_score'] > 40:
            gemini_confirms = self._get_gemini_confirmations(market, news, context)
            
            # Adjust pattern score based on confirmations
            if gemini_confirms.get('has_recent_news'):
                pattern_analysis['combined_score'] += 10
            
            if gemini_confirms.get('sentiment') == 'POSITIVE':
                pattern_analysis['combined_score'] += 5
        else:
            gemini_confirms = {}
        
        # Step 3: Convert to probability (CLAUDE'S LOGIC)
        probability = self._pattern_score_to_probability(
            pattern_analysis,
            market.yes_price or 0.5,
            gemini_confirms
        )
        
        # Step 4: Calculate edge and confidence
        market_price = market.yes_price or 0.5
        edge = abs(probability - market_price)
        confidence = pattern_analysis['combined_score'] / 100
        
        return {
            'probability': probability,
            'market_price': market_price,
            'edge': edge,
            'confidence': confidence,
            'pattern_analysis': pattern_analysis,
            'gemini_confirms': gemini_confirms,
            'should_trade': edge > 0.10 and confidence > 0.60
        }
    
    def _build_context(self, market: Market, news: Optional[str]) -> Dict:
        """Build context dict for pattern detection.
        
        This is where we'd add:
        - Historical price data (if available)
        - Volume history
        - News data
        - Cross-platform prices
        - etc.
        """
        context = {}
        
        # Add news context if available
        if news:
            context['breaking_news'] = True
            context['news_age_hours'] = 1  # Assume recent if provided
        
        # Add market timing context
        if market.end_date:
            from datetime import datetime
            hours_left = (market.end_date - datetime.utcnow()).total_seconds() / 3600
            context['hours_to_resolution'] = hours_left
        
        # TODO: Add more context as data becomes available:
        # - context['price_history'] = get_price_history(market.id)
        # - context['volume_history'] = get_volume_history(market.id)
        # - context['kalshi_price'] = get_kalshi_price(market)
        # - context['similar_markets'] = find_similar_markets(market)
        
        return context
    
    def _get_gemini_confirmations(self, market: Market, news: Optional[str], context: Dict) -> Dict:
        """Use Gemini for simple yes/no confirmations only.
        
        These are SIMPLE tasks - no reasoning required from Gemini.
        """
        confirmations = {}
        
        # Confirmation 1: Is there breaking news? (YES/NO)
        if news:
            sentiment = self.llm.binary_sentiment_check(market, news)
            confirmations['sentiment'] = sentiment
            confirmations['has_recent_news'] = True
        
        # Confirmation 2: Quick probability check (just a number)
        quick_prob = self.llm.quick_probability_check(market, news)
        confirmations['llm_probability'] = quick_prob.get('probability', 0.5)
        
        # Confirmation 3: Has event already happened? (YES/NO)
        if market.end_date and (market.end_date - datetime.utcnow()).days < 7:
            already_happened = self.llm.fact_check_resolved(market)
            confirmations['already_resolved'] = already_happened
        
        return confirmations
    
    def _pattern_score_to_probability(
        self, 
        pattern_analysis: Dict, 
        market_price: float,
        gemini_confirms: Dict
    ) -> float:
        """Convert pattern score to probability estimate.
        
        This is CLAUDE'S LOGIC - not Gemini's reasoning.
        """
        # Start with market price (assume market is somewhat efficient)
        probability = market_price
        
        # Get top pattern signal
        top_pattern = pattern_analysis['top_pattern']
        top_signal = pattern_analysis['signals'][top_pattern]
        
        # Adjust based on pattern type (CLAUDE'S STRATEGY)
        if top_pattern == 'mispricing':
            # Mispricing suggests market is wrong
            # Use LLM probability if available, otherwise use opposite of extremes
            if 'llm_probability' in gemini_confirms:
                probability = gemini_confirms['llm_probability']
            else:
                # If price is extreme, expect mean reversion
                if market_price > 0.75:
                    probability = market_price - 0.10
                elif market_price < 0.25:
                    probability = market_price + 0.10
        
        elif top_pattern == 'momentum':
            # Momentum suggests price will continue in direction
            direction = top_signal.get('direction', 'neutral')
            if direction == 'bullish':
                probability = min(market_price + 0.10, 0.95)
            elif direction == 'bearish':
                probability = max(market_price - 0.10, 0.05)
        
        elif top_pattern == 'reversal':
            # Reversal suggests price will reverse
            if market_price > 0.75:
                probability = market_price - 0.15
            elif market_price < 0.25:
                probability = market_price + 0.15
        
        elif top_pattern == 'arbitrage':
            # Arbitrage means we know the real price
            if 'kalshi_price' in gemini_confirms:
                # Use cross-platform price
                probability = gemini_confirms['kalshi_price']
        
        elif top_pattern == 'event_driven':
            # News-driven - use LLM probability if available
            if 'llm_probability' in gemini_confirms:
                # Blend LLM estimate with market price
                probability = (gemini_confirms['llm_probability'] + market_price) / 2
        
        # Sanity check: keep probability in valid range
        probability = max(0.05, min(0.95, probability))
        
        return probability
