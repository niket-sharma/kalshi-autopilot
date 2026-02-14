"""Configuration management for Polymarket Autopilot."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Polymarket API
    polymarket_api_key: str = ""
    polymarket_secret: str = ""
    polymarket_private_key: str = ""
    polymarket_proxy_address: str = ""
    
    # AI Model Configuration
    ai_provider: str = "gemini"  # gemini, openai, or anthropic
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # News API (optional)
    news_api_key: str = ""
    
    # Trading Configuration
    initial_capital: float = 25.0
    max_position_size: float = 0.15  # 15% of capital
    risk_per_trade: float = 0.05  # 5% risk
    max_concurrent_positions: int = 3
    auto_compound: bool = True
    min_edge_threshold: float = 0.10  # 10% edge required
    min_confidence: float = 0.70  # 70% confidence required
    
    # Risk Limits
    max_daily_loss: float = 0.10  # 10% max daily loss
    kill_switch_drawdown: float = 0.20  # 20% drawdown kills trading
    stop_loss_pct: float = 0.20  # 20% stop loss
    take_profit_pct: float = 1.0  # 100% profit target
    
    # Monitoring
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    # Execution Mode
    mode: Literal["test", "live"] = "test"
    
    # URLs
    polymarket_clob_url: str = "https://clob.polymarket.com"
    polymarket_gamma_url: str = "https://gamma-api.polymarket.com"
    
    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return self.mode == "test"


# Global settings instance
settings = Settings()
