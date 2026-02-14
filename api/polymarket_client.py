"""Polymarket CLOB API client."""
import requests
import hmac
import hashlib
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from config import settings
from models import Market, Outcome, MarketStatus
import logging

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Client for Polymarket CLOB API."""
    
    def __init__(self):
        self.clob_url = settings.polymarket_clob_url
        self.gamma_url = settings.polymarket_gamma_url
        self.api_key = settings.polymarket_api_key
        self.secret = settings.polymarket_secret
        self.session = requests.Session()
        
    def _sign_request(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Sign API request with HMAC."""
        timestamp = str(int(time.time() * 1000))
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "POLY-API-KEY": self.api_key,
            "POLY-SIGNATURE": signature,
            "POLY-TIMESTAMP": timestamp,
        }
    
    def get_markets(self, limit: int = 20, active_only: bool = True) -> List[Market]:
        """Fetch active markets from Polymarket.
        
        Args:
            limit: Maximum number of markets to return
            active_only: Only return active markets
            
        Returns:
            List of Market objects
        """
        try:
            # Use Gamma API for market data (public, no auth needed)
            url = f"{self.gamma_url}/markets"
            params = {
                "limit": limit,
                "active": active_only,
                "_type": "binary"  # Focus on binary markets (Yes/No)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            markets = []
            for item in data:
                try:
                    # Parse market data
                    market = self._parse_market(item)
                    if market:
                        markets.append(market)
                except Exception as e:
                    logger.warning(f"Failed to parse market: {e}")
                    continue
            
            logger.info(f"Fetched {len(markets)} markets from Polymarket")
            return markets
            
        except Exception as e:
            logger.error(f"Failed to fetch markets: {e}")
            return []
    
    def _parse_market(self, data: Dict[str, Any]) -> Optional[Market]:
        """Parse market data from API response."""
        try:
            # Extract outcomes
            outcomes = []
            if "outcomes" in data:
                for outcome_data in data["outcomes"]:
                    outcome = Outcome(
                        id=outcome_data.get("id", ""),
                        title=outcome_data.get("title", ""),
                        price=float(outcome_data.get("price", 0.5))
                    )
                    outcomes.append(outcome)
            
            # Parse timestamps
            created_at = None
            if "createdAt" in data:
                created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
            
            end_date = None
            if "endDate" in data:
                end_date = datetime.fromisoformat(data["endDate"].replace("Z", "+00:00"))
            
            # Determine status
            status = MarketStatus.ACTIVE
            if data.get("closed", False):
                status = MarketStatus.CLOSED
            elif data.get("resolved", False):
                status = MarketStatus.RESOLVED
            
            market = Market(
                id=data.get("conditionId", data.get("id", "")),
                question=data.get("question", ""),
                description=data.get("description"),
                outcomes=outcomes,
                volume=float(data.get("volume", 0)),
                liquidity=float(data.get("liquidity", 0)),
                created_at=created_at,
                end_date=end_date,
                status=status,
                category=data.get("category"),
                tags=data.get("tags", [])
            )
            
            # Calculate implied probability from Yes price
            if market.yes_price:
                market.implied_probability = market.yes_price
            
            return market
            
        except Exception as e:
            logger.error(f"Error parsing market: {e}")
            return None
    
    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        """Fetch a specific market by ID."""
        try:
            url = f"{self.gamma_url}/markets/{market_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_market(data)
        except Exception as e:
            logger.error(f"Failed to fetch market {market_id}: {e}")
            return None
    
    def get_high_volume_markets(self, min_volume: float = 10000, limit: int = 10) -> List[Market]:
        """Get high-volume markets (most liquid/active)."""
        all_markets = self.get_markets(limit=50, active_only=True)
        
        # Filter by minimum volume
        high_vol = [m for m in all_markets if m.volume >= min_volume]
        
        # Sort by volume descending
        high_vol.sort(key=lambda m: m.volume, reverse=True)
        
        return high_vol[:limit]
    
    def place_order(self, market_id: str, side: str, size: float, price: float) -> Optional[Dict]:
        """Place an order on Polymarket (LIVE MODE ONLY).
        
        Args:
            market_id: Market condition ID
            side: "BUY" or "SELL"
            size: Number of shares
            price: Price per share (0-1)
            
        Returns:
            Order response or None if failed
        """
        if settings.is_test_mode:
            logger.info(f"[TEST MODE] Would place order: {side} {size} shares at ${price} on market {market_id}")
            return {
                "success": True,
                "test_mode": True,
                "order_id": f"test_{int(time.time())}"
            }
        
        try:
            # Real order placement would go here
            # This requires more setup (wallet signing, etc.)
            logger.warning("Live trading not yet implemented - use test mode")
            return None
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
