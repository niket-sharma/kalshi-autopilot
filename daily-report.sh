#!/bin/bash
# Generate daily report and optionally email/notify

cd "$(dirname "$0")"

REPORT_FILE="daily_report_$(date +%Y%m%d).txt"

{
    echo "📊 KALSHI BOT DAILY REPORT"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S EST')"
    echo "========================================"
    echo ""
    
    # Bot status
    if ps aux | grep "main.py" | grep -v grep > /dev/null; then
        echo "Bot Status: 🟢 RUNNING"
    else
        echo "Bot Status: 🔴 STOPPED"
    fi
    echo ""
    
    # Account info
    echo "Account Status:"
    ./venv/bin/python -c "
from api.kalshi_client import KalshiClient
from config import settings
try:
    client = KalshiClient()
    balance = client.get_balance()
    positions = client.get_positions()
    initial = settings.initial_capital
    pnl = balance - initial
    pnl_pct = (pnl / initial * 100) if initial > 0 else 0
    
    print(f'  Balance: \${balance:.2f}')
    print(f'  P&L: \${pnl:+.2f} ({pnl_pct:+.1f}%)')
    print(f'  Open Positions: {len(positions)}')
except Exception as e:
    print(f'  Error: {e}')
" 2>&1 | grep -v "INFO\|WARNING"
    
    echo ""
    echo "Trades Today:"
    TODAY=$(date +%Y-%m-%d)
    TRADES=$(grep -i "$TODAY.*position opened" autopilot.log 2>/dev/null | wc -l)
    echo "  Total: $TRADES"
    
    if [ "$TRADES" -gt 0 ]; then
        echo ""
        echo "  Details:"
        grep -i "$TODAY.*position opened" autopilot.log | tail -5
    fi
    
    echo ""
    echo "========================================"
    echo "Full log: ~/ai/kalshi-autopilot/autopilot.log"
    
} | tee "$REPORT_FILE"

echo ""
echo "Report saved to: $REPORT_FILE"
