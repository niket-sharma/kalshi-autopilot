"""Polymarket CLOB API client using py-clob-client."""
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from typing import List, Dict, Optional, Any
from datetime import datetime
from config import settings
from models import Market, Outcome, MarketStatus
import logging

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Client for Polymarket CLOB using wallet-based trading."""
    
    def __init__(self):
        # Initialize CLOB client with private key
        host = "https://clob.polymarket.com"
        chain_id = 137  # Polygon mainnet
        
        try:
            self.client = ClobClient(
                host=host,
                key=settings.polymarket_private_key,
                chain_id=chain_id
            )
            logger.info("✅ Polymarket client initialized with wallet")
            
            # Get wallet address
            self.address = self.client.get_address()
            logger.info(f"📍 Wallet address: {self.address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Polymarket client: {e}")
            raise
        
    def get_markets(self, limit: int = 20, active_only: bool = True) -> List[Market]:
        """Fetch active markets from Polymarket.
        
        Args:
            limit: Maximum number of markets to return
            active_only: Only return active markets
            
        Returns:
            List of Market objects
        """
        try:
            # Get markets (returns dict with 'data' key)
            response = self.client.get_markets()
            markets_data = response.get('data', [])
            
            markets = []
            for item in markets_data[:limit]:
                try:
                    market = self._parse_market(item)
                    if market:
                        # Filter for active only if needed
                        if not active_only or market.status == MarketStatus.ACTIVE:
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
        """Parse market data from CLOB API response."""
        try:
            # Extract basic info
            market_id = data.get("condition_id", "")
            question = data.get("question", "")
            
            # Parse outcomes
            outcomes = []
            tokens = data.get("tokens", [])
            for token_data in tokens:
                outcome = Outcome(
                    id=token_data.get("token_id", ""),
                    title=token_data.get("outcome", ""),
                    price=float(token_data.get("price", 0.5))
                )
                outcomes.append(outcome)
            
            # Parse status
            status = MarketStatus.ACTIVE
            if data.get("closed", False):
                status = MarketStatus.CLOSED
            elif data.get("resolved", False):
                status = MarketStatus.RESOLVED
            
            # Create market object
            market = Market(
                id=market_id,
                question=question,
                description=data.get("description"),
                outcomes=outcomes,
                volume=float(data.get("volume", 0)),
                liquidity=float(data.get("liquidity", 0)),
                status=status,
                category=data.get("category"),
                tags=data.get("tags", [])
            )
            
            # Set implied probability from first outcome (YES)
            if outcomes:
                market.implied_probability = outcomes[0].price
            
            return market
            
        except Exception as e:
            logger.error(f"Error parsing market: {e}")
            return None
    
    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        """Fetch a specific market by ID."""
        try:
            # Get market data
            market_data = self.client.get_market(market_id)
            if market_data:
                return self._parse_market(market_data)
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
    
    def place_order(
        self, 
        token_id: str,
        side: str,
        size: float,
        price: float
    ) -> Optional[Dict]:
        """Place an order on Polymarket.
        
        Args:
            token_id: Token ID to trade
            side: "BUY" or "SELL"
            size: Number of shares
            price: Price per share (0-1)
            
        Returns:
            Order response or None if failed
        """
        if settings.is_test_mode:
            logger.info(
                f"[TEST MODE] Would place order: {side} {size} shares "
                f"at ${price:.3f} (token: {token_id})"
            )
            return {
                "success": True,
                "test_mode": True,
                "order_id": f"test_{int(datetime.utcnow().timestamp())}"
            }
        
        try:
            # Create order arguments
            order_args = OrderArgs(
                token_id=token_id,
                price=price,
                size=size,
                side=side.upper(),
                order_type=OrderType.GTC  # Good-til-cancelled
            )
            
            # Place order
            signed_order = self.client.create_order(order_args)
            resp = self.client.post_order(signed_order)
            
            logger.info(f"✅ Order placed: {resp.get('orderID', 'unknown')}")
            return resp
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def get_balance(self) -> float:
        """Get USDC balance."""
        try:
            balances = self.client.get_balances()
            usdc_balance = balances.get("USDC", 0)
            logger.info(f"💰 USDC Balance: ${usdc_balance:.2f}")
            return float(usdc_balance)
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0
