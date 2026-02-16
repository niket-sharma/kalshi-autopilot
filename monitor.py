#!/usr/bin/env python3
"""Kalshi Trading Bot Monitor - Real-time dashboard."""
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from api.kalshi_client import KalshiClient
from models import Portfolio
from config import settings

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def get_bot_status():
    """Check if bot is running."""
    try:
        result = os.popen("ps aux | grep 'main.py' | grep -v grep").read()
        return bool(result.strip())
    except:
        return False


def get_log_tail(lines=20):
    """Get last N lines from log file."""
    log_file = Path(__file__).parent / "autopilot.log"
    if not log_file.exists():
        return ["No log file found"]
    
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if all_lines else ["Log file empty"]
    except Exception as e:
        return [f"Error reading log: {e}"]


def count_trades_today():
    """Count trades executed today."""
    log_file = Path(__file__).parent / "autopilot.log"
    if not log_file.exists():
        return 0
    
    today = datetime.now().strftime("%Y-%m-%d")
    trades = 0
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if today in line and "✅ Position opened" in line:
                    trades += 1
    except:
        pass
    
    return trades


def print_dashboard():
    """Print the main dashboard."""
    clear_screen()
    
    # Initialize clients
    try:
        client = KalshiClient()
        balance = client.get_balance()
        positions = client.get_positions()
        markets = client.get_markets(limit=5)
    except Exception as e:
        print(f"{RED}❌ Error connecting to Kalshi: {e}{RESET}")
        return
    
    # Bot status
    bot_running = get_bot_status()
    trades_today = count_trades_today()
    
    # Calculate P&L
    initial_capital = settings.initial_capital
    pnl = balance - initial_capital
    pnl_pct = (pnl / initial_capital * 100) if initial_capital > 0 else 0
    pnl_color = GREEN if pnl >= 0 else RED
    
    # Header
    print(f"{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}🤖 KALSHI TRADING BOT DASHBOARD{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")
    
    # Bot Status
    status_color = GREEN if bot_running else RED
    status_text = "🟢 RUNNING" if bot_running else "🔴 STOPPED"
    print(f"{BOLD}Bot Status:{RESET} {status_color}{status_text}{RESET}")
    print(f"{BOLD}Mode:{RESET} {settings.mode.upper()}")
    print(f"{BOLD}Last Updated:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n")
    
    # Account Summary
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}{BLUE}💰 ACCOUNT SUMMARY{RESET}")
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}Balance:{RESET}          ${balance:.2f}")
    print(f"{BOLD}Initial Capital:{RESET}  ${initial_capital:.2f}")
    print(f"{BOLD}Total P&L:{RESET}        {pnl_color}${pnl:+.2f} ({pnl_pct:+.1f}%){RESET}")
    print(f"{BOLD}Open Positions:{RESET}   {len(positions)}")
    print(f"{BOLD}Trades Today:{RESET}     {trades_today}\n")
    
    # Open Positions
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}{BLUE}📊 OPEN POSITIONS{RESET}")
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    
    if positions:
        for i, pos in enumerate(positions[:5], 1):
            ticker = pos.get('ticker', 'Unknown')
            position_size = pos.get('position', 0)
            side = "YES" if position_size > 0 else "NO"
            side_color = GREEN if position_size > 0 else RED
            print(f"{i}. {BOLD}{ticker}{RESET}")
            print(f"   Side: {side_color}{side}{RESET} | Size: {abs(position_size)} contracts")
    else:
        print(f"{YELLOW}No open positions{RESET}")
    
    print()
    
    # Active Markets
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}{BLUE}📈 ACTIVE MARKETS (Top 5){RESET}")
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    
    if markets:
        for i, market in enumerate(markets[:5], 1):
            question = market.question[:65] + "..." if len(market.question) > 65 else market.question
            yes_price = market.implied_probability if hasattr(market, 'implied_probability') else 0.5
            print(f"{i}. {question}")
            print(f"   Yes: {yes_price:.1%} | Vol: ${market.volume:,.0f}")
    else:
        print(f"{YELLOW}No active markets{RESET}")
    
    print()
    
    # Recent Activity (last 10 log lines)
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}{BLUE}📝 RECENT ACTIVITY{RESET}")
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}")
    
    log_lines = get_log_tail(10)
    for line in log_lines:
        # Color code important events
        if "✅" in line or "SUCCESS" in line.upper():
            print(f"{GREEN}{line.strip()}{RESET}")
        elif "❌" in line or "ERROR" in line.upper():
            print(f"{RED}{line.strip()}{RESET}")
        elif "⚠️" in line or "WARNING" in line.upper():
            print(f"{YELLOW}{line.strip()}{RESET}")
        else:
            # Just show timestamp and message part
            if " - " in line:
                parts = line.split(" - ", 3)
                if len(parts) >= 4:
                    timestamp = parts[0]
                    message = parts[-1].strip()
                    print(f"{CYAN}{timestamp}{RESET} {message}")
                else:
                    print(line.strip())
            else:
                print(line.strip())
    
    print()
    
    # Footer
    print(f"{BOLD}{CYAN}{'─'*80}{RESET}")
    print(f"{CYAN}Commands: [r] Refresh | [l] View full log | [s] Stop bot | [q] Quit{RESET}")
    print(f"{BOLD}{CYAN}{'─'*80}{RESET}")


def main():
    """Main monitoring loop."""
    print("Starting Kalshi Trading Bot Monitor...")
    time.sleep(1)
    
    while True:
        try:
            print_dashboard()
            
            # Auto-refresh every 10 seconds
            print(f"\n{CYAN}Auto-refreshing in 10 seconds... (press Ctrl+C to exit){RESET}")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Dashboard stopped.{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}Error: {e}{RESET}")
            time.sleep(5)


if __name__ == "__main__":
    main()
