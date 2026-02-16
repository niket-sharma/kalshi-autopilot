#!/bin/bash
# Quick script to check if bot has made any trades

cd "$(dirname "$0")"

echo "🔍 Checking for trades..."
echo ""

TRADES=$(grep -i "position opened\|trade executed" autopilot.log 2>/dev/null | wc -l)

if [ "$TRADES" -gt 0 ]; then
    echo "✅ Found $TRADES trade(s)!"
    echo ""
    echo "Recent trades:"
    grep -i "position opened\|trade executed" autopilot.log | tail -5
else
    echo "❌ No trades yet"
    echo ""
    echo "Bot is running but waiting for opportunities."
    echo "This is normal - it only trades when it finds real edge."
fi

echo ""
echo "📊 Quick stats:"
./venv/bin/python -c "
from api.kalshi_client import KalshiClient
try:
    client = KalshiClient()
    balance = client.get_balance()
    positions = client.get_positions()
    print(f'  Balance: \${balance:.2f}')
    print(f'  Open Positions: {len(positions)}')
except Exception as e:
    print(f'  Error: {e}')
" 2>&1 | grep -v "INFO\|WARNING"

echo ""
echo "Last updated: $(date)"
