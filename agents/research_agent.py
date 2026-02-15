"""Research Agent - Analyzes events using 3-layer optimization."""
from typing import Optional, List
from models import Market, Event
from api import NewsAggregator
from strategy import MarketFilter, QuantitativeScorer, MinimalLLMAnalyzer
from config import settings
import logging

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent that researches events using optimized 3-layer approach."""
    
    def __init__(self):
        # Layer 1: Filters
        self.filter = MarketFilter(
            min_liquidity=5000,
            min_volume=10000,
            min_days_to_close=2,
            max_price=0.85,
            min_price=0.15
        )
        
        # Layer 2: Quantitative scorer
        self.scorer = QuantitativeScorer(
            min_score=50.0
        )
        
        # Layer 3: Minimal LLM
        self.llm = MinimalLLMAnalyzer()
        
        # News aggregator
        self.news_aggregator = NewsAggregator()
        
        logger.info("🧠 Research Agent initialized with 3-layer optimization")
        logger.info("   Layer 1: Python filters")
        logger.info("   Layer 2: Quantitative scoring")
        logger.info("   Layer 3: Minimal LLM calls")
    
    def analyze_markets(self, markets: List[Market]) -> List[Event]:
        """Analyze multiple markets efficiently.
        
        Uses 3-layer approach:
        1. Filter out bad markets (no LLM)
        2. Score remaining markets (no LLM)
        3. LLM analysis only for top candidates
        
        Args:
            markets: List of markets to analyze
            
        Returns:
            List of Event objects with analysis
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 Starting 3-Layer Market Analysis")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Total markets: {len(markets)}")
        
        # LAYER 1: Quick filters (Python only)
        logger.info("\n📍 LAYER 1: Applying filters...")
        filtered_markets = self.filter.filter_markets(markets)
        
        if not filtered_markets:
            logger.info("❌ No markets passed filters")
            return []
        
        # LAYER 2: Quantitative scoring (Python only)
        logger.info("\n📍 LAYER 2: Calculating scores...")
        scored_markets = self.scorer.score_markets(filtered_markets)
        
        if not scored_markets:
            logger.info("❌ No markets scored above threshold")
            return []
        
        # Take top 5 for LLM analysis
        top_markets = scored_markets[:5]
        logger.info(f"\n✅ Top {len(top_markets)} markets for LLM analysis:")
        for i, (market, score) in enumerate(top_markets, 1):
            logger.info(f"  {i}. Score {score:.1f}: {market.question[:60]}...")
        
        # LAYER 3: Minimal LLM analysis (only top candidates)
        logger.info("\n📍 LAYER 3: LLM analysis (minimal tokens)...")
        events = []
        
        for market, quant_score in top_markets:
            # Get news headline (just first one)
            keywords = self.news_aggregator.extract_keywords(market.question)
            articles = self.news_aggregator.get_news_for_event(keywords, days_back=1, max_results=1)
            news_headline = articles[0].get('title', '') if articles else None
            
            # Quick LLM check (minimal tokens)
            llm_result = self.llm.quick_probability_check(market, news_headline)
            
            # Create event
            event = Event(
                market=market,
                news_summary=news_headline or "No recent news",
                research_probability=llm_result['probability'],
                confidence=llm_result['confidence']
            )
            
            # Calculate edge
            event.calculate_edge()
            
            # Add quantitative score as metadata
            event.quant_score = quant_score
            
            if event.has_edge and event.is_confident:
                logger.info(
                    f"   ✅ {market.question[:50]}... "
                    f"Edge: {event.edge:.1%} (AI: {event.research_probability:.0%} vs Market: {market.yes_price:.0%})"
                )
                events.append(event)
            else:
                logger.debug(
                    f"   ❌ No trade: {market.question[:50]}... "
                    f"Edge: {event.edge:.1%}"
                )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📈 Analysis Complete:")
        logger.info(f"   Started with: {len(markets)} markets")
        logger.info(f"   After filters: {len(filtered_markets)}")
        logger.info(f"   After scoring: {len(scored_markets)}")
        logger.info(f"   LLM analyzed: {len(top_markets)}")
        logger.info(f"   Tradeable opportunities: {len(events)}")
        logger.info(f"{'='*60}\n")
        
        return events
    
    def analyze_market(self, market: Market) -> Event:
        """Analyze a single market (legacy method for compatibility).
        
        Args:
            market: Market to analyze
            
        Returns:
            Event with analysis
        """
        # Use optimized multi-market analyzer with single market
        events = self.analyze_markets([market])
        
        if events:
            return events[0]
        
        # If no trade found, still return event but with no edge
        return Event(
            market=market,
            news_summary="Filtered out by optimization",
            research_probability=market.yes_price or 0.5,
            confidence=0.0,
            edge=0.0
        )
