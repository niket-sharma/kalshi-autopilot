#!/usr/bin/env python3
"""Quick status check for Kalshi Trading Bot."""
import os
from datetime import datetime
from pathlib import Path
from api.kalshi_client import KalshiClient
from config import settings

print("=" * 80)
print("🤖 KALSHI TRADING BOT - STATUS")
print("=" * 80)
print()

# Check if bot is running
try:
    result = os.popen("ps aux | grep 'main.py' | grep -v grep").read()
    bot_running = bool(result.strip())
except:
    bot_running = False

print(f"Bot Status: {'🟢 RUNNING' if bot_running else '🔴 STOPPED'}")
print(f"Mode: {settings.mode.upper()}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}")
print()

# Get account data
try:
    client = KalshiClient()
    balance = client.get_balance()
    positions = client.get_positions()
    
    # Calculate P&L
    initial_capital = settings.initial_capital
    pnl = balance - initial_capital
    pnl_pct = (pnl / initial_capital * 100) if initial_capital > 0 else 0
    pnl_sign = "+" if pnl >= 0 else ""
    
    print("=" * 80)
    print("💰 ACCOUNT")
    print("=" * 80)
    print(f"Balance:          ${balance:.2f}")
    print(f"Initial Capital:  ${initial_capital:.2f}")
    print(f"Total P&L:        {pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_pct:.1f}%)")
    print(f"Open Positions:   {len(positions)}")
    print()
    
    if positions:
        print("=" * 80)
        print("📊 OPEN POSITIONS")
        print("=" * 80)
        for i, pos in enumerate(positions[:10], 1):
            ticker = pos.get('ticker', 'Unknown')
            position_size = pos.get('position', 0)
            side = "YES" if position_size > 0 else "NO"
            print(f"{i}. {ticker}")
            print(f"   Side: {side} | Size: {abs(position_size)} contracts")
        print()
    
except Exception as e:
    print(f"❌ Error connecting to Kalshi: {e}")
    print()

# Recent log entries
log_file = Path(__file__).parent / "autopilot.log"
if log_file.exists():
    print("=" * 80)
    print("📝 RECENT ACTIVITY (Last 10 lines)")
    print("=" * 80)
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                # Clean up log line
                if " - " in line:
                    parts = line.split(" - ", 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        message = parts[-1].strip()
                        print(f"{timestamp} {message}")
                    else:
                        print(line.strip())
                else:
                    print(line.strip())
    except Exception as e:
        print(f"Error reading log: {e}")
else:
    print("No log file found")

print()
print("=" * 80)
print("📚 Quick Commands:")
print("   View live logs:     tail -f ~/ai/kalshi-autopilot/autopilot.log")
print("   CLI Dashboard:      cd ~/ai/kalshi-autopilot && ./venv/bin/python monitor.py")
print("   Web Dashboard:      cd ~/ai/kalshi-autopilot && ./start-dashboard.sh")
print("   Stop bot:           kill <PID>  (find PID with: ps aux | grep main.py)")
print("=" * 80)
