# 🇺🇸 Kalshi Setup Guide - Legal US Trading!

## ✅ Why Kalshi?

**Kalshi is the FIRST CFTC-regulated prediction market exchange**
- ✅ **100% Legal in the United States**
- ✅ CFTC-regulated (like stock exchanges)
- ✅ Similar markets to Polymarket (politics, economics, sports, etc.)
- ✅ Works with our bot's strategies perfectly

---

## 📋 Quick Setup (10 minutes)

### Step 1: Create Kalshi Account

1. **Go to:** https://kalshi.com
2. **Click "Sign Up"**
3. **Enter:**
   - Email address
   - Password (strong!)
   - Personal info (required by CFTC)

4. **Verify identity** (required by regulation)
   - Upload ID (driver's license, passport)
   - Verify address
   - SSN (for tax reporting - standard for US exchanges)

5. **Get approved** (usually instant, max 24 hours)

---

### Step 2: Fund Your Account

**Minimum:** $25  
**Recommended:** $50-100 to start

**Methods:**
1. **Bank Transfer (ACH)** - Free, 1-3 days
2. **Debit Card** - Instant, ~2% fee
3. **Wire Transfer** - Same day, bank may charge fee

**Steps:**
1. Click "Deposit" in Kalshi
2. Choose method
3. Enter amount
4. Confirm

---

### Step 3: Get API Credentials

**For the bot to work, you need API access:**

1. **Contact Kalshi Support:**
   - Email: support@kalshi.com
   - Subject: "API Access Request"
   - Body: "I would like API access for algorithmic trading"

2. **They'll ask:**
   - Your account email
   - Use case (say: "Automated trading bot for personal use")
   - Trading experience

3. **You'll receive:**
   - API key (your email)
   - API secret (your password, or separate API password)

**Note:** API access may not be instant, but usually approved within 1-2 business days for verified accounts.

---

### Step 4: Configure the Bot

1. **Edit `.env` file:**
   ```bash
   cd ~/ai/kalshi-autopilot
   nano .env
   ```

2. **Add your credentials:**
   ```bash
   KALSHI_API_KEY=your_email@example.com
   KALSHI_API_SECRET=your_password_or_api_secret
   MODE=test  # Start with test mode!
   ```

3. **Save** (Ctrl+X, Y, Enter)

---

### Step 5: Test the Bot

```bash
cd ~/ai/kalshi-autopilot
source venv/bin/activate

# Test connection
python test_wallet.py

# Run one cycle (test mode)
python main.py --mode once
```

---

## 💰 Kalshi vs Polymarket

| Feature | Kalshi | Polymarket |
|---------|--------|------------|
| **Legal in US** | ✅ YES | ❌ NO |
| **Regulated** | ✅ CFTC | ❌ Offshore |
| **API Access** | ✅ Official | ✅ Yes |
| **Liquidity** | 🟡 Good | 🟢 Excellent |
| **Markets** | 🟢 Many | 🟢 Many |
| **Fees** | ~3-5% | ~2% |
| **Funding** | Bank/Card | Crypto only |

**Bottom Line:** Kalshi is the **legal, safe choice** for US traders!

---

## 📊 Market Categories on Kalshi

**Available markets:**
- 🏛️ **Politics** - Elections, policy outcomes
- 📈 **Economics** - GDP, unemployment, inflation
- 🏈 **Sports** - NFL, NBA, MLB outcomes
- 🌡️ **Weather** - Temperature, precipitation
- 💼 **Business** - Earnings, M&A, tech launches
- 🌍 **Events** - News outcomes, scheduled events

**All work with our bot's strategies!**

---

## 🎯 Trading Limits

**Kalshi has position limits** (CFTC requirement):
- Max $25,000 per market (way more than you need!)
- Max $100,000 total across all markets
- Limits reset monthly

**For our $25-100 starting capital, limits are not an issue.**

---

## 💡 Tips for Success

### 1. **Start Small**
- Begin with $25-50
- Test in demo mode first
- Verify bot works correctly

### 2. **Use Demo API First**
Kalshi has a demo environment:
- Same markets as live
- Fake money
- Perfect for testing
- Set `MODE=test` in `.env`

### 3. **Monitor Closely**
- Check trades daily first week
- Verify strategy is working
- Adjust parameters as needed

### 4. **Scale Gradually**
- If profitable after 1 week → add $50
- If profitable after 1 month → add more
- Never risk more than you can lose

---

## 🔐 Security

**Kalshi Security:**
- ✅ CFTC-regulated (like Coinbase, Robinhood)
- ✅ 2FA available (enable it!)
- ✅ US-based company
- ✅ Segregated accounts
- ✅ Audit trail

**Bot Security:**
- ✅ API credentials stored locally
- ✅ Never shared
- ✅ Test mode prevents accidental trades
- ✅ All code is open-source (you can review)

---

## 📞 Support

**Kalshi Support:**
- Email: support@kalshi.com
- Discord: https://discord.gg/kalshi
- Docs: https://docs.kalshi.com

**Bot Issues:**
- Check logs: `tail -f autopilot.log`
- GitHub: https://github.com/niket-sharma/kalshi-autopilot
- Review STRATEGY_GUIDE.md

---

## ⚠️ Important Notes

### Tax Reporting
- Kalshi reports to IRS (like stocks)
- Keep records of trades
- Profits are taxable
- Talk to tax advisor if needed

### Risk Warning
- Prediction markets involve risk
- No guaranteed profits
- Start small
- Only invest what you can afford to lose

### Compliance
- Must be 18+ years old
- Must be US resident
- Cannot trade for others
- Cannot manipulate markets

---

## 🚀 Ready to Trade

Once setup is complete:

```bash
cd ~/ai/kalshi-autopilot
source venv/bin/activate

# Test mode (safe)
python main.py --mode once

# Live trading (after testing)
# Change MODE=live in .env first
python main.py --mode continuous
```

---

## 📈 Expected Performance

**Realistic expectations with $25 starting capital:**
- Good week: +$2-5 profit
- Bad week: -$2-5 loss
- Long-term: 5-15% monthly return (if bot works)

**Remember:**
- Not every market has edge
- May go days without trades
- This is experimental
- Results not guaranteed

---

**Questions? Issues? Check the logs and documentation, or reach out to Kalshi support!**

Good luck trading! 🚀
