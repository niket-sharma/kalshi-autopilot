"""Position tracking models."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PositionSide(str, Enum):
    """Position side (direction)."""
    YES = "yes"  # Buying 'Yes' shares
    NO = "no"    # Buying 'No' shares


class PositionStatus(str, Enum):
    """Position status."""
    OPEN = "open"
    CLOSED = "closed"
    STOPPED = "stopped"  # Hit stop loss


class Position(BaseModel):
    """Trading position."""
    id: str = Field(..., description="Position ID")
    market_id: str = Field(..., description="Market ID")
    question: str = Field(..., description="Market question")
    
    # Position details
    side: PositionSide
    shares: float = Field(..., description="Number of shares")
    entry_price: float = Field(..., description="Entry price per share")
    current_price: Optional[float] = None
    
    # Capital
    capital_allocated: float = Field(..., description="Total USDC invested")
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Status
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    # P&L
    realized_pnl: float = 0.0
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L."""
        if self.current_price is None or self.status != PositionStatus.OPEN:
            return 0.0
        
        # P&L = (current_price - entry_price) * shares
        return (self.current_price - self.entry_price) * self.shares
    
    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)."""
        return self.realized_pnl + self.unrealized_pnl
    
    @property
    def pnl_percent(self) -> float:
        """P&L as percentage of capital allocated."""
        if self.capital_allocated == 0:
            return 0.0
        return (self.total_pnl / self.capital_allocated) * 100
    
    @property
    def current_value(self) -> float:
        """Current value of position."""
        if self.current_price is None:
            return self.capital_allocated
        return self.shares * self.current_price
    
    def check_stop_loss(self) -> bool:
        """Check if stop loss is hit."""
        if self.stop_loss is None or self.current_price is None:
            return False
        
        if self.side == PositionSide.YES:
            return self.current_price <= self.stop_loss
        else:  # NO side
            return self.current_price >= self.stop_loss
    
    def check_take_profit(self) -> bool:
        """Check if take profit is hit."""
        if self.take_profit is None or self.current_price is None:
            return False
        
        if self.side == PositionSide.YES:
            return self.current_price >= self.take_profit
        else:  # NO side
            return self.current_price <= self.take_profit
    
    def close(self, exit_price: float) -> float:
        """Close position and return realized P&L."""
        self.current_price = exit_price
        self.realized_pnl = (exit_price - self.entry_price) * self.shares
        self.status = PositionStatus.CLOSED
        self.closed_at = datetime.utcnow()
        return self.realized_pnl
