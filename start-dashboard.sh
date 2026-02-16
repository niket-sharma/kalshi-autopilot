#!/bin/bash
# Start the Kalshi Trading Bot Web Dashboard

cd "$(dirname "$0")"

echo "🚀 Starting Kalshi Trading Bot Dashboard..."
echo ""
echo "📊 Web Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

./venv/bin/streamlit run dashboard.py --server.headless=true
