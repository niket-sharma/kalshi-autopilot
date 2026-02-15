# Kalshi Autopilot 🤖

**Autonomous AI trading agent for Kalshi prediction markets**

✅ **CFTC-Regulated & Legal in the US**

Uses multi-agent AI system to analyze events, assess probabilities, manage risk, and execute profitable trades automatically on Kalshi - the first CFTC-regulated prediction market exchange.

## 🎯 Features

- **Multi-Agent Architecture**: Research, Risk Management, and Execution agents
- **Event Analysis**: Real-time news + social sentiment analysis
- **Smart Risk Management**: Kelly Criterion, position sizing, portfolio limits
- **Autonomous Trading**: 24/7 market monitoring and execution
- **Profit Compounding**: Reinvests profits automatically
- **Real-time Monitoring**: Dashboard + alerts

## 🏗️ Architecture

```
Event Monitor → Research Agent → Risk Manager → Execution Agent
                      ↓               ↓              ↓
                   News API       Kelly Calc    Polymarket API
                   GPT-4          Position $     CLOB Orders
                   Sentiment      Stop Loss      Wallet (USDC)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Polymarket account + API credentials
- USDC on Polygon network
- OpenAI API key

### Installation
```bash
# Clone and setup
git clone https://github.com/niket-sharma/polymarket-autopilot.git
cd polymarket-autopilot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```bash
# .env
POLYMARKET_API_KEY=your_api_key
POLYMARKET_SECRET=your_secret
POLYMARKET_PRIVATE_KEY=your_wallet_private_key
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_news_api_key  # optional

# Trading config
INITIAL_CAPITAL=25.0
MAX_POSITION_SIZE=0.15  # 15% of capital per trade
RISK_PER_TRADE=0.05     # 5% risk per trade
AUTO_COMPOUND=true
```

### Run

**Test Mode (Paper Trading):**
```bash
python main.py --mode test
```

**Live Trading:**
```bash
python main.py --mode live
```

**Dashboard:**
```bash
streamlit run dashboard.py
```

## 📊 Multi-Agent System

### 1. Research Agent
- Monitors Polymarket markets
- Analyzes event context via GPT-4
- Aggregates news sentiment
- Calculates implied vs. real probability
- Identifies edge opportunities

### 2. Risk Manager
- Kelly Criterion for position sizing
- Portfolio concentration limits
- Stop-loss rules
- Profit-taking targets
- Drawdown protection

### 3. Execution Agent
- Places orders via Polymarket CLOB
- Manages open positions
- Tracks P&L
- Auto-compounds profits
- Sends alerts

## 🎓 Strategy

**Edge Detection:**
- Compare market odds vs. model probability
- Threshold: >10% edge required
- Confidence: >70% to enter

**Position Sizing:**
- Kelly Criterion: f = (bp - q) / b
- Max 15% per position
- Max 3 concurrent positions

**Risk Management:**
- Stop loss: 20% of position
- Take profit: 100% gain (2x)
- Max daily loss: 10% of capital
- Kill switch at -20% total drawdown

## 📁 Project Structure

```
polymarket-autopilot/
├── agents/
│   ├── research_agent.py      # Event analysis + probability
│   ├── risk_manager.py        # Position sizing + limits
│   ├── execution_agent.py     # Order placement
│   └── orchestrator.py        # Multi-agent coordination
├── api/
│   ├── polymarket_client.py   # CLOB API wrapper
│   └── news_aggregator.py     # News/sentiment data
├── models/
│   ├── event.py              # Market event data model
│   ├── position.py           # Position tracking
│   └── portfolio.py          # Portfolio management
├── strategy/
│   ├── probability.py        # Probability estimation
│   ├── edge_detector.py      # Edge calculation
│   └── kelly.py              # Kelly Criterion
├── monitoring/
│   ├── logger.py             # Trade logging
│   ├── alerter.py            # Notifications
│   └── dashboard.py          # Streamlit UI
├── tests/
├── main.py                   # Entry point
├── config.py                 # Configuration
├── requirements.txt
└── README.md
```

## ⚠️ Disclaimer

**This is experimental software for educational/research purposes.**

- Prediction markets involve risk of loss
- No guarantees of profit
- Start small ($25) and test thoroughly
- Review all trades before going live
- Use at your own risk

This is NOT financial advice. Do your own research.

## 📈 Roadmap

- [x] Multi-agent architecture
- [x] Polymarket API integration
- [x] Risk management system
- [ ] Live deployment
- [ ] Advanced ML models
- [ ] Cross-market arbitrage
- [ ] Telegram/Discord bot

## 🤝 Contributing

Open to contributions! Please open an issue first to discuss changes.

## 📄 License

MIT License - see LICENSE file

## 🔗 Links

- [Polymarket API Docs](https://docs.polymarket.com)
- [CLOB API](https://docs.polymarket.com/#clob-api)
- [Discord Community](#)

---

**Built with:** Python, CrewAI, LangChain, Web3.py, FastAPI, Streamlit
