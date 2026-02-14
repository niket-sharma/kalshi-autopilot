"""Research Agent - Analyzes events and estimates probabilities."""
from openai import OpenAI
from typing import Optional, Tuple
from models import Market, Event
from api import NewsAggregator
from config import settings
import logging

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent that researches events and estimates probabilities."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.news_aggregator = NewsAggregator()
        
    def analyze_market(self, market: Market) -> Event:
        """Analyze a market and estimate probability.
        
        Args:
            market: Market to analyze
            
        Returns:
            Event with analysis
        """
        logger.info(f"Analyzing market: {market.question}")
        
        # Step 1: Gather news context
        keywords = self.news_aggregator.extract_keywords(market.question)
        articles = self.news_aggregator.get_news_for_event(keywords)
        news_summary = self.news_aggregator.summarize_news(articles)
        
        # Step 2: Use GPT-4 to analyze and estimate probability
        probability, confidence, reasoning = self._estimate_probability(
            question=market.question,
            news_context=news_summary,
            current_price=market.yes_price
        )
        
        # Step 3: Create Event object
        event = Event(
            market=market,
            news_summary=news_summary,
            research_probability=probability,
            confidence=confidence
        )
        
        # Calculate edge
        event.calculate_edge()
        
        logger.info(
            f"Analysis complete - "
            f"Probability: {probability:.2%}, "
            f"Confidence: {confidence:.2%}, "
            f"Edge: {event.edge:.2%} "
            f"(Market: {market.yes_price:.2%})"
        )
        
        return event
    
    def _estimate_probability(
        self, 
        question: str, 
        news_context: str,
        current_price: Optional[float]
    ) -> Tuple[float, float, str]:
        """Use GPT-4 to estimate probability of event.
        
        Args:
            question: Market question
            news_context: News summary
            current_price: Current market price (implied probability)
            
        Returns:
            (probability, confidence, reasoning)
        """
        prompt = f"""You are an expert analyst for prediction markets. Analyze this event and provide your probability estimate.

Market Question: {question}

Current Market Price: {current_price:.2%} (implied probability)

Recent News Context:
{news_context}

Please analyze this event and provide:
1. Your estimated probability (0.0 to 1.0) that the answer is YES
2. Your confidence level (0.0 to 1.0) in this estimate
3. Brief reasoning (2-3 sentences)

Consider:
- Base rates and historical precedents
- Current news and developments
- Known unknowns and uncertainties
- Whether the market price seems mispriced

Format your response as:
PROBABILITY: 0.XX
CONFIDENCE: 0.XX
REASONING: Your reasoning here
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {"role": "system", "content": "You are an expert prediction market analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            probability = self._extract_value(content, "PROBABILITY")
            confidence = self._extract_value(content, "CONFIDENCE")
            reasoning = self._extract_reasoning(content)
            
            return probability, confidence, reasoning
            
        except Exception as e:
            logger.error(f"Failed to estimate probability: {e}")
            # Fallback: return market price with low confidence
            return current_price or 0.5, 0.3, "Analysis failed, using market price"
    
    def _extract_value(self, text: str, field: str) -> float:
        """Extract numerical value from GPT response."""
        try:
            for line in text.split("\n"):
                if field in line:
                    # Extract number
                    parts = line.split(":")
                    if len(parts) > 1:
                        value = float(parts[1].strip())
                        return max(0.0, min(1.0, value))  # Clamp to [0, 1]
        except:
            pass
        return 0.5  # Default to 50% if parsing fails
    
    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning from GPT response."""
        try:
            for line in text.split("\n"):
                if "REASONING" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        return parts[1].strip()
        except:
            pass
        return "No reasoning provided"
