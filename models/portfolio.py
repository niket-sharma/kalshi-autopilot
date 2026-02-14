"""Portfolio management model."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, date
from .position import Position, PositionStatus


class Portfolio(BaseModel):
    """Trading portfolio tracker."""
    
    # Capital
    initial_capital: float
    current_capital: float
    
    # Positions
    positions: List[Position] = Field(default_factory=list)
    
    # Daily tracking
    daily_pnl: Dict[str, float] = Field(default_factory=dict)  # date -> pnl
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def open_positions(self) -> List[Position]:
        """Get all open positions."""
        return [p for p in self.positions if p.status == PositionStatus.OPEN]
    
    @property
    def closed_positions(self) -> List[Position]:
        """Get all closed positions."""
        return [p for p in self.positions if p.status != PositionStatus.OPEN]
    
    @property
    def total_allocated(self) -> float:
        """Total capital allocated to open positions."""
        return sum(p.capital_allocated for p in self.open_positions)
    
    @property
    def available_capital(self) -> float:
        """Available capital for new positions."""
        return self.current_capital - self.total_allocated
    
    @property
    def total_unrealized_pnl(self) -> float:
        """Total unrealized P&L from open positions."""
        return sum(p.unrealized_pnl for p in self.open_positions)
    
    @property
    def total_realized_pnl(self) -> float:
        """Total realized P&L from closed positions."""
        return sum(p.realized_pnl for p in self.closed_positions)
    
    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)."""
        return self.total_realized_pnl + self.total_unrealized_pnl
    
    @property
    def total_pnl_percent(self) -> float:
        """Total P&L as percentage of initial capital."""
        if self.initial_capital == 0:
            return 0.0
        return (self.total_pnl / self.initial_capital) * 100
    
    @property
    def equity(self) -> float:
        """Total portfolio equity (capital + unrealized P&L)."""
        return self.current_capital + self.total_unrealized_pnl
    
    @property
    def drawdown(self) -> float:
        """Current drawdown from peak equity."""
        peak = max(self.initial_capital, self.equity)
        if peak == 0:
            return 0.0
        return ((peak - self.equity) / peak) * 100
    
    def get_today_pnl(self) -> float:
        """Get today's P&L."""
        today = date.today().isoformat()
        return self.daily_pnl.get(today, 0.0)
    
    def update_daily_pnl(self):
        """Update today's P&L."""
        today = date.today().isoformat()
        self.daily_pnl[today] = self.total_pnl
        self.last_updated = datetime.utcnow()
    
    def can_open_position(self, capital_required: float) -> bool:
        """Check if we can open a new position."""
        from config import settings
        
        # Check available capital
        if capital_required > self.available_capital:
            return False
        
        # Check max concurrent positions
        if len(self.open_positions) >= settings.max_concurrent_positions:
            return False
        
        # Check daily loss limit
        today_pnl = self.get_today_pnl()
        max_loss = self.initial_capital * settings.max_daily_loss
        if today_pnl < -max_loss:
            return False
        
        # Check drawdown kill switch
        if self.drawdown >= settings.kill_switch_drawdown * 100:
            return False
        
        return True
    
    def add_position(self, position: Position):
        """Add a new position to portfolio."""
        self.positions.append(position)
        self.last_updated = datetime.utcnow()
    
    def close_position(self, position_id: str, exit_price: float) -> Optional[float]:
        """Close a position and update capital."""
        for position in self.positions:
            if position.id == position_id and position.status == PositionStatus.OPEN:
                pnl = position.close(exit_price)
                
                # Update capital
                self.current_capital += position.capital_allocated + pnl
                
                # Update daily P&L
                self.update_daily_pnl()
                
                return pnl
        return None
    
    def update_position_prices(self, market_prices: Dict[str, float]):
        """Update current prices for all open positions."""
        for position in self.open_positions:
            if position.market_id in market_prices:
                position.current_price = market_prices[position.market_id]
        
        self.update_daily_pnl()
