"""Layer 3: Minimal LLM calls - Simple binary questions only."""
import google.generativeai as genai
from models import Market
from typing import Dict, Optional
from config import settings
import logging
import re

logger = logging.getLogger(__name__)


class MinimalLLMAnalyzer:
    """Lightweight LLM analysis with minimal token usage."""
    
    def __init__(self):
        if settings.ai_provider == "gemini" and settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.provider = "gemini"
        else:
            raise ValueError("Gemini API key required for minimal LLM analysis")
    
    def quick_probability_check(
        self, 
        market: Market, 
        news_headline: Optional[str] = None
    ) -> Dict[str, any]:
        """Get a quick probability estimate with minimal tokens.
        
        Args:
            market: Market to analyze
            news_headline: Optional recent news headline
            
        Returns:
            Dict with probability, confidence, and whether to trade
        """
        # Build ultra-short prompt
        prompt = self._build_minimal_prompt(market, news_headline)
        
        try:
            # Generate with strict token limit
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': 20,  # Super short!
                    'temperature': 0.3  # More deterministic
                }
            )
            
            text = response.text.strip()
            
            # Parse response (expecting just a number 0-100)
            probability = self._parse_probability(text)
            
            # Calculate edge
            market_price = market.yes_price or 0.5
            edge = abs(probability - market_price)
            
            result = {
                'probability': probability,
                'market_price': market_price,
                'edge': edge,
                'should_trade': edge >= settings.min_edge_threshold,
                'confidence': 0.7,  # Fixed confidence for minimal mode
                'raw_response': text
            }
            
            logger.debug(
                f"LLM Check: {market.question[:50]}... "
                f"→ {probability:.0%} (market: {market_price:.0%}, edge: {edge:.0%})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Minimal LLM analysis failed: {e}")
            return {
                'probability': market.yes_price or 0.5,
                'market_price': market.yes_price or 0.5,
                'edge': 0.0,
                'should_trade': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _build_minimal_prompt(self, market: Market, news: Optional[str] = None) -> str:
        """Build the shortest possible prompt."""
        prompt = f"Question: {market.question}\n"
        
        if news:
            # Only include first 200 chars of news
            prompt += f"News: {news[:200]}\n"
        
        prompt += f"Market: {(market.yes_price or 0.5):.0%}\n"
        prompt += "\nYour estimate (0-100): "
        
        return prompt
    
    def _parse_probability(self, text: str) -> float:
        """Extract probability from LLM response.
        
        Args:
            text: Response text
            
        Returns:
            Probability as float (0.0 to 1.0)
        """
        # Try to find a number in the text
        numbers = re.findall(r'\d+', text)
        
        if numbers:
            # Take first number
            num = int(numbers[0])
            
            # Convert to 0-1 range
            if num > 1:  # Assume it's 0-100
                return min(100, max(0, num)) / 100
            else:  # Assume it's 0-1
                return min(1.0, max(0.0, num))
        
        # Fallback: return 0.5
        logger.warning(f"Could not parse probability from: {text}")
        return 0.5
    
    def binary_sentiment_check(self, market: Market, news: str) -> str:
        """Super fast sentiment check - one word answer.
        
        Args:
            market: Market
            news: News headlines
            
        Returns:
            "POSITIVE" or "NEGATIVE"
        """
        prompt = f"""Headlines: {news[:300]}

Question: {market.question}

Sentiment: POSITIVE or NEGATIVE?
Answer: """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'max_output_tokens': 3}
            )
            
            text = response.text.strip().upper()
            
            if "POSITIVE" in text:
                return "POSITIVE"
            elif "NEGATIVE" in text:
                return "NEGATIVE"
            else:
                return "NEUTRAL"
                
        except Exception as e:
            logger.error(f"Sentiment check failed: {e}")
            return "NEUTRAL"
    
    def fact_check_resolved(self, market: Market) -> bool:
        """Check if an event has already happened (avoid resolved markets).
        
        Args:
            market: Market to check
            
        Returns:
            True if already resolved/happened
        """
        prompt = f"""Question: {market.question}

Has this already happened or been resolved? Answer YES or NO.
Answer: """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'max_output_tokens': 5}
            )
            
            text = response.text.strip().upper()
            return "YES" in text
            
        except Exception as e:
            logger.error(f"Fact check failed: {e}")
            return False
