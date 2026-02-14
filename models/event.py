"""Event and Market data models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MarketStatus(str, Enum):
    """Market status."""
    ACTIVE = "active"
    CLOSED = "closed"
    RESOLVED = "resolved"


class Outcome(BaseModel):
    """Market outcome option."""
    id: str
    title: str
    price: float  # Current price (probability in [0, 1])
    

class Market(BaseModel):
    """Polymarket market representation."""
    id: str = Field(..., description="Market condition ID")
    question: str = Field(..., description="Market question")
    description: Optional[str] = None
    outcomes: List[Outcome] = Field(default_factory=list)
    
    # Market metadata
    volume: float = 0.0
    liquidity: float = 0.0
    created_at: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: MarketStatus = MarketStatus.ACTIVE
    
    # Category/tags
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Derived metrics
    implied_probability: Optional[float] = None  # From prices
    
    @property
    def is_binary(self) -> bool:
        """Check if this is a binary market (Yes/No)."""
        return len(self.outcomes) == 2
    
    @property
    def yes_price(self) -> Optional[float]:
        """Get 'Yes' price for binary markets."""
        if not self.is_binary:
            return None
        for outcome in self.outcomes:
            if outcome.title.lower() in ["yes", "true"]:
                return outcome.price
        return None
    
    @property
    def no_price(self) -> Optional[float]:
        """Get 'No' price for binary markets."""
        if not self.is_binary:
            return None
        for outcome in self.outcomes:
            if outcome.title.lower() in ["no", "false"]:
                return outcome.price
        return None


class Event(BaseModel):
    """Real-world event with analysis context."""
    market: Market
    
    # Analysis context
    news_summary: Optional[str] = None
    sentiment_score: Optional[float] = None  # [-1, 1]
    key_developments: List[str] = Field(default_factory=list)
    
    # Agent analysis
    research_probability: Optional[float] = None  # Agent's estimated probability
    confidence: Optional[float] = None  # Agent's confidence [0, 1]
    edge: Optional[float] = None  # Difference between research_prob and market price
    
    # Metadata
    analyzed_at: Optional[datetime] = None
    
    def calculate_edge(self) -> Optional[float]:
        """Calculate edge: difference between research probability and market price."""
        if self.research_probability is None or self.market.yes_price is None:
            return None
        self.edge = abs(self.research_probability - self.market.yes_price)
        return self.edge
    
    @property
    def has_edge(self) -> bool:
        """Check if there's a tradeable edge."""
        from config import settings
        if self.edge is None:
            self.calculate_edge()
        return (self.edge or 0) >= settings.min_edge_threshold
    
    @property
    def is_confident(self) -> bool:
        """Check if confidence meets threshold."""
        from config import settings
        return (self.confidence or 0) >= settings.min_confidence
