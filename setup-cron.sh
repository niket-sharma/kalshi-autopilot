#!/bin/bash
# Setup cron jobs for Kalshi bot monitoring

echo "🔧 Setting up automated monitoring..."
echo ""

# Add cron job for daily report at 6 PM EST
CRON_CMD="0 18 * * * cd $HOME/ai/kalshi-autopilot && ./daily-report.sh >> daily-reports.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "daily-report.sh"; then
    echo "✅ Cron job already exists"
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Added daily report cron job"
    echo "   Runs every day at 6 PM EST"
fi

echo ""
echo "Current cron jobs:"
crontab -l 2>/dev/null | grep -i kalshi || echo "  (none related to Kalshi)"

echo ""
echo "📝 Reports will be saved to:"
echo "   ~/ai/kalshi-autopilot/daily_report_YYYYMMDD.txt"
echo "   ~/ai/kalshi-autopilot/daily-reports.log"
echo ""
echo "To remove cron job:"
echo "   crontab -e"
echo "   (delete the line with 'daily-report.sh')"
