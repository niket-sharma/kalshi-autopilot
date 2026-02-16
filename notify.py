#!/usr/bin/env python3
"""Send notifications when bot makes trades."""
import os
import time
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "autopilot.log"
STATE_FILE = Path(__file__).parent / ".notify_state"

def get_last_position():
    """Get position from last notification."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def save_position(pos):
    """Save log file position."""
    with open(STATE_FILE, 'w') as f:
        f.write(str(pos))

def check_for_trades():
    """Check log for new trades."""
    if not LOG_FILE.exists():
        return []
    
    last_pos = get_last_position()
    trades = []
    
    with open(LOG_FILE, 'r') as f:
        # Skip to last position
        f.seek(last_pos)
        
        for line in f:
            # Look for trade indicators
            if "✅ Position opened" in line or "Position closed" in line:
                trades.append(line.strip())
            elif "Opportunity:" in line:
                trades.append(line.strip())
        
        # Save new position
        save_position(f.tell())
    
    return trades

def send_notification(message):
    """Send notification (print for now, can add Telegram later)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🔔 {message}")

if __name__ == "__main__":
    print("🔔 Kalshi Bot Notification Monitor")
    print("Checking for trades every 30 seconds...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            trades = check_for_trades()
            
            if trades:
                send_notification(f"NEW ACTIVITY DETECTED!")
                for trade in trades:
                    print(f"  → {trade}")
                print()
            
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
