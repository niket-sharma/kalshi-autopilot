# Quick Start Guide - Polymarket Autopilot

Get your AI trading agent running in 5 minutes!

## Prerequisites

1. **Polymarket Account** → Sign up at [polymarket.com](https://polymarket.com)
2. **API Keys** → Get from Polymarket settings
3. **OpenAI API Key** → From [platform.openai.com](https://platform.openai.com)
4. **USDC on Polygon** → Fund your wallet with $25+ USDC

## Installation

```bash
# 1. Clone repository
git clone https://github.com/niket-sharma/polymarket-autopilot.git
cd polymarket-autopilot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your API keys
```

## Configuration

Edit `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...                    # From OpenAI
POLYMARKET_API_KEY=your_key              # From Polymarket
POLYMARKET_SECRET=your_secret
POLYMARKET_PRIVATE_KEY=0x...            # Your wallet private key

# Trading settings
INITIAL_CAPITAL=25.0                     # Starting amount ($25)
MAX_POSITION_SIZE=0.15                   # 15% max per trade
MIN_EDGE_THRESHOLD=0.10                  # 10% edge required
MODE=test                                # Start with test mode!
```

## Test the System

```bash
# Run test suite (no trading)
python test_system.py
```

Expected output:
```
🧪 Polymarket Autopilot System Tests
✅ Fetched 5 markets
✅ Analysis complete
✅ Position sizing complete
✅ Cycle complete
✅ All tests passed!
```

## Run Once (Manual)

```bash
# Run one trading cycle
python main.py --mode once
```

This will:
1. Scan high-volume markets
2. Analyze events with GPT-4
3. Find edges (mispriced markets)
4. Calculate position sizes
5. Execute trades (if edges found)
6. Monitor existing positions

## Run Continuously (Autonomous)

```bash
# Run every 30 minutes (default)
python main.py --mode continuous

# Custom interval (every 15 minutes)
python main.py --mode continuous --interval 15
```

Press `Ctrl+C` to stop.

## Monitor Your Agent

Check logs:
```bash
tail -f autopilot.log
```

View portfolio:
```bash
# TODO: Dashboard coming soon
streamlit run dashboard.py
```

## What to Expect

**First Run:**
- Scans 10-20 high-volume markets
- Analyzes top opportunities
- May or may not find tradeable edges
- Executes 0-2 trades typically

**Ongoing:**
- Monitors positions every cycle
- Closes on stop-loss or take-profit
- Compounds profits automatically
- Stops if drawdown hits 20%

## Safety Features

✅ **Test Mode First** - Always start in test mode  
✅ **Risk Limits** - Max 15% per position  
✅ **Stop Losses** - Auto-exit at -20%  
✅ **Daily Loss Limit** - Stops at -10% daily  
✅ **Kill Switch** - Halts at -20% total drawdown  
✅ **Position Limits** - Max 3 concurrent positions  

## Going Live

**Only after testing!**

1. Verify test mode works correctly
2. Check you have USDC in wallet
3. Review risk settings
4. Change `.env`: `MODE=live`
5. Start with small capital ($25-50)
6. Monitor closely for first 24 hours

## Troubleshooting

**"No markets found"**
- Check internet connection
- Polymarket API may be down

**"Analysis failed"**
- Check OPENAI_API_KEY is set
- Verify API key has credits

**"Cannot open position"**
- Check portfolio limits
- May have hit daily loss limit
- Verify available capital

**"Failed to place order"**
- Test mode: This is normal (simulated)
- Live mode: Check wallet balance/approval

## Next Steps

- [x] Run tests
- [x] First manual cycle
- [ ] Monitor for 24 hours in test mode
- [ ] Deploy to cloud for 24/7 operation
- [ ] Add Telegram alerts
- [ ] Scale capital after success

## Support

- GitHub Issues: [Report bugs](https://github.com/niket-sharma/polymarket-autopilot/issues)
- Docs: See README.md
- Community: Coming soon

## Disclaimer

**This is experimental software. Start small. No guarantees.**

Prediction markets involve risk. Only invest what you can afford to lose.

---

Ready to profit? Let's go! 🚀
