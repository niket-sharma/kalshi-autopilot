"""Kalshi API client with RSA signature authentication."""
import time
import base64
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from config import settings
from models import Market, Outcome, MarketStatus
import logging

logger = logging.getLogger(__name__)


class KalshiClient:
    """Client for Kalshi Exchange API with RSA signature authentication."""
    
    def __init__(self):
        # Kalshi API endpoints (NEW: moved to elections subdomain)
        if settings.is_test_mode:
            self.base_url = "https://demo-api.elections.kalshi.com"
            logger.info("Using Kalshi DEMO API (paper trading)")
        else:
            self.base_url = "https://api.elections.kalshi.com"
            logger.info("Using Kalshi LIVE API")
        
        self.api_key = settings.kalshi_api_key
        
        # Load private key from file
        self.private_key = self._load_private_key()
        
        self.session = requests.Session()
        
        logger.info("✅ Kalshi client initialized with RSA authentication")
        
    def _load_private_key(self):
        """Load RSA private key from file."""
        try:
            key_path = Path(settings.kalshi_private_key_path)
            if not key_path.is_absolute():
                # If relative path, look in project directory
                key_path = Path(__file__).parent.parent / settings.kalshi_private_key_path
            
            with open(key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            
            logger.info(f"✅ Loaded private key from {key_path}")
            return private_key
            
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise
    
    def _sign_message(self, message: str) -> str:
        """Sign a message using RSA private key."""
        try:
            signature = self.private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode()
        except Exception as e:
            logger.error(f"Error signing message: {e}")
            raise
    
    def _get_headers(self, method: str, path: str) -> Dict[str, str]:
        """Generate headers with RSA signature."""
        timestamp = str(int(time.time() * 1000))
        
        # Create message to sign: timestamp + method + path
        message = f"{timestamp}{method}{path}"
        
        # Sign the message
        signature = self._sign_message(message)
        
        return {
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "Content-Type": "application/json"
        }
    
    def get_markets(self, limit: int = 20, active_only: bool = True) -> List[Market]:
        """Fetch active markets from Kalshi.
        
        Args:
            limit: Maximum number of markets to return
            active_only: Only return active/open markets
            
        Returns:
            List of Market objects
        """
        try:
            path = "/trade-api/v2/markets"
            headers = self._get_headers("GET", path)
            
            params = {
                'limit': limit,
                'status': 'open' if active_only else None
            }
            
            response = self.session.get(
                f"{self.base_url}{path}",
                headers=headers,
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
            
            # Set implied probability only (yes_price is computed property)
            market.implied_probability = yes_price
            
            return market
            
        except Exception as e:
            logger.error(f"Error parsing market: {e}")
            return None
    
    def get_market_by_ticker(self, ticker: str) -> Optional[Market]:
        """Fetch a specific market by ticker."""
        try:
            path = f"/trade-api/v2/markets/{ticker}"
            headers = self._get_headers("GET", path)
            
            response = self.session.get(f"{self.base_url}{path}", headers=headers)
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
    
    def get_balance(self) -> float:
        """Get account balance in USD."""
        try:
            path = "/trade-api/v2/portfolio/balance"
            headers = self._get_headers("GET", path)
            
            response = self.session.get(f"{self.base_url}{path}", headers=headers)
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
            path = "/trade-api/v2/portfolio/positions"
            headers = self._get_headers("GET", path)
            
            response = self.session.get(f"{self.base_url}{path}", headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Kalshi returns "market_positions"
            positions = data.get('market_positions', [])
            logger.info(f"📋 Retrieved {len(positions)} positions")
            return positions
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    def place_order(
        self,
        ticker: str,
        side: str,
        amount: float
    ) -> Optional[Dict]:
        """Place a market order on Kalshi.
        
        Args:
            ticker: Market ticker
            side: "yes" or "no"
            amount: Dollar amount to spend
            
        Returns:
            Order response or None if failed
        """
        if settings.is_test_mode:
            logger.info(
                f"[TEST MODE] Would place order: {side.upper()} ${amount:.2f} "
                f"on {ticker}"
            )
            return {
                "success": True,
                "test_mode": True,
                "order_id": f"test_{int(time.time())}"
            }
        
        try:
            import uuid
            
            # Generate unique client order ID
            client_order_id = str(uuid.uuid4())
            
            # Convert dollar amount to cents
            buy_max_cost_cents = int(amount * 100)
            
            order_data = {
                "ticker": ticker,
                "side": side.lower(),
                "action": "buy",
                "type": "market",
                "client_order_id": client_order_id,
                "count": 1000,  # High count, limited by buy_max_cost
                "buy_max_cost": buy_max_cost_cents
            }
            
            path = "/trade-api/v2/portfolio/orders"
            headers = self._get_headers("POST", path)
            
            response = self.session.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=order_data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Order placed: {ticker} {side} ${amount}")
            return {
                "success": True,
                "order_id": result.get("order_id", ""),
                "client_order_id": client_order_id
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        """Get market by ID (ticker for Kalshi)."""
        return self.get_market_by_ticker(market_id)
