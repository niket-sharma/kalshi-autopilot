#!/usr/bin/env python3
"""Kalshi Trading Bot Web Dashboard - Streamlit-based."""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from api.kalshi_client import KalshiClient
from config import settings

# Page config
st.set_page_config(
    page_title="Kalshi Trading Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {font-size: 2em; font-weight: bold;}
    .positive {color: #00CC00;}
    .negative {color: #FF3333;}
    .neutral {color: #888888;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def get_account_data():
    """Fetch account data from Kalshi."""
    try:
        client = KalshiClient()
        balance = client.get_balance()
        positions = client.get_positions()
        markets = client.get_markets(limit=20)
        return {
            'balance': balance,
            'positions': positions,
            'markets': markets,
            'error': None
        }
    except Exception as e:
        return {
            'balance': 0,
            'positions': [],
            'markets': [],
            'error': str(e)
        }


def get_bot_status():
    """Check if bot is running."""
    try:
        result = os.popen("ps aux | grep 'main.py' | grep -v grep").read()
        return bool(result.strip())
    except:
        return False


def parse_log_file():
    """Parse log file for trades and events."""
    log_file = Path(__file__).parent / "autopilot.log"
    if not log_file.exists():
        return []
    
    events = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if any(keyword in line for keyword in ['✅ Position opened', 'Cycle Complete', 'ERROR', 'Opportunity']):
                    # Extract timestamp
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        timestamp = parts[0]
                        message = parts[1].strip()
                        events.append({
                            'timestamp': timestamp,
                            'message': message
                        })
    except Exception as e:
        st.error(f"Error reading log: {e}")
    
    return events[-50:]  # Last 50 events


# Main dashboard
st.title("🤖 Kalshi Trading Bot Dashboard")
st.markdown("Real-time monitoring of your autonomous trading bot")

# Fetch data
data = get_account_data()
bot_running = get_bot_status()

# Error handling
if data['error']:
    st.error(f"❌ Error connecting to Kalshi: {data['error']}")
    st.stop()

# Calculate metrics
balance = data['balance']
initial_capital = settings.initial_capital
pnl = balance - initial_capital
pnl_pct = (pnl / initial_capital * 100) if initial_capital > 0 else 0

# Sidebar - Bot Status
with st.sidebar:
    st.header("⚙️ Bot Status")
    
    if bot_running:
        st.success("🟢 Bot is RUNNING")
    else:
        st.error("🔴 Bot is STOPPED")
    
    st.metric("Mode", settings.mode.upper())
    st.metric("Check Interval", "30 minutes")
    
    st.divider()
    
    st.header("🎯 Trading Parameters")
    st.metric("Min Edge", f"{settings.min_edge_threshold:.0%}")
    st.metric("Min Confidence", f"{settings.min_confidence:.0%}")
    st.metric("Max Position Size", f"{settings.max_position_size:.0%}")
    st.metric("Max Positions", settings.max_concurrent_positions)
    
    hedging_status = "✅ Enabled" if settings.enable_hedging else "❌ Disabled"
    st.metric("Hedging", hedging_status)
    
    st.divider()
    
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Main content - Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Balance",
        value=f"${balance:.2f}",
        delta=None
    )

with col2:
    delta_color = "normal" if pnl >= 0 else "inverse"
    st.metric(
        label="📊 Total P&L",
        value=f"${pnl:.2f}",
        delta=f"{pnl_pct:+.1f}%",
        delta_color=delta_color
    )

with col3:
    st.metric(
        label="📈 Open Positions",
        value=len(data['positions'])
    )

with col4:
    st.metric(
        label="🎯 Available",
        value=f"${balance:.2f}"
    )

st.divider()

# Two-column layout
col_left, col_right = st.columns([1, 1])

# Left column - Open Positions
with col_left:
    st.subheader("📊 Open Positions")
    
    if data['positions']:
        positions_data = []
        for pos in data['positions']:
            ticker = pos.get('ticker', 'Unknown')
            position_size = pos.get('position', 0)
            side = "YES" if position_size > 0 else "NO"
            
            positions_data.append({
                'Market': ticker,
                'Side': side,
                'Size': abs(position_size),
            })
        
        df_positions = pd.DataFrame(positions_data)
        st.dataframe(df_positions, use_container_width=True, hide_index=True)
    else:
        st.info("No open positions")

# Right column - Active Markets
with col_right:
    st.subheader("📈 Active Markets")
    
    if data['markets']:
        markets_data = []
        for market in data['markets'][:10]:
            yes_price = market.implied_probability if hasattr(market, 'implied_probability') else 0.5
            markets_data.append({
                'Question': market.question[:50] + "...",
                'Yes Price': f"{yes_price:.1%}",
                'Volume': f"${market.volume:,.0f}"
            })
        
        df_markets = pd.DataFrame(markets_data)
        st.dataframe(df_markets, use_container_width=True, hide_index=True)
    else:
        st.info("No active markets")

st.divider()

# Recent Activity
st.subheader("📝 Recent Activity")

events = parse_log_file()
if events:
    # Show last 15 events
    for event in reversed(events[-15:]):
        timestamp = event['timestamp']
        message = event['message']
        
        # Color code based on message type
        if "✅" in message or "SUCCESS" in message.upper():
            st.success(f"**{timestamp}** - {message}")
        elif "❌" in message or "ERROR" in message.upper():
            st.error(f"**{timestamp}** - {message}")
        elif "⚠️" in message or "WARNING" in message.upper():
            st.warning(f"**{timestamp}** - {message}")
        else:
            st.info(f"**{timestamp}** - {message}")
else:
    st.info("No recent activity")

# Footer
st.divider()
st.caption("🤖 Kalshi Autonomous Trading Bot | Built with Phase 1 improvements (hedging, skip duplicates, 0.75x Kelly)")
