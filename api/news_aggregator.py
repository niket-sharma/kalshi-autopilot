"""News aggregation for event context."""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import settings
import logging

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Aggregates news for market context."""
    
    def __init__(self):
        self.news_api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
        
    def get_news_for_event(self, query: str, days_back: int = 3, max_results: int = 10) -> List[Dict]:
        """Fetch recent news articles related to an event.
        
        Args:
            query: Search query (event keywords)
            days_back: How many days back to search
            max_results: Maximum number of articles
            
        Returns:
            List of news articles
        """
        if not self.news_api_key:
            logger.warning("No NEWS_API_KEY configured, skipping news fetch")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "relevancy",
                "pageSize": max_results,
                "apiKey": self.news_api_key,
                "language": "en"
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            logger.info(f"Found {len(articles)} news articles for query: {query}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return []
    
    def summarize_news(self, articles: List[Dict]) -> str:
        """Create a brief summary from news articles.
        
        Args:
            articles: List of news article dicts
            
        Returns:
            Text summary
        """
        if not articles:
            return "No recent news found."
        
        summaries = []
        for article in articles[:5]:  # Top 5 articles
            title = article.get("title", "")
            description = article.get("description", "")
            source = article.get("source", {}).get("name", "Unknown")
            
            if title:
                summary = f"• [{source}] {title}"
                if description:
                    summary += f": {description[:100]}..."
                summaries.append(summary)
        
        return "\n".join(summaries)
    
    def extract_keywords(self, question: str) -> str:
        """Extract search keywords from a market question.
        
        Args:
            question: Market question
            
        Returns:
            Search query string
        """
        # Simple keyword extraction (could be improved with NLP)
        # Remove common words
        stop_words = {"will", "be", "the", "a", "an", "in", "on", "at", "to", "by", "for", "of", "or", "and"}
        
        words = question.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Take first 4-5 keywords
        return " ".join(keywords[:5])
