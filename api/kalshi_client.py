"""Kalshi API client for the CFTC-regulated prediction market exchange."""
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


class KalshiClient:
    """Client for Kalshi Exchange API - CFTC-regulated, legal in US."""
    
    def __init__(self):
        # Kalshi API endpoints
        if settings.is_test_mode:
            self.base_url = "https://demo-api.kalshi.co/trade-api/v2"
            logger.info("Using Kalshi DEMO API (paper trading)")
        else:
            self.base_url = "https://trading-api.kalshi.com/trade-api/v2"
            logger.info("Using Kalshi LIVE API")
        
        self.api_key = settings.kalshi_api_key
        self.api_secret = settings.kalshi_api_secret
        self.session = requests.Session()
        self.token = None
        
        # Login to get auth token
        if self.api_key and self.api_secret:
            self._login()
        
    def _login(self):
        """Login to Kalshi API and get auth token."""
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={
                    "email": self.api_key,
                    "password": self.api_secret
                }
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get('token')
            
            # Set auth header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            
            logger.info("✅ Logged in to Kalshi")
            
        except Exception as e:
            logger.error(f"Failed to login to Kalshi: {e}")
            raise
    
    def get_markets(self, limit: int = 20, active_only: bool = True) -> List[Market]:
        """Fetch active markets from Kalshi.
        
        Args:
            limit: Maximum number of markets to return
            active_only: Only return active/open markets
            
        Returns:
            List of Market objects
        """
        try:
            params = {
                'limit': limit,
                'status': 'open' if active_only else None
            }
            
            response = self.session.get(
                f"{self.base_url}/markets",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            markets = []
            for item in data.get('markets', []):
                try:
                    market = self._parse_market(item)
                    if market:
                        markets.append(market)
                except Exception as e:
                    logger.warning(f"Failed to parse market: {e}")
                    continue
            
            logger.info(f"Fetched {len(markets)} markets from Kalshi")
            return markets
            
        except Exception as e:
            logger.error(f"Failed to fetch markets: {e}")
            return []
    
    def _parse_market(self, data: Dict[str, Any]) -> Optional[Market]:
        """Parse market data from Kalshi API response."""
        try:
            # Kalshi markets are binary (Yes/No)
            ticker = data.get('ticker', '')
            title = data.get('title', '')
            subtitle = data.get('subtitle', '')
            question = f"{title}: {subtitle}" if subtitle else title
            
            # Get Yes price (Kalshi uses cents, 0-100)
            yes_bid = data.get('yes_bid', 0) / 100.0
            yes_ask = data.get('yes_ask', 100) / 100.0
            yes_price = (yes_bid + yes_ask) / 2  # Mid price
            
            # Create outcomes
            outcomes = [
                Outcome(id=f"{ticker}-YES", title="YES", price=yes_price),
                Outcome(id=f"{ticker}-NO", title="NO", price=1 - yes_price)
            ]
            
            # Parse status
            status_str = data.get('status', '').lower()
            if status_str == 'open':
                status = MarketStatus.ACTIVE
            elif status_str == 'closed':
                status = MarketStatus.CLOSED
            elif status_str == 'settled':
                status = MarketStatus.RESOLVED
            else:
                status = MarketStatus.ACTIVE
            
            # Parse end date
            end_date = None
            if 'close_time' in data:
                end_date = datetime.fromisoformat(data['close_time'].replace('Z', '+00:00'))
            
            market = Market(
                id=ticker,
                question=question,
                description=data.get('category'),
                outcomes=outcomes,
                volume=float(data.get('volume', 0)),
                liquidity=float(data.get('open_interest', 0)),
                created_at=None,
                end_date=end_date,
                status=status,
                category=data.get('category'),
                tags=data.get('tags', [])
            )
            
            market.implied_probability = yes_price
            
            return market
            
        except Exception as e:
            logger.error(f"Error parsing market: {e}")
            return None
    
    def get_market_by_ticker(self, ticker: str) -> Optional[Market]:
        """Fetch a specific market by ticker."""
        try:
            response = self.session.get(f"{self.base_url}/markets/{ticker}")
            response.raise_for_status()
            data = response.json()
            return self._parse_market(data.get('market', {}))
        except Exception as e:
            logger.error(f"Failed to fetch market {ticker}: {e}")
            return None
    
    def get_high_volume_markets(self, min_volume: float = 10000, limit: int = 10) -> List[Market]:
        """Get high-volume markets (most liquid/active)."""
        all_markets = self.get_markets(limit=100, active_only=True)
        
        # Filter by minimum volume
        high_vol = [m for m in all_markets if m.volume >= min_volume]
        
        # Sort by volume descending
        high_vol.sort(key=lambda m: m.volume, reverse=True)
        
        return high_vol[:limit]
    
    def place_order(
        self,
        ticker: str,
        side: str,
        quantity: int,
        price_cents: int
    ) -> Optional[Dict]:
        """Place an order on Kalshi.
        
        Args:
            ticker: Market ticker (e.g., "NASDAQ100Y-23DEC31-B10300")
            side: "yes" or "no"
            quantity: Number of contracts
            price_cents: Price in cents (1-99)
            
        Returns:
            Order response or None if failed
        """
        if settings.is_test_mode:
            logger.info(
                f"[TEST MODE] Would place order: {side.upper()} {quantity} contracts "
                f"at {price_cents}¢ (ticker: {ticker})"
            )
            return {
                "success": True,
                "test_mode": True,
                "order_id": f"test_{int(time.time())}"
            }
        
        try:
            order_data = {
                "ticker": ticker,
                "action": "buy",  # Always buying (YES or NO shares)
                "side": side.lower(),
                "type": "limit",
                "yes_price": price_cents if side.lower() == "yes" else None,
                "no_price": price_cents if side.lower() == "no" else None,
                "count": quantity
            }
            
            response = self.session.post(
                f"{self.base_url}/portfolio/orders",
                json=order_data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Order placed: {result.get('order_id', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def get_balance(self) -> float:
        """Get account balance in USD."""
        try:
            response = self.session.get(f"{self.base_url}/portfolio/balance")
            response.raise_for_status()
            data = response.json()
            balance = float(data.get('balance', 0)) / 100.0  # Convert cents to dollars
            logger.info(f"💰 Balance: ${balance:.2f}")
            return balance
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0
    
    def get_positions(self) -> List[Dict]:
        """Get current open positions."""
        try:
            response = self.session.get(f"{self.base_url}/portfolio/positions")
            response.raise_for_status()
            data = response.json()
            return data.get('positions', [])
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
