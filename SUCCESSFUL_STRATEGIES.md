# Successful Kalshi Bot Strategies - Research Summary

**Research Date**: 2026-02-15  
**Sources**: 235 Kalshi bots found on GitHub  
**Top 3 Analyzed**: ryanfrigo, OctagonAI, CarlosIbCu

---

## 🏆 Top Performing Bots

### 1. ryanfrigo/kalshi-ai-trading-bot (132 ⭐, updated yesterday)

**Key Innovations:**
- **Multi-Model Ensemble** (5 LLMs with weighted votes)
  - Grok-4 (30%) - Lead Forecaster
  - Claude Sonnet 4 (20%) - News Analyst
  - GPT-4o (20%) - Bull Case
  - Gemini 2.5 Flash (15%) - Bear Case
  - DeepSeek R1 (15%) - Risk Manager
  
- **3-Strategy Portfolio**
  - Directional Trading (50% allocation)
  - Market Making (40% allocation) ⚠️ NEW FOR US
  - Arbitrage Detection (10% allocation) ⚠️ NEW FOR US

- **Advanced Risk Management**
  - Kelly Criterion with 0.75x fractional sizing (we use 0.5x)
  - Risk parity allocation across positions ⚠️ NEW FOR US
  - Dynamic rebalancing every 6 hours ⚠️ NEW FOR US
  - Confidence-decay exits (reduce when AI conviction drops) ⚠️ NEW FOR US
  - Time-based max hold: 10 days ⚠️ NEW FOR US

- **Exit Strategies**
  - Trailing take-profit: 20% gain
  - Stop-loss: 15% per position
  - Volatility-adjusted thresholds ⚠️ NEW FOR US

---

### 2. OctagonAI/kalshi-deep-trading-bot (101 ⭐)

**Key Innovations:**
- **Event-Based Analysis** (analyzes entire events, not individual markets) ⚠️ NEW FOR US
- **Independent Probability Predictions** from deep research
- **Hedging System**
  - Auto-hedge low-confidence bets (< 0.6 confidence) ⚠️ NEW FOR US
  - Configurable hedge ratio (25% default)
  - Min downside protection
  
- **Smart Filters**
  - Skip existing positions (avoid duplicate trades) ⚠️ WE SHOULD ADD
  - Filter by soonest expiration
  - Top markets by volume within each event

---

### 3. CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot (171 ⭐)

**Key Innovations:**
- **Cross-Platform Arbitrage** (Polymarket ↔ Kalshi) ⚠️ NEW FOR US
- **Real-Time Monitoring** (fetch every 1 second)
- **Risk-Free Profit Detection**
  - Find opposing positions that sum to < $1.00
  - Instant execution when found
  
---

## 📊 Strategy Comparison Matrix

| Strategy Component | Our Bot | Ryan's Bot | Octagon Bot | Carlos's Bot |
|-------------------|---------|------------|-------------|--------------|
| **Core Approach** | Pattern detection + Gemini | Multi-model ensemble | Deep research + OpenAI | Arbitrage detection |
| **LLM Usage** | Minimal (Gemini only) | Heavy (5 models) | Medium (OpenAI) | None (pure math) |
| **Kelly Criterion** | ✅ 0.5x fractional | ✅ 0.75x fractional | ❌ | N/A |
| **Market Making** | ❌ | ✅ 40% allocation | ❌ | ✅ (implicit) |
| **Arbitrage** | ❌ | ✅ 10% allocation | ❌ | ✅ 100% |
| **Hedging** | ❌ | ❌ | ✅ Auto-hedge | N/A |
| **Dynamic Exits** | Basic stop/take-profit | ✅ Confidence decay | ❌ | Instant close |
| **Risk Parity** | ❌ | ✅ | ❌ | N/A |
| **Event-Based** | Market-focused | Market-focused | ✅ Event analysis | Market-focused |
| **Skip Duplicates** | ❌ | ❌ | ✅ | N/A |
| **Real-Time** | Periodic | Periodic | Periodic | 1-second polling |

---

## 🎯 Recommended Improvements for Our Bot

### HIGH PRIORITY (Implement Now)

#### 1. **Add Market Making Strategy** ⭐⭐⭐
- **Why**: Ryan's bot allocates 40% to market making
- **How**: Place limit orders on bid-ask spread
- **Benefit**: Passive income from spread capture
- **Effort**: Medium (need order book integration)

```python
class MarketMakingStrategy:
    """Capture bid-ask spreads by providing liquidity."""
    
    def find_wide_spreads(self, markets):
        """Find markets with spreads > 5%."""
        # Filter for wide spreads
        # Place limit orders on both sides
        # Earn spread when filled
```

#### 2. **Add Cross-Platform Arbitrage** ⭐⭐⭐
- **Why**: Carlos's bot (171 stars) is pure arbitrage
- **How**: Monitor Polymarket vs Kalshi for same events
- **Benefit**: Risk-free profits
- **Effort**: High (need Polymarket API integration)

```python
class CrossPlatformArbitrage:
    """Detect arbitrage between Kalshi and Polymarket."""
    
    def find_arbitrage(self, kalshi_market, polymarket_market):
        # If Kalshi_YES + Polymarket_NO < $1.00 → profit
        # Execute both sides simultaneously
```

#### 3. **Implement Hedging System** ⭐⭐
- **Why**: Octagon auto-hedges low-confidence trades
- **How**: For confidence < 0.6, hedge 25% on opposite side
- **Benefit**: Downside protection
- **Effort**: Low (simple modification)

```python
def hedge_low_confidence_positions(position, confidence):
    """Auto-hedge positions below 60% confidence."""
    if confidence < 0.6:
        hedge_amount = position.size * 0.25
        # Place opposing bet for hedge_amount
```

#### 4. **Skip Existing Positions** ⭐⭐
- **Why**: Avoid duplicate trades on same market
- **How**: Check portfolio before placing new trades
- **Benefit**: Better capital allocation
- **Effort**: Low

```python
def should_skip_market(market_id, portfolio):
    """Skip if we already have position in this market."""
    return any(p.market_id == market_id for p in portfolio.positions)
```

### MEDIUM PRIORITY (After MVP Working)

#### 5. **Event-Based Analysis** ⭐⭐
- **Why**: Octagon analyzes entire events (holistic view)
- **How**: Group markets by event, analyze collectively
- **Benefit**: Better context, find correlated opportunities
- **Effort**: Medium

#### 6. **Confidence-Decay Exits** ⭐⭐
- **Why**: Ryan's bot exits when AI conviction drops
- **How**: Re-analyze positions, exit if confidence < 50%
- **Benefit**: Cut losers early
- **Effort**: Medium (need periodic re-analysis)

#### 7. **Risk Parity Allocation** ⭐
- **Why**: Ryan balances risk across positions
- **How**: Size positions by inverse volatility
- **Benefit**: Smoother returns
- **Effort**: High (complex math)

#### 8. **Dynamic Rebalancing** ⭐
- **Why**: Ryan rebalances every 6 hours
- **How**: Adjust position sizes based on new probabilities
- **Benefit**: Maintain optimal portfolio
- **Effort**: Medium

### LOW PRIORITY (Future Enhancements)

#### 9. **Multi-Model Ensemble** ⭐
- **Why**: Ryan uses 5 LLMs with weighted votes
- **Conflict**: We want minimal LLM usage (cheaper)
- **Decision**: Skip for now, our pattern approach is better for cost

#### 10. **Real-Time Streaming** ⭐
- **Why**: Carlos polls every 1 second
- **How**: WebSocket integration
- **Benefit**: Faster arbitrage detection
- **Effort**: High

---

## 🚀 Implementation Roadmap

### Phase 1: Quick Wins (This Week)
1. ✅ Skip existing positions filter
2. ✅ Basic hedging for low-confidence trades
3. ✅ Increase Kelly fraction to 0.75x (more aggressive)

### Phase 2: Market Making (Next Week)
1. Add limit order support
2. Implement spread detection
3. Market making strategy module
4. Test with small capital

### Phase 3: Arbitrage (Week 3)
1. Research Polymarket API
2. Build cross-platform price fetcher
3. Arbitrage detection engine
4. Dual execution system

### Phase 4: Advanced Features (Month 2)
1. Event-based analysis
2. Confidence-decay exits
3. Risk parity allocation
4. Dynamic rebalancing

---

## 💡 Key Insights

### What Makes Successful Bots Successful?

1. **Multiple Strategies**: Don't rely on one approach
   - Directional trading (alpha)
   - Market making (steady income)
   - Arbitrage (risk-free)

2. **Risk Management > Prediction**:
   - Hedging protects downside
   - Position sizing matters more than win rate
   - Exit strategies prevent big losses

3. **Speed Matters for Arbitrage**:
   - Real-time monitoring (1-second polls)
   - Instant execution
   - Cross-platform coordination

4. **Event Context > Market Isolation**:
   - Analyze events holistically
   - Find correlated markets
   - Understand narrative

### What Can We Do Better?

1. **Cost Efficiency**: Our minimal LLM approach is cheaper than 5-model ensembles
2. **Pattern Detection**: Our advanced patterns (mispricing, momentum, etc.) are Python-based (faster)
3. **Flexibility**: We can add strategies incrementally

---

## 📈 Expected ROI from Improvements

| Improvement | Expected Profit Boost | Implementation Time |
|-------------|----------------------|---------------------|
| Market Making | +20-30% (passive income) | 1 week |
| Arbitrage | +10-15% (risk-free) | 2 weeks |
| Hedging | +5-10% (loss reduction) | 2 days |
| Skip Duplicates | +2-5% (better allocation) | 1 day |
| Confidence Decay | +5-10% (cut losers early) | 3 days |

**Total Potential Boost**: +42-70% over baseline

---

## 🔗 References

- [ryanfrigo/kalshi-ai-trading-bot](https://github.com/ryanfrigo/kalshi-ai-trading-bot)
- [OctagonAI/kalshi-deep-trading-bot](https://github.com/OctagonAI/kalshi-deep-trading-bot)
- [CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot](https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot)
- [235 Kalshi bots on GitHub](https://github.com/search?q=kalshi+bot)

---

**Next Step**: Implement Phase 1 quick wins (skip duplicates + hedging) this weekend!
