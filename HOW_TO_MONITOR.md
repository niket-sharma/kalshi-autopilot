# 🔔 How to Monitor Your Kalshi Trading Bot

Your bot is running autonomously 24/7. Here's how to check on it:

---

## ⚡ Quick Checks (Use These Daily!)

### 1. **Fastest Status Check** (2 seconds)
```bash
cd ~/ai/kalshi-autopilot
./venv/bin/python status.py
```
Shows: Balance, P&L, open positions, recent activity

### 2. **Check for Trades**
```bash
cd ~/ai/kalshi-autopilot
./check-trades.sh
```
Shows: If bot has made any trades today

### 3. **Daily Report**
```bash
cd ~/ai/kalshi-autopilot
./daily-report.sh
```
Generates: Full daily summary with all trades and P&L

---

## 📊 Dashboards

### **CLI Dashboard** (Terminal, auto-refresh)
```bash
cd ~/ai/kalshi-autopilot
./venv/bin/python monitor.py
```
Real-time dashboard that refreshes every 10 seconds

### **Web Dashboard** (Browser)
```bash
cd ~/ai/kalshi-autopilot
./start-dashboard.sh
```
Then open: http://localhost:8501 in your browser

---

## 🔔 Automated Monitoring

### **Daily Reports** (Already Set Up! ✅)
- **When**: Every day at 6 PM EST
- **What**: Generates daily summary automatically
- **Where**: `~/ai/kalshi-autopilot/daily_report_YYYYMMDD.txt`
- **Log**: `~/ai/kalshi-autopilot/daily-reports.log`

### **View Auto-Generated Reports**
```bash
cd ~/ai/kalshi-autopilot
ls -lh daily_report_*.txt
cat daily_report_$(date +%Y%m%d).txt
```

---

## 🤖 Bot Control

### **Check if Bot is Running**
```bash
ps aux | grep "main.py" | grep -v grep
```

### **View Live Logs**
```bash
tail -f ~/ai/kalshi-autopilot/autopilot.log
```

### **Stop the Bot**
```bash
# Find process ID
ps aux | grep "main.py" | grep -v grep

# Kill it (replace 12345 with actual PID)
kill 12345
```

### **Restart the Bot**
```bash
cd ~/ai/kalshi-autopilot
nohup ./venv/bin/python main.py --mode continuous > autopilot.log 2>&1 &
```

---

## 📱 On Your Phone (Kalshi App)

**Check Kalshi app to verify trades**:
1. Open Kalshi app
2. Go to "Portfolio"
3. Look for new positions
4. Check balance changes

---

## 🎯 What to Expect

### **Normal Behavior**
- ✅ **0-2 trades per day**: Bot is selective (this is good!)
- ✅ **Days with no trades**: Waiting for quality setups
- ✅ **Small position sizes**: $2-4 per trade with $25 capital

### **When to Check**
- **Morning (9 AM)**: Quick status check
- **Afternoon (2-3 PM)**: Check if any trades during market hours
- **Evening (6 PM)**: Read automated daily report

### **When to Worry**
- ❌ Bot stopped running (check `ps aux | grep main.py`)
- ❌ Daily loss > 10% ($2.50+)
- ❌ Unusual number of trades (>10 per day)
- ❌ Balance dropping consistently

---

## 📧 Get Notified on Trades

### **Live Notification Monitor** (Optional)
Run this in a terminal to get alerted instantly when trades happen:
```bash
cd ~/ai/kalshi-autopilot
./venv/bin/python notify.py
```
Checks log every 30 seconds and prints alerts

---

## 🔍 Troubleshooting

### **No Trades for Days**
✅ **This is normal!** Bot only trades when it finds real edge (>5%).

Check:
```bash
cd ~/ai/kalshi-autopilot
grep "Opportunities:" autopilot.log | tail -10
```

Should see lines like:
- "Opportunities: 0" = No good trades found (correct behavior)
- "Opportunities: 2" = Found trades but maybe already had position

### **Bot Stopped**
Restart it:
```bash
cd ~/ai/kalshi-autopilot
nohup ./venv/bin/python main.py --mode continuous > autopilot.log 2>&1 &
```

### **Can't Access Dashboard**
Make sure you're running `start-dashboard.sh` then open http://localhost:8501

---

## 📚 Recommended Daily Routine

**Morning (30 seconds)**:
```bash
cd ~/ai/kalshi-autopilot && ./venv/bin/python status.py
```

**Afternoon (if you're curious)**:
```bash
cd ~/ai/kalshi-autopilot && ./check-trades.sh
```

**Evening (automated - check your reports folder)**:
```bash
cd ~/ai/kalshi-autopilot && cat daily_report_$(date +%Y%m%d).txt
```

**Weekend (review week)**:
```bash
cd ~/ai/kalshi-autopilot && ./venv/bin/python status.py
# Check P&L for the week
```

---

## 💡 Pro Tips

1. **Don't check too often** - Let the bot work. Once a day is enough.
2. **Trust the process** - No trades for days is normal and good.
3. **Use Kalshi app** - Fastest way to verify if trade happened.
4. **Check logs if curious** - `tail -f autopilot.log` shows everything.
5. **Daily reports** - Auto-generated at 6 PM, check those!

---

## 🆘 Emergency Commands

**Stop everything immediately**:
```bash
ps aux | grep "main.py" | awk '{print $2}' | xargs kill
```

**Check last error**:
```bash
grep -i error ~/ai/kalshi-autopilot/autopilot.log | tail -5
```

**Fresh restart**:
```bash
cd ~/ai/kalshi-autopilot
ps aux | grep "main.py" | awk '{print $2}' | xargs kill
sleep 2
nohup ./venv/bin/python main.py --mode continuous > autopilot.log 2>&1 &
```

---

**The bot is now monitoring itself and will generate reports automatically!** 🤖✅
