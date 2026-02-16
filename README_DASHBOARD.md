# 📊 Kalshi Trading Bot Dashboard

Two dashboards available for monitoring your autonomous trading bot:

## 🖥️ CLI Dashboard (Terminal)

Quick terminal-based dashboard with real-time updates:

```bash
cd ~/ai/kalshi-autopilot
./venv/bin/python monitor.py
```

**Features:**
- ✅ Real-time bot status (running/stopped)
- ✅ Account balance & P&L
- ✅ Open positions
- ✅ Active markets
- ✅ Recent activity log
- ✅ Auto-refreshes every 10 seconds
- ✅ Color-coded events (green=success, red=error, yellow=warning)

**Commands:**
- Press `Ctrl+C` to exit

---

## 🌐 Web Dashboard (Browser)

Beautiful web-based dashboard with interactive charts:

```bash
cd ~/ai/kalshi-autopilot
./start-dashboard.sh

# Or manually:
./venv/bin/streamlit run dashboard.py
```

Then open: **http://localhost:8501** in your browser

**Features:**
- ✅ Real-time metrics (balance, P&L, positions)
- ✅ Open positions table
- ✅ Active markets list
- ✅ Recent activity timeline
- ✅ Bot status indicator
- ✅ Trading parameters display
- ✅ Auto-refresh every 30 seconds
- ✅ Mobile-responsive design

---

## 📝 Log File

Full detailed logs are saved to:
```bash
~/ai/kalshi-autopilot/autopilot.log
```

View live logs:
```bash
tail -f ~/ai/kalshi-autopilot/autopilot.log
```

View recent trades:
```bash
grep -i "position opened\|trade" ~/ai/kalshi-autopilot/autopilot.log | tail -20
```

---

## 🤖 Bot Control

**Check if bot is running:**
```bash
ps aux | grep "main.py" | grep -v grep
```

**Stop the bot:**
```bash
# Find the process ID (PID)
ps aux | grep "main.py" | grep -v grep

# Kill it (replace XXXXX with actual PID)
kill XXXXX
```

**Start the bot:**
```bash
cd ~/ai/kalshi-autopilot
nohup ./venv/bin/python main.py --mode continuous > autopilot.log 2>&1 &
```

---

## 📊 Monitoring Tips

1. **Use CLI Dashboard for quick checks**: Fast, lightweight, perfect for SSH
2. **Use Web Dashboard for detailed analysis**: Better visualization, interactive
3. **Check logs for debugging**: Full details of every decision and trade
4. **Monitor daily**: Check at least once per day to ensure bot is healthy

---

## ⚡ Quick Start

```bash
# Terminal 1: Run the bot (if not already running)
cd ~/ai/kalshi-autopilot
nohup ./venv/bin/python main.py --mode continuous > autopilot.log 2>&1 &

# Terminal 2: Watch the CLI dashboard
./venv/bin/python monitor.py

# OR Terminal 2: Start web dashboard
./start-dashboard.sh
# Then open http://localhost:8501 in browser
```

---

**Pro Tip**: Keep the web dashboard open in a browser tab and refresh when you want updates!
