"""
TradeCraft - Simple Streamlit Trading Journal

A clean, minimal trading journal and analytics dashboard.
Much simpler than the complex Dash version!
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import calendar

# Authentication removed for personal use

# Configure page
st.set_page_config(
    page_title="TradeCraft Trading Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2c5aa0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2c5aa0;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Database functions (simplified from your existing utils)
@st.cache_resource
def get_db_connection(db_path: str = "data/tradecraft.db"):
    """Get database connection with resource caching."""
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data(ttl=60)
def load_trades(account_id: Optional[int] = None) -> pd.DataFrame:
    """Load trades from database with P&L calculations."""
    try:
        conn = sqlite3.connect("data/tradecraft.db")
        
        query = "SELECT * FROM trades"
        params = []
        
        if account_id:
            query += " WHERE account_id = ?"
            params.append(account_id)
        
        query += " ORDER BY opened_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            # Convert date columns
            date_cols = ['opened_at', 'closed_at']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Calculate P&L for each trade using the existing analytics function
            pnl_data = []
            for _, trade in df.iterrows():
                try:
                    # Import the analytics function
                    import sys
                    sys.path.append('.')
                    from utils.db_access import trade_analytics
                    
                    analytics = trade_analytics(trade['id'])
                    pnl_data.append({
                        'trade_id': trade['id'],
                        'realized_pnl': analytics.get('realized_pnl', 0.0),
                        'status': analytics.get('status', 'UNKNOWN'),
                        'total_fees': analytics.get('total_fees', 0.0),
                        'avg_buy_price': analytics.get('avg_buy_price', 0.0),
                        'avg_sell_price': analytics.get('avg_sell_price', 0.0),
                        'open_qty': analytics.get('open_qty', 0.0)
                    })
                except Exception as e:
                    pnl_data.append({
                        'trade_id': trade['id'],
                        'realized_pnl': 0.0,
                        'status': 'ERROR',
                        'total_fees': 0.0,
                        'avg_buy_price': 0.0,
                        'avg_sell_price': 0.0,
                        'open_qty': 0.0
                    })
            
            # Add P&L data to the DataFrame
            if pnl_data:
                pnl_df = pd.DataFrame(pnl_data)
                df = df.merge(pnl_df, left_on='id', right_on='trade_id', how='left')
                
                # Add some computed columns for better display
                df['symbol'] = df['asset_symbol']  # Alias for consistency
                df['pnl'] = df['realized_pnl']     # Alias for consistency
        
        return df
    except Exception as e:
        st.error(f"Error loading trades: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_accounts() -> pd.DataFrame:
    """Load all available accounts."""
    try:
        conn = sqlite3.connect("data/tradecraft.db")
        df = pd.read_sql_query("SELECT * FROM accounts ORDER BY name", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading accounts: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_unique_symbols(df: pd.DataFrame) -> List[str]:
    """Get unique symbols from trades."""
    if df.empty:
        return []
    
    # Check for both 'symbol' and 'asset_symbol' columns
    symbol_col = None
    if 'symbol' in df.columns:
        symbol_col = 'symbol'
    elif 'asset_symbol' in df.columns:
        symbol_col = 'asset_symbol'
    
    if symbol_col is None:
        return []
    
    return sorted(df[symbol_col].dropna().unique().tolist())

@st.cache_data(ttl=60)
def get_unique_tags(df: pd.DataFrame) -> List[str]:
    """Get unique tags from trades."""
    if df.empty or 'tags' not in df.columns:
        return []
    all_tags = []
    for tags in df['tags'].dropna():
        if tags:
            all_tags.extend([tag.strip() for tag in str(tags).split(',')])
    return sorted(list(set(all_tags)))

def calculate_portfolio_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive portfolio statistics."""
    # Default stats structure
    default_stats = {
        'total_trades': 0,
        'total_pnl': 0.0,
        'win_rate': 0.0,
        'avg_win': 0.0,
        'avg_loss': 0.0,
        'largest_win': 0.0,
        'largest_loss': 0.0,
        'expectancy': 0.0,
        'avg_win_hold_time': 0.0,
        'avg_loss_hold_time': 0.0,
        'max_win_streak': 0,
        'max_loss_streak': 0,
        'avg_daily_vol': 0.0,
        'avg_size': 0.0
    }
    
    if df.empty:
        return default_stats
    
    pnl_col = 'realized_pnl' if 'realized_pnl' in df.columns else 'pnl'
    
    if pnl_col not in df.columns:
        # Return default stats but with correct trade count
        default_stats['total_trades'] = len(df)
        return default_stats
    
    # Filter out NaN values
    df_clean = df.dropna(subset=[pnl_col])
    
    if df_clean.empty:
        default_stats['total_trades'] = len(df)
        return default_stats
    
    wins = df_clean[df_clean[pnl_col] > 0]
    losses = df_clean[df_clean[pnl_col] < 0]
    
    # Basic stats
    total_trades = len(df_clean)
    total_pnl = df_clean[pnl_col].sum()
    win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
    avg_win = wins[pnl_col].mean() if len(wins) > 0 else 0
    avg_loss = losses[pnl_col].mean() if len(losses) > 0 else 0
    
    # Expectancy calculation: (Win Rate * Avg Win) + (Loss Rate * Avg Loss)
    loss_rate = (total_trades - len(wins)) / total_trades if total_trades > 0 else 0
    expectancy = (win_rate/100 * avg_win) + (loss_rate * avg_loss) if total_trades > 0 else 0
    
    # Hold time calculations (if date columns exist)
    avg_win_hold_time = 0.0
    avg_loss_hold_time = 0.0
    if 'opened_at' in df_clean.columns and 'closed_at' in df_clean.columns:
        # Calculate hold times for wins and losses
        df_with_dates = df_clean.dropna(subset=['opened_at', 'closed_at']).copy()
        if not df_with_dates.empty:
            df_with_dates['hold_time_days'] = (
                pd.to_datetime(df_with_dates['closed_at']) - 
                pd.to_datetime(df_with_dates['opened_at'])
            ).dt.total_seconds() / (24 * 3600)
            
            # Average hold time for wins
            win_trades = df_with_dates[df_with_dates[pnl_col] > 0]
            if not win_trades.empty:
                avg_win_hold_time = win_trades['hold_time_days'].mean()
            
            # Average hold time for losses
            loss_trades = df_with_dates[df_with_dates[pnl_col] < 0]
            if not loss_trades.empty:
                avg_loss_hold_time = loss_trades['hold_time_days'].mean()
    
    # Win/Loss streak calculations
    def calculate_streaks(pnl_series):
        """Calculate max win and loss streaks."""
        if len(pnl_series) == 0:
            return 0, 0
        
        win_streak = 0
        loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for pnl in pnl_series:
            if pnl > 0:
                win_streak += 1
                loss_streak = 0
                max_win_streak = max(max_win_streak, win_streak)
            elif pnl < 0:
                loss_streak += 1
                win_streak = 0
                max_loss_streak = max(max_loss_streak, loss_streak)
            else:  # Break even
                win_streak = 0
                loss_streak = 0
        
        return max_win_streak, max_loss_streak
    
    max_win_streak, max_loss_streak = calculate_streaks(df_clean[pnl_col])
    
    # Average daily volume calculation (if we have quantity/size data)
    avg_daily_vol = 0.0
    if 'opened_at' in df_clean.columns:
        df_with_dates = df_clean.dropna(subset=['opened_at']).copy()
        if not df_with_dates.empty:
            df_with_dates['date'] = pd.to_datetime(df_with_dates['opened_at']).dt.date
            daily_trades = df_with_dates.groupby('date').size()
            avg_daily_vol = daily_trades.mean() if len(daily_trades) > 0 else 0
    
    # Average position size (using a proxy calculation if available)
    avg_size = 0.0
    if 'avg_buy_price' in df_clean.columns and 'avg_sell_price' in df_clean.columns:
        # Use average of buy and sell prices as position size proxy
        df_size = df_clean.dropna(subset=['avg_buy_price', 'avg_sell_price'])
        if not df_size.empty:
            df_size['avg_price'] = (df_size['avg_buy_price'] + df_size['avg_sell_price']) / 2
            avg_size = df_size['avg_price'].mean()
    elif 'avg_buy_price' in df_clean.columns:
        # Use buy price as proxy
        avg_size = df_clean['avg_buy_price'].mean()
    
    return {
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'largest_win': df_clean[pnl_col].max() if total_trades > 0 else 0,
        'largest_loss': df_clean[pnl_col].min() if total_trades > 0 else 0,
        'expectancy': expectancy,
        'avg_win_hold_time': avg_win_hold_time,
        'avg_loss_hold_time': avg_loss_hold_time,
        'max_win_streak': max_win_streak,
        'max_loss_streak': max_loss_streak,
        'avg_daily_vol': avg_daily_vol,
        'avg_size': avg_size
    }

def create_equity_curve(df: pd.DataFrame) -> go.Figure:
    """Create equity curve chart."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Use realized_pnl for P&L and appropriate date column
    pnl_col = 'realized_pnl' if 'realized_pnl' in df.columns else 'pnl'
    
    # For equity curve, use closed_at if available and not null, otherwise opened_at
    if 'closed_at' in df.columns:
        # Filter to only completed trades (those with closed_at dates)
        completed_trades = df.dropna(subset=['closed_at'])
        if not completed_trades.empty:
            date_col = 'closed_at'
            df_for_curve = completed_trades
        else:
            # Fall back to opened_at if no closed trades
            date_col = 'opened_at'
            df_for_curve = df
    else:
        date_col = 'opened_at'
        df_for_curve = df
    
    if pnl_col not in df_for_curve.columns or date_col not in df_for_curve.columns:
        fig = go.Figure()
        fig.add_annotation(text="Missing P&L or date data", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Filter out rows with null P&L or dates
    df_clean = df_for_curve.dropna(subset=[pnl_col, date_col])
    
    if df_clean.empty:
        fig = go.Figure()
        fig.add_annotation(text="No complete trade data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Sort by date and calculate cumulative PnL
    df_sorted = df_clean.sort_values(date_col)
    df_sorted['cumulative_pnl'] = df_sorted[pnl_col].cumsum()
    
    fig = px.line(df_sorted, x=date_col, y='cumulative_pnl',
                  title="Equity Curve (Cumulative P&L)",
                  labels={'cumulative_pnl': 'Cumulative P&L ($)', date_col: 'Date'})
    
    # Add a horizontal line at y=0 for reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        hovermode='x unified',
        showlegend=False,
        height=400,
        yaxis_title="Cumulative P&L ($)",
        xaxis_title="Date"
    )
    
    return fig

def filter_trades(df: pd.DataFrame, symbols: List[str], tags: List[str], 
                 start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Filter trades based on criteria."""
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Filter by symbols - check both 'symbol' and 'asset_symbol'
    if symbols:
        symbol_col = 'symbol' if 'symbol' in filtered_df.columns else 'asset_symbol'
        if symbol_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[symbol_col].isin(symbols)]
    
    # Filter by tags
    if tags and 'tags' in filtered_df.columns:
        mask = filtered_df['tags'].str.contains('|'.join(tags), na=False, case=False)
        filtered_df = filtered_df[mask]
    
    # Filter by date range - prefer closed_at for completed trades, fallback to opened_at
    date_col = 'closed_at' if 'closed_at' in filtered_df.columns else 'opened_at'
    if date_col in filtered_df.columns:
        # For date filtering, use non-null dates
        date_mask = filtered_df[date_col].notna()
        filtered_df = filtered_df[date_mask]
        
        if not filtered_df.empty:
            filtered_df = filtered_df[
                (filtered_df[date_col].dt.date >= start_date.date()) &
                (filtered_df[date_col].dt.date <= end_date.date())
            ]
    
    return filtered_df

@st.cache_data(ttl=60)
def load_trade_legs(trade_id: int) -> pd.DataFrame:
    """Load trade legs for a specific trade."""
    try:
        # Import the function from utils
        import sys
        sys.path.append('.')
        from utils.db_access import fetch_legs_for_trade
        
        legs = fetch_legs_for_trade(trade_id)
        if legs:
            df = pd.DataFrame(legs)
            # Convert date columns
            if 'executed_at' in df.columns:
                df['executed_at'] = pd.to_datetime(df['executed_at'], errors='coerce')
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading trade legs: {e}")
        return pd.DataFrame()

def get_trades_by_day(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    """Get trades grouped by day for a specific month."""
    if df.empty:
        return pd.DataFrame()
    
    # Filter by year and month
    df_filtered = df.copy()
    if 'opened_at' in df_filtered.columns:
        df_filtered = df_filtered.dropna(subset=['opened_at'])
        df_filtered = df_filtered[df_filtered['opened_at'].dt.year == year]
        df_filtered = df_filtered[df_filtered['opened_at'].dt.month == month]
        df_filtered['date'] = df_filtered['opened_at'].dt.date
    else:
        return pd.DataFrame()
    
    return df_filtered

def create_calendar_data(df: pd.DataFrame, year: int, month: int) -> Dict[str, Any]:
    """Create calendar data structure with daily P&L and trade counts."""
    # Get trades for the month
    month_trades = get_trades_by_day(df, year, month)
    
    # Group by day
    if not month_trades.empty:
        pnl_col = 'realized_pnl' if 'realized_pnl' in month_trades.columns else 'pnl'
        if pnl_col in month_trades.columns:
            daily_stats = month_trades.groupby('date').agg({
                pnl_col: 'sum',
                'id': 'count'
            }).rename(columns={'id': 'trade_count'})
        else:
            daily_stats = month_trades.groupby('date').agg({
                'id': 'count'
            }).rename(columns={'id': 'trade_count'})
            daily_stats[pnl_col] = 0
    else:
        daily_stats = pd.DataFrame()
    
    # Generate calendar structure
    cal = calendar.Calendar()
    month_dates = list(cal.itermonthdates(year, month))
    
    # Create weeks structure
    weeks = []
    for week_start in range(0, len(month_dates), 7):
        week_dates = month_dates[week_start:week_start+7]
        week_data = []
        
        for date_obj in week_dates:
            if date_obj.month != month:
                # Day from previous/next month
                week_data.append({
                    'date': date_obj,
                    'day': date_obj.day,
                    'is_current_month': False,
                    'pnl': 0,
                    'trade_count': 0
                })
            else:
                # Day from current month
                if not daily_stats.empty and date_obj in daily_stats.index:
                    pnl = daily_stats.loc[date_obj, pnl_col] if pnl_col in daily_stats.columns else 0
                    trade_count = daily_stats.loc[date_obj, 'trade_count']
                else:
                    pnl = 0
                    trade_count = 0
                
                week_data.append({
                    'date': date_obj,
                    'day': date_obj.day,
                    'is_current_month': True,
                    'pnl': pnl,
                    'trade_count': trade_count
                })
        
        # Calculate weekly summary
        current_month_days = [d for d in week_data if d['is_current_month']]
        week_pnl = sum(d['pnl'] for d in current_month_days)
        week_trades = sum(d['trade_count'] for d in current_month_days)
        wins = len([d for d in current_month_days if d['pnl'] > 0])
        losses = len([d for d in current_month_days if d['pnl'] < 0])
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        weeks.append({
            'days': week_data,
            'summary': {
                'pnl': week_pnl,
                'trades': week_trades,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate
            }
        })
    
    return {'weeks': weeks, 'month_name': calendar.month_name[month], 'year': year}

def render_calendar(calendar_data: Dict[str, Any]) -> None:
    """Render the calendar in Streamlit."""
    # Calendar grid
    st.markdown("---")
    
    # Day headers
    day_headers = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Weekly Summary"]
    header_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1.2])
    for i, day in enumerate(day_headers):
        with header_cols[i]:
            st.markdown(f"**{day}**")
    
    # Calendar weeks
    for week in calendar_data['weeks']:
        week_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1.2])
        
        # Days of the week
        for i, day_data in enumerate(week['days']):
            with week_cols[i]:
                if day_data['is_current_month']:
                    # Current month day with styling
                    pnl = day_data['pnl']
                    trade_count = day_data['trade_count']
                    
                    # Color based on P&L
                    if pnl > 0:
                        color = "#28a745"  # Green for profit
                        bg_color = "#d4edda"
                    elif pnl < 0:
                        color = "#dc3545"  # Red for loss
                        bg_color = "#f8d7da"
                    else:
                        color = "#6c757d"  # Gray for break-even/no trades
                        bg_color = "#f8f9fa"
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {bg_color}; 
                        border: 1px solid {color}; 
                        border-radius: 8px; 
                        padding: 8px; 
                        text-align: center; 
                        min-height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    ">
                        <div style="font-size: 14px; font-weight: bold; color: #333;">
                            {day_data['day']}
                        </div>
                        <div style="color: {color}; font-weight: bold; font-size: 12px; margin: 2px 0;">
                            ${pnl:.0f}
                        </div>
                        <div style="color: #666; font-size: 10px;">
                            {trade_count} trade{'s' if trade_count != 1 else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Other month day (grayed out)
                    st.markdown(f"""
                    <div style="
                        background-color: #f8f9fa; 
                        border: 1px solid #e9ecef; 
                        border-radius: 8px; 
                        padding: 8px; 
                        text-align: center; 
                        min-height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        opacity: 0.3;
                    ">
                        <div style="font-size: 14px; color: #999;">
                            {day_data['day']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Weekly summary
        with week_cols[7]:
            summary = week['summary']
            pnl_color = "#28a745" if summary['pnl'] > 0 else ("#dc3545" if summary['pnl'] < 0 else "#6c757d")
            
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa; 
                border: 2px solid {pnl_color}; 
                border-radius: 8px; 
                padding: 12px; 
                min-height: 80px;
            ">
                <div style="color: {pnl_color}; font-weight: bold; font-size: 14px;">
                    P&L: ${summary['pnl']:.0f}
                </div>
                <div style="color: #666; font-size: 12px; margin: 4px 0;">
                    Win Rate: {summary['win_rate']:.0f}%
                </div>
                <div style="color: #666; font-size: 11px;">
                    W: {summary['wins']} L: {summary['losses']}
                </div>
            </div>
            """, unsafe_allow_html=True)
          # Add spacing between weeks
        st.markdown("<br>", unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header with custom styling
    st.markdown("""
    <div class="main-header">
        <h1>📈 TradeCraft Trading Journal</h1>
        <p style="margin: 0; opacity: 0.9;">Simple. Clean. Effective.</p>
    </div>
    """, unsafe_allow_html=True)
      # Add a refresh button and data info
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Refresh Data", help="Clear cache and reload data"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Toggle Stats", help="Show/hide summary statistics"):
            st.session_state.show_summary = not st.session_state.get('show_summary', True)
    
    with col3:
        if st.button("➕ Add Trade", help="Add a new trade"):
            st.session_state.show_add_form = not st.session_state.get('show_add_form', False)
    
    # Initialize session state
    if 'show_summary' not in st.session_state:
        st.session_state.show_summary = True
      # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    st.sidebar.markdown("---")
    
    # Load accounts for current user
    accounts_df = load_accounts()
    if not accounts_df.empty:
        account_options = {f"{row['name']} (ID: {row['id']})": row['id'] 
                         for _, row in accounts_df.iterrows()}
        selected_account_display = st.sidebar.selectbox("Account", list(account_options.keys()))
        selected_account = account_options[selected_account_display]
    else:
        st.sidebar.warning("No accounts found")
        selected_account = None
        
    # Load trades for current user
    trades_df = load_trades(account_id=selected_account)
    
    # For personal use, always show the add trade form if no trades exist
    if trades_df.empty:
        if selected_account:
            # Show trade entry form when no trades exist
            show_add_trade_form(selected_account)
            
            # Also show some helpful info
            st.markdown("---")
            st.markdown("### 💡 Getting Started Tips")
            st.info("""
            **Welcome to TradeCraft!** Here are some tips to get you started:
            
            1. **Add trades manually** using the form above
            2. **Import from CSV** (feature coming soon)
            3. **Use demo accounts** (alice/bob) to see sample data            4. **Explore analytics** once you have some trades
            """)
        else:
            st.warning("Please select an account to add trades.")
        st.stop()
    
    # Get filter options
    all_symbols = get_unique_symbols(trades_df)
    all_tags = get_unique_tags(trades_df)
    
    # Quick date filters
    st.sidebar.markdown("### 📅 Quick Dates")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Today", key="today"):
            st.session_state.date_filter = "today"
        if st.button("This Week", key="this_week"):
            st.session_state.date_filter = "this_week"
        if st.button("This Month", key="this_month"):
            st.session_state.date_filter = "this_month"
        if st.button("This Year", key="this_year"):
            st.session_state.date_filter = "this_year"
    
    with col2:
        if st.button("Yesterday", key="yesterday"):
            st.session_state.date_filter = "yesterday"
        if st.button("Last Week", key="last_week"):
            st.session_state.date_filter = "last_week"
        if st.button("Last Month", key="last_month"):
            st.session_state.date_filter = "last_month"
        if st.button("Last Year", key="last_year"):
            st.session_state.date_filter = "last_year"
    
    if st.sidebar.button("All Time", key="all_time"):
        st.session_state.date_filter = "all_time"
    
    # Calculate date range based on quick filter
    today = datetime.now().date()
    
    if st.session_state.get('date_filter') == "today":
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif st.session_state.get('date_filter') == "yesterday":
        yesterday = today - timedelta(days=1)
        start_date = datetime.combine(yesterday, datetime.min.time())
        end_date = datetime.combine(yesterday, datetime.max.time())
    elif st.session_state.get('date_filter') == "this_week":
        start_of_week = today - timedelta(days=today.weekday())
        start_date = datetime.combine(start_of_week, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif st.session_state.get('date_filter') == "last_week":
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        start_date = datetime.combine(start_of_last_week, datetime.min.time())
        end_date = datetime.combine(end_of_last_week, datetime.max.time())
    elif st.session_state.get('date_filter') == "this_month":
        start_of_month = today.replace(day=1)
        start_date = datetime.combine(start_of_month, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif st.session_state.get('date_filter') == "last_month":
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        start_of_last_month = last_month.replace(day=1)
        start_date = datetime.combine(start_of_last_month, datetime.min.time())
        end_date = datetime.combine(last_month, datetime.max.time())
    elif st.session_state.get('date_filter') == "this_year":
        start_of_year = today.replace(month=1, day=1)
        start_date = datetime.combine(start_of_year, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif st.session_state.get('date_filter') == "last_year":
        start_of_last_year = today.replace(year=today.year-1, month=1, day=1)
        end_of_last_year = today.replace(year=today.year-1, month=12, day=31)
        start_date = datetime.combine(start_of_last_year, datetime.min.time())
        end_date = datetime.combine(end_of_last_year, datetime.max.time())
    else:
        # Default to full date range or custom date picker
        min_date = trades_df['opened_at'].min().date() if 'opened_at' in trades_df.columns else today
        max_date = trades_df['opened_at'].max().date() if 'opened_at' in trades_df.columns else today
        
        st.sidebar.markdown("### 📅 Custom Date Range")
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())
        else:
            start_date = datetime.combine(date_range[0], datetime.min.time())
            end_date = datetime.combine(date_range[0], datetime.max.time())
    
    st.sidebar.markdown("---")
    
    # Symbol filter
    st.sidebar.markdown("### 📊 Filters")
    if all_symbols:
        selected_symbols = st.sidebar.multiselect("Symbols", all_symbols, default=[], key="symbol_filter")
    else:
        selected_symbols = []
    
    # Tag filter (only show if tags exist)
    if all_tags:
        selected_tags = st.sidebar.multiselect("Tags", all_tags, default=[], key="tag_filter")
    else:
        selected_tags = []
        st.sidebar.info("💡 No tags found. Add tags to your trades to enable tag filtering.")
    
    # Show active filters
    active_filters = []
    if st.session_state.get('date_filter'):
        active_filters.append(f"📅 {st.session_state.date_filter.replace('_', ' ').title()}")
    if selected_symbols:
        active_filters.append(f"🎯 {len(selected_symbols)} symbol(s)")
    if selected_tags:
        active_filters.append(f"🏷️ {len(selected_tags)} tag(s)")
    
    if active_filters:
        st.sidebar.markdown("### 🎯 Active Filters")
        for filter_name in active_filters:
            st.sidebar.markdown(f"• {filter_name}")
        
        if st.sidebar.button("🗑️ Clear All Filters"):
            st.session_state.date_filter = None
            st.session_state.symbol_filter = []
            st.session_state.tag_filter = []
            st.rerun()
    
    # Apply filters
    filtered_df = filter_trades(trades_df, selected_symbols, selected_tags, start_date, end_date)
    
    # Show add trade form if requested
    if st.session_state.get('show_add_form', False) and selected_account:
        st.markdown("---")
        show_add_trade_form(selected_account)
        st.markdown("---")
    
    # Main content
    if filtered_df.empty:
        st.warning("No trades match your filters.")
        return
    
    # Stats overview
    stats = calculate_portfolio_stats(filtered_df)
      # Display summary statistics if enabled
    if st.session_state.show_summary:
        st.markdown("### 📊 Portfolio Performance")
        
        # Performance Overview - Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pnl_delta = f"${stats['total_pnl']:,.2f}" if stats['total_pnl'] != 0 else None
            pnl_color = "normal" if stats['total_pnl'] >= 0 else "inverse"
            st.metric(
                "Total P&L", 
                f"${stats['total_pnl']:,.2f}",
                delta=pnl_delta,
                delta_color=pnl_color,
                help="Total profit/loss for selected trades"
            )
        
        with col2:
            st.metric(
                "Total Trades", 
                f"{stats['total_trades']:,}", 
                help="Total number of trades in selected period"
            )
        
        with col3:
            avg_pnl = stats['total_pnl'] / stats['total_trades'] if stats['total_trades'] > 0 else 0
            avg_color = "normal" if avg_pnl >= 0 else "inverse"
            st.metric(
                "Avg P&L per Trade", 
                f"${avg_pnl:.2f}",
                delta=f"${avg_pnl:.2f}" if avg_pnl != 0 else None,
                delta_color=avg_color,
                help="Average profit/loss per trade"
            )
        
        with col4:
            profit_factor = abs(stats['avg_win'] / stats['avg_loss']) if stats.get('avg_loss', 0) != 0 else 0
            pf_color = "normal" if profit_factor >= 1.0 else "inverse"
            st.metric(
                "Profit Factor", 
                f"{profit_factor:.2f}",
                delta=f"{profit_factor:.2f}" if profit_factor != 0 else None,
                delta_color=pf_color,
                help="Average win divided by average loss (>1.0 is profitable)"
            )
        
        # Win/Loss Analysis
        st.markdown("#### 🎯 Win/Loss Analysis")
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            win_rate_color = "normal" if stats['win_rate'] >= 50 else "inverse"
            st.metric(
                "Win Rate", 
                f"{stats['win_rate']:.1f}%",
                delta=f"{stats['win_rate']:.1f}%",
                delta_color=win_rate_color,
                help="Percentage of winning trades"
            )
        
        with col6:
            # Calculate loss rate
            loss_rate = 100 - stats['win_rate']
            loss_rate_color = "inverse" if loss_rate >= 50 else "normal"
            st.metric(
                "Loss Rate", 
                f"{loss_rate:.1f}%",
                delta=f"{loss_rate:.1f}%",
                delta_color=loss_rate_color,
                help="Percentage of losing trades"
            )
        
        with col7:
            # Calculate number of wins and losses
            wins = int(stats['total_trades'] * stats['win_rate'] / 100) if stats['total_trades'] > 0 else 0
            st.metric(
                "Winning Trades", 
                f"{wins:,}",
                help="Number of profitable trades"
            )
        
        with col8:
            losses = stats['total_trades'] - wins
            st.metric(
                "Losing Trades", 
                f"{losses:,}",
                help="Number of unprofitable trades"
            )
        
        # Trade Performance Details
        st.markdown("#### 💰 Trade Performance Details")
        col9, col10, col11, col12 = st.columns(4)
        
        with col9:
            avg_win_color = "normal" if stats['avg_win'] > 0 else "inverse"
            st.metric(
                "Avg Win", 
                f"${stats['avg_win']:.2f}" if stats['avg_win'] > 0 else "$0.00",
                delta=f"${stats['avg_win']:.2f}" if stats['avg_win'] > 0 else None,
                delta_color=avg_win_color,
                help="Average profit per winning trade"
            )
        
        with col10:
            avg_loss_color = "inverse" if stats['avg_loss'] < 0 else "normal"
            st.metric(
                "Avg Loss", 
                f"${stats['avg_loss']:.2f}" if stats['avg_loss'] < 0 else "$0.00",
                delta=f"${stats['avg_loss']:.2f}" if stats['avg_loss'] < 0 else None,
                delta_color=avg_loss_color,
                help="Average loss per losing trade"
            )
        
        with col11:
            best_color = "normal" if stats['largest_win'] > 0 else "inverse"
            st.metric(
                "Best Trade", 
                f"${stats['largest_win']:.2f}",
                delta=f"${stats['largest_win']:.2f}" if stats['largest_win'] > 0 else None,
                delta_color=best_color,
                help="Largest winning trade"
            )
        
        with col12:
            worst_color = "inverse" if stats['largest_loss'] < 0 else "normal"
            st.metric(
                "Worst Trade", 
                f"${stats['largest_loss']:.2f}",
                delta=f"${stats['largest_loss']:.2f}" if stats['largest_loss'] < 0 else None,
                delta_color=worst_color,
                help="Largest losing trade"
            )
        
        # Advanced Portfolio Metrics
        st.markdown("#### 🎯 Advanced Metrics")
        col13, col14, col15, col16 = st.columns(4)
        
        with col13:
            expectancy_color = "normal" if stats.get('expectancy', 0) > 0 else "inverse"
            st.metric(
                "Expectancy", 
                f"${stats.get('expectancy', 0):.2f}",
                delta=f"${stats.get('expectancy', 0):.2f}" if stats.get('expectancy', 0) != 0 else None,
                delta_color=expectancy_color,
                help="Expected value per trade: (Win Rate × Avg Win) + (Loss Rate × Avg Loss)"
            )
        
        with col14:
            avg_daily_vol = stats.get('avg_daily_vol', 0)
            st.metric(
                "Avg Daily Volume", 
                f"{avg_daily_vol:.1f}",
                help="Average number of trades per trading day"
            )
        
        with col15:
            avg_size = stats.get('avg_size', 0)
            st.metric(
                "Avg Position Size", 
                f"${avg_size:.2f}" if avg_size > 0 else "N/A",
                help="Average position size based on entry prices"
            )
        
        with col16:
            max_win_streak = stats.get('max_win_streak', 0)
            max_loss_streak = stats.get('max_loss_streak', 0)
            streak_text = f"W:{max_win_streak} / L:{max_loss_streak}"
            st.metric(
                "Max Streaks", 
                streak_text,
                help=f"Maximum consecutive wins: {max_win_streak}, Maximum consecutive losses: {max_loss_streak}"
            )
        
        # Hold Time Analysis
        st.markdown("#### ⏱️ Hold Time Analysis")
        col17, col18, col19, col20 = st.columns(4)
        
        with col17:
            avg_win_hold = stats.get('avg_win_hold_time', 0)
            st.metric(
                "Avg Win Hold Time", 
                f"{avg_win_hold:.1f} days" if avg_win_hold > 0 else "N/A",
                help="Average number of days winning trades are held"
            )
        
        with col18:
            avg_loss_hold = stats.get('avg_loss_hold_time', 0)
            st.metric(
                "Avg Loss Hold Time", 
                f"{avg_loss_hold:.1f} days" if avg_loss_hold > 0 else "N/A",
                help="Average number of days losing trades are held"
            )
        
        with col19:
            # Calculate hold time ratio if both values exist
            if avg_win_hold > 0 and avg_loss_hold > 0:
                hold_ratio = avg_win_hold / avg_loss_hold
                ratio_color = "normal" if hold_ratio > 1.0 else "inverse"
                st.metric(
                    "Hold Time Ratio", 
                    f"{hold_ratio:.2f}",
                    delta=f"{hold_ratio:.2f}",
                    delta_color=ratio_color,
                    help="Ratio of average win hold time to average loss hold time (>1.0 means winners held longer)"
                )
            else:
                st.metric(
                    "Hold Time Ratio", 
                    "N/A",
                    help="Ratio of average win hold time to average loss hold time"
                )
        
        with col20:
            # Calculate total hold time if we have the data
            total_hold_time = (avg_win_hold * len(stats.get('wins', [])) + 
                             avg_loss_hold * len(stats.get('losses', []))) if avg_win_hold > 0 and avg_loss_hold > 0 else 0
            if total_hold_time == 0:
                # Fallback calculation
                total_hold_time = (avg_win_hold + avg_loss_hold) * stats.get('total_trades', 0) / 2
            
            st.metric(
                "Est. Total Time", 
                f"{total_hold_time:.0f} days" if total_hold_time > 0 else "N/A",
                help="Estimated total time capital was deployed in trades"
            )
        
        st.markdown("---")
    
    # Main content in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", "📋 Trades", "📊 Analytics", "🗓️ Calendar"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Equity curve
            st.subheader("📈 Equity Curve")
            equity_fig = create_equity_curve(filtered_df)
            st.plotly_chart(equity_fig, use_container_width=True)
        
        with col2:
            # P&L Distribution
            if 'realized_pnl' in filtered_df.columns or 'pnl' in filtered_df.columns:
                st.subheader("📊 P&L Distribution")
                pnl_col = 'realized_pnl' if 'realized_pnl' in filtered_df.columns else 'pnl'
                
                fig_hist = px.histogram(filtered_df, x=pnl_col, nbins=20,
                                       title="P&L Distribution",
                                       labels={pnl_col: 'P&L ($)'})
                fig_hist.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_hist, use_container_width=True)
        
        # Additional charts row
        col3, col4 = st.columns(2)
        
        with col3:
            # Win/Loss pie chart
            if 'realized_pnl' in filtered_df.columns or 'pnl' in filtered_df.columns:
                pnl_col = 'realized_pnl' if 'realized_pnl' in filtered_df.columns else 'pnl'
                wins = filtered_df[filtered_df[pnl_col] > 0]
                losses = filtered_df[filtered_df[pnl_col] <= 0]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Wins', 'Losses'],
                    values=[len(wins), len(losses)],
                    hole=0.4,
                    marker_colors=['#28a745', '#dc3545']
                )])
                fig_pie.update_layout(title="Win/Loss Ratio", height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col4:
            # Monthly P&L if we have enough data
            if not filtered_df.empty and 'realized_pnl' in filtered_df.columns:
                pnl_col = 'realized_pnl'
                date_col = 'closed_at' if 'closed_at' in filtered_df.columns else 'opened_at'
                
                # Create monthly P&L chart
                df_monthly = filtered_df.dropna(subset=[date_col, pnl_col]).copy()
                if not df_monthly.empty:
                    df_monthly['month'] = df_monthly[date_col].dt.to_period('M')
                    monthly_pnl = df_monthly.groupby('month')[pnl_col].sum().reset_index()
                    monthly_pnl['month_str'] = monthly_pnl['month'].astype(str)
                    
                    fig_monthly = px.bar(monthly_pnl, x='month_str', y=pnl_col,
                                        title="Monthly P&L",
                                        labels={pnl_col: 'P&L ($)', 'month_str': 'Month'})
                    fig_monthly.update_layout(height=400, showlegend=False)
                    # Color bars based on positive/negative
                    colors = ['#28a745' if x >= 0 else '#dc3545' for x in monthly_pnl[pnl_col]]
                    fig_monthly.update_traces(marker_color=colors)
                    st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab2:
        # Recent trades table
        st.subheader("📋 Recent Trades")
        st.markdown("*Click on a row to view trade legs below*")
        
        # Select relevant columns for display
        display_cols = []
        available_cols = filtered_df.columns.tolist()
        
        # Common columns to show with their preferred order
        preferred_cols = [
            'asset_symbol', 'symbol',  # Symbol columns
            'status', 'realized_pnl', 'pnl',  # P&L columns
            'avg_buy_price', 'avg_sell_price', 'total_fees',  # Price columns
            'opened_at', 'closed_at',  # Date columns
            'tags', 'notes'  # Additional info
        ]
        
        for col in preferred_cols:
            if col in available_cols and col not in display_cols:
                display_cols.append(col)
        
        # Add any remaining important columns
        for col in available_cols:
            if col not in display_cols and col not in ['id', 'user_id', 'account_id', 'trade_id', 'created_at', 'updated_at']:
                display_cols.append(col)
        
        # Limit to first 10 columns if too many
        display_cols = display_cols[:10]
        
        if not filtered_df.empty and 'id' in filtered_df.columns:
            if display_cols:
                display_df = filtered_df[display_cols].head(20).copy()
                
                # Store the original trade IDs for selection mapping
                trade_ids = filtered_df['id'].head(20).tolist()
                
                # Format numeric columns
                for col in display_df.columns:
                    if display_df[col].dtype in ['float64', 'float32']:
                        if any(keyword in col.lower() for keyword in ['price', 'pnl', 'fee']):
                            display_df[col] = display_df[col].round(2)
                            # Format as currency for P&L columns
                            if 'pnl' in col.lower():
                                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
                            else:
                                display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
                
                # Format date columns
                for col in display_df.columns:
                    if 'at' in col.lower() and display_df[col].dtype == 'datetime64[ns]':
                        display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M')
                
                # Use st.dataframe with selection mode
                selected_rows = st.dataframe(
                    display_df, 
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="trades_table"
                )
                
                # Check if a row is selected
                if selected_rows['selection']['rows']:
                    selected_idx = selected_rows['selection']['rows'][0]
                    if selected_idx < len(trade_ids):
                        selected_trade_id = trade_ids[selected_idx]
                        
                        # Show trade legs for selected trade
                        st.markdown("---")
                        st.subheader("🔍 Trade Legs for Selected Trade")
                        
                        # Get trade info for display
                        selected_trade = filtered_df[filtered_df['id'] == selected_trade_id].iloc[0]
                        symbol = selected_trade.get('asset_symbol', selected_trade.get('symbol', 'N/A'))
                        pnl = selected_trade.get('realized_pnl', selected_trade.get('pnl', 0))
                        opened_at = selected_trade.get('opened_at', 'N/A')
                        
                        # Format trade info
                        if pd.notna(opened_at) and hasattr(opened_at, 'strftime'):
                            date_str = opened_at.strftime('%Y-%m-%d %H:%M')
                        else:
                            date_str = str(opened_at)[:16] if str(opened_at) != 'N/A' else 'N/A'
                        
                        pnl_str = f"${pnl:,.2f}" if pd.notna(pnl) else "$0.00"
                        
                        st.info(f"**Trade:** {symbol} | **Date:** {date_str} | **P&L:** {pnl_str} | **ID:** {selected_trade_id}")
                        
                        # Load and display trade legs
                        with st.spinner("Loading trade legs..."):
                            legs_df = load_trade_legs(selected_trade_id)
                        
                        if not legs_df.empty:
                            # Format the legs dataframe for display
                            display_legs_df = legs_df.copy()
                            
                            # Format numeric columns
                            for col in display_legs_df.columns:
                                if display_legs_df[col].dtype in ['float64', 'float32']:
                                    if any(keyword in col.lower() for keyword in ['price', 'amount', 'fee', 'value']):
                                        display_legs_df[col] = display_legs_df[col].round(4)
                                        # Format as currency for price/amount columns
                                        if 'price' in col.lower():
                                            display_legs_df[col] = display_legs_df[col].apply(lambda x: f"${x:.4f}" if pd.notna(x) else "")
                                        elif 'amount' in col.lower() or 'value' in col.lower():
                                            display_legs_df[col] = display_legs_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
                                        elif 'fee' in col.lower():
                                            display_legs_df[col] = display_legs_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
                            
                            # Format date columns
                            for col in display_legs_df.columns:
                                if 'at' in col.lower() and display_legs_df[col].dtype == 'datetime64[ns]':
                                    display_legs_df[col] = display_legs_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            st.dataframe(display_legs_df, use_container_width=True)
                            
                            # Add some basic stats about the legs
                            if len(legs_df) > 0:
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Legs", len(legs_df))
                                with col2:
                                    if 'side' in legs_df.columns:
                                        buy_count = len(legs_df[legs_df['side'].str.upper() == 'BUY'])
                                        st.metric("Buy Orders", buy_count)
                                with col3:
                                    if 'side' in legs_df.columns:
                                        sell_count = len(legs_df[legs_df['side'].str.upper() == 'SELL'])
                                        st.metric("Sell Orders", sell_count)
                                with col4:
                                    if 'quantity' in legs_df.columns:
                                        total_qty = legs_df['quantity'].sum()
                                        st.metric("Total Quantity", f"{total_qty:,.0f}")
                        else:
                            st.warning("No trade legs found for this trade.")
                else:
                    st.info("👆 Click on a row in the table above to view its trade legs")
            else:
                # Fallback if no display columns
                selected_rows = st.dataframe(
                    filtered_df.head(20), 
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="trades_table_fallback"
                )
        else:
            st.info("No trades available to display.")
    
    with tab3:
        st.subheader("📊 Advanced Analytics")
        
        if filtered_df.empty:
            st.info("No data available for analytics. Please adjust your filters.")
            return
        
        # Top section: Key Performance Metrics
        st.markdown("#### 🎯 Performance Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Risk/Reward Ratio
            if 'realized_pnl' in filtered_df.columns:
                wins = filtered_df[filtered_df['realized_pnl'] > 0]['realized_pnl']
                losses = filtered_df[filtered_df['realized_pnl'] < 0]['realized_pnl']
                risk_reward = abs(wins.mean() / losses.mean()) if len(losses) > 0 and len(wins) > 0 else 0
                rr_color = "normal" if risk_reward >= 1.0 else "inverse"
                st.metric(
                    "Risk/Reward Ratio",
                    f"{risk_reward:.2f}",
                    delta=f"{risk_reward:.2f}",
                    delta_color=rr_color,
                    help="Average win size divided by average loss size"
                )
        
        with col2:
            # Sharpe Ratio approximation (using daily returns)
            if 'realized_pnl' in filtered_df.columns:
                daily_returns = filtered_df['realized_pnl']
                sharpe = daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0
                sharpe_color = "normal" if sharpe > 0 else "inverse"
                st.metric(
                    "Return/Volatility",
                    f"{sharpe:.2f}",
                    delta=f"{sharpe:.2f}",
                    delta_color=sharpe_color,
                    help="Average return divided by volatility (Sharpe-like ratio)"
                )
        
        with col3:
            # Recovery Factor
            if 'realized_pnl' in filtered_df.columns:
                total_pnl = filtered_df['realized_pnl'].sum()
                max_drawdown = filtered_df['realized_pnl'].cumsum().expanding().max() - filtered_df['realized_pnl'].cumsum()
                max_dd = max_drawdown.max() if len(max_drawdown) > 0 else 1
                recovery_factor = total_pnl / max_dd if max_dd > 0 else 0
                rf_color = "normal" if recovery_factor > 0 else "inverse"
                st.metric(
                    "Recovery Factor",
                    f"{recovery_factor:.2f}",
                    delta=f"{recovery_factor:.2f}",
                    delta_color=rf_color,
                    help="Total profit divided by maximum drawdown"
                )
        
        with col4:
            # Trade Frequency
            if 'opened_at' in filtered_df.columns:
                df_with_dates = filtered_df.dropna(subset=['opened_at'])
                if not df_with_dates.empty:
                    date_range = (df_with_dates['opened_at'].max() - df_with_dates['opened_at'].min()).days
                    frequency = len(df_with_dates) / max(date_range, 1) * 30  # trades per month
                    st.metric(
                        "Monthly Frequency",
                        f"{frequency:.1f}",
                        help="Average number of trades per month"
                    )
        
        st.markdown("---")
        
        # Main Analytics Grid
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Symbol Performance
            st.markdown("#### 📈 Symbol Performance Analysis")
            if 'asset_symbol' in filtered_df.columns and 'realized_pnl' in filtered_df.columns:
                symbol_analysis = filtered_df.groupby('asset_symbol').agg({
                    'realized_pnl': ['sum', 'count', 'mean', 'std'],
                    'id': 'count'
                }).round(2)
                
                # Flatten column names
                symbol_analysis.columns = ['Total P&L', 'PnL Count', 'Avg P&L', 'P&L Std', 'Trade Count']
                symbol_analysis['Win Rate'] = filtered_df.groupby('asset_symbol')['realized_pnl'].apply(lambda x: (x > 0).mean() * 100).round(1)
                symbol_analysis['Sharpe'] = (symbol_analysis['Avg P&L'] / symbol_analysis['P&L Std']).fillna(0).round(2)
                
                # Sort by total P&L
                symbol_analysis = symbol_analysis.sort_values('Total P&L', ascending=False).reset_index()
                
                # Display top performers
                st.write("**Top 10 Symbols by Total P&L**")
                display_cols = ['asset_symbol', 'Total P&L', 'Trade Count', 'Avg P&L', 'Win Rate', 'Sharpe']
                st.dataframe(
                    symbol_analysis[display_cols].head(10),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Symbol P&L chart
                top_symbols = symbol_analysis.head(8)
                if not top_symbols.empty:
                    fig_symbols = px.bar(
                        top_symbols,
                        x='asset_symbol',
                        y='Total P&L',
                        title="P&L by Symbol (Top 8)",
                        color='Total P&L',
                        color_continuous_scale=['red', 'yellow', 'green']
                    )
                    fig_symbols.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_symbols, use_container_width=True)
            else:
                st.info("Symbol data not available")
        
        with col2:
            # PnL by Tags Analysis
            st.markdown("#### 🏷️ Tag Performance Analysis")
            if 'tags' in filtered_df.columns and 'realized_pnl' in filtered_df.columns:
                # Process tags (handle both string and list formats)
                tag_rows = []
                for _, row in filtered_df.iterrows():
                    tags = row['tags']
                    if pd.isna(tags) or tags == '':
                        continue
                    
                    if isinstance(tags, str):
                        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
                    elif isinstance(tags, list):
                        tag_list = tags
                    else:
                        continue
                    
                    for tag in tag_list:
                        tag_rows.append({
                            'tag': tag,
                            'pnl': row['realized_pnl'],
                            'trade_id': row['id']
                        })
                
                if tag_rows:
                    tag_df = pd.DataFrame(tag_rows)
                    tag_stats = tag_df.groupby('tag').agg({
                        'pnl': ['sum', 'count', 'mean'],
                        'trade_id': 'nunique'
                    }).round(2)
                    
                    # Flatten columns
                    tag_stats.columns = ['Total P&L', 'Entries', 'Avg P&L', 'Unique Trades']
                    tag_stats['Win Rate'] = tag_df.groupby('tag')['pnl'].apply(lambda x: (x > 0).mean() * 100).round(1)
                    tag_stats = tag_stats.sort_values('Total P&L', ascending=False).reset_index()
                    
                    st.write("**Performance by Tag**")
                    st.dataframe(
                        tag_stats.head(10),
                        use_container_width=True,
                        hide_index=True
                    )                    # Tag P&L visualization
                    if len(tag_stats) > 0 and not tag_stats.empty:
                        top_tags = tag_stats.head(8)
                        if not top_tags.empty:
                            fig_tags = px.bar(
                                top_tags,
                                x='tag',
                                y='Total P&L',
                                title="P&L by Tag (Top 8)",
                                color='Total P&L',
                                color_continuous_scale=['red', 'yellow', 'green']
                            )
                            fig_tags.update_layout(height=350, showlegend=False)
                            fig_tags.update_xaxes(tickangle=45)
                            st.plotly_chart(fig_tags, use_container_width=True)
                else:
                    st.info("No tag data available")
            else:
                st.info("Tag data not available")
        
        st.markdown("---")
        
        # Second row: Time-based and Risk Analysis
        col3, col4 = st.columns(2)
        
        with col3:
            # Monthly Performance Analysis
            st.markdown("#### 📅 Monthly Performance Trends")
            if 'opened_at' in filtered_df.columns and 'realized_pnl' in filtered_df.columns:
                df_monthly = filtered_df.dropna(subset=['opened_at']).copy()
                if not df_monthly.empty:
                    df_monthly['month'] = df_monthly['opened_at'].dt.to_period('M')
                    monthly_stats = df_monthly.groupby('month').agg({
                        'realized_pnl': ['sum', 'count', 'mean'],
                    }).round(2)
                    
                    monthly_stats.columns = ['Total P&L', 'Trades', 'Avg P&L']
                    monthly_stats['Win Rate'] = df_monthly.groupby('month')['realized_pnl'].apply(lambda x: (x > 0).mean() * 100).round(1)
                    monthly_stats = monthly_stats.reset_index()
                    monthly_stats['month'] = monthly_stats['month'].astype(str)
                    
                    if len(monthly_stats) > 1:
                        fig_monthly = px.line(
                            monthly_stats,
                            x='month',
                            y='Total P&L',
                            title="Monthly P&L Trend",
                            markers=True
                        )
                        fig_monthly.update_layout(height=300)
                        fig_monthly.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_monthly, use_container_width=True)
                        
                        # Monthly stats table
                        st.write("**Monthly Statistics**")
                        st.dataframe(
                            monthly_stats.tail(6),  # Show last 6 months
                            use_container_width=True,
                            hide_index=True
                        )
            
            # Day of Week Analysis
            st.markdown("#### 📊 Day of Week Performance")
            if 'opened_at' in filtered_df.columns:
                df_with_dates = filtered_df.dropna(subset=['opened_at']).copy()
                if not df_with_dates.empty:
                    df_with_dates['day_of_week'] = df_with_dates['opened_at'].dt.day_name()
                    
                    # Performance by day
                    if 'realized_pnl' in df_with_dates.columns:
                        day_performance = df_with_dates.groupby('day_of_week').agg({
                            'realized_pnl': ['sum', 'count', 'mean'],
                        }).round(2)
                        day_performance.columns = ['Total P&L', 'Trades', 'Avg P&L']
                        day_performance['Win Rate'] = df_with_dates.groupby('day_of_week')['realized_pnl'].apply(lambda x: (x > 0).mean() * 100).round(1)
                        
                        # Reorder by weekday
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        day_performance = day_performance.reindex([day for day in day_order if day in day_performance.index])
                        
                        fig_dow = px.bar(
                            day_performance.reset_index(),
                            x='day_of_week',
                            y='Total P&L',
                            title="P&L by Day of Week",
                            color='Total P&L',
                            color_continuous_scale=['red', 'yellow', 'green']
                        )
                        fig_dow.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig_dow, use_container_width=True)
        
        with col4:
            # Risk Analysis
            st.markdown("#### ⚠️ Risk Analysis")
            if 'realized_pnl' in filtered_df.columns:
                pnl_series = filtered_df['realized_pnl']
                
                # Drawdown analysis
                cumulative_pnl = pnl_series.cumsum()
                running_max = cumulative_pnl.expanding().max()
                drawdown = running_max - cumulative_pnl
                max_drawdown = drawdown.max()
                
                # Risk metrics
                col4a, col4b = st.columns(2)
                with col4a:
                    st.metric(
                        "Max Drawdown",
                        f"${max_drawdown:.2f}",
                        delta=f"-${max_drawdown:.2f}",
                        delta_color="inverse",
                        help="Maximum peak-to-trough decline"
                    )
                
                with col4b:
                    var_95 = pnl_series.quantile(0.05)  # 5% VaR
                    st.metric(
                        "5% VaR",
                        f"${var_95:.2f}",
                        delta=f"${var_95:.2f}",
                        delta_color="inverse" if var_95 < 0 else "normal",
                        help="5% Value at Risk - potential loss on worst 5% of trades"
                    )
                
                # P&L Distribution Analysis
                fig_dist = px.histogram(
                    filtered_df,
                    x='realized_pnl',
                    nbins=25,
                    title="P&L Distribution",
                    labels={'realized_pnl': 'P&L ($)', 'count': 'Frequency'}
                )
                fig_dist.add_vline(x=pnl_series.mean(), line_dash="dash", 
                                 annotation_text=f"Mean: ${pnl_series.mean():.2f}")
                fig_dist.add_vline(x=pnl_series.median(), line_dash="dot", 
                                 annotation_text=f"Median: ${pnl_series.median():.2f}")
                fig_dist.update_layout(height=300)
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Outlier Analysis
                q1 = pnl_series.quantile(0.25)
                q3 = pnl_series.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers_low = pnl_series[pnl_series < lower_bound]
                outliers_high = pnl_series[pnl_series > upper_bound]
                
                st.write("**Outlier Analysis**")
                col4c, col4d = st.columns(2)
                with col4c:
                    st.metric("Large Losses", len(outliers_low), help="Trades below Q1 - 1.5*IQR")
                with col4d:
                    st.metric("Large Wins", len(outliers_high), help="Trades above Q3 + 1.5*IQR")
        
        st.markdown("---")
        
        # Bottom section: Asset Allocation and Advanced Charts
        col5, col6 = st.columns(2)
        
        with col5:
            # Asset Type Allocation
            st.markdown("#### 🥧 Asset Allocation")
            if 'asset_type' in filtered_df.columns:
                asset_counts = filtered_df['asset_type'].value_counts()
                if not asset_counts.empty:
                    colors = ['#1AA9E5', '#00FFCC', '#FF4C6A', '#FFA500', '#9966CC']
                    fig_allocation = go.Figure(go.Pie(
                        labels=asset_counts.index,
                        values=asset_counts.values,
                        hole=0.4,
                        marker=dict(colors=colors[:len(asset_counts)])
                    ))
                    fig_allocation.update_layout(
                        title="Trades by Asset Type",
                        height=350,
                        showlegend=True
                    )
                    st.plotly_chart(fig_allocation, use_container_width=True)
                    
                    # Asset performance table
                    if 'realized_pnl' in filtered_df.columns:
                        asset_performance = filtered_df.groupby('asset_type').agg({
                            'realized_pnl': ['sum', 'count', 'mean'],
                        }).round(2)
                        asset_performance.columns = ['Total P&L', 'Trades', 'Avg P&L']
                        asset_performance['Win Rate'] = filtered_df.groupby('asset_type')['realized_pnl'].apply(lambda x: (x > 0).mean() * 100).round(1)
                        
                        st.write("**Performance by Asset Type**")
                        st.dataframe(
                            asset_performance.sort_values('Total P&L', ascending=False),
                            use_container_width=True
                        )
            else:
                st.info("Asset type data not available")
        
        with col6:
            # Trade Duration vs P&L Analysis
            st.markdown("#### ⏱️ Duration vs Performance")
            if 'opened_at' in filtered_df.columns and 'closed_at' in filtered_df.columns and 'realized_pnl' in filtered_df.columns:
                duration_df = filtered_df.dropna(subset=['opened_at', 'closed_at']).copy()
                if not duration_df.empty:
                    duration_df['duration_days'] = (duration_df['closed_at'] - duration_df['opened_at']).dt.total_seconds() / (24 * 3600)
                    
                    # Duration bins analysis
                    duration_df['duration_bin'] = pd.cut(
                        duration_df['duration_days'], 
                        bins=[0, 1, 7, 30, 90, float('inf')],
                        labels=['< 1 day', '1-7 days', '1-4 weeks', '1-3 months', '> 3 months']
                    )
                    
                    duration_analysis = duration_df.groupby('duration_bin').agg({
                        'realized_pnl': ['sum', 'count', 'mean'],
                    }).round(2)
                    duration_analysis.columns = ['Total P&L', 'Trades', 'Avg P&L']
                    duration_analysis['Win Rate'] = duration_df.groupby('duration_bin')['realized_pnl'].apply(lambda x: (x > 0).mean() * 100).round(1)
                    
                    st.write("**Performance by Hold Duration**")
                    st.dataframe(
                        duration_analysis,
                        use_container_width=True
                    )
                    
                    # Scatter plot: Duration vs P&L
                    sample_size = min(200, len(duration_df))  # Limit points for performance
                    duration_sample = duration_df.sample(n=sample_size) if len(duration_df) > sample_size else duration_df
                    
                    fig_duration = px.scatter(
                        duration_sample,
                        x='duration_days',
                        y='realized_pnl',
                        title="Trade Duration vs P&L",
                        labels={'duration_days': 'Duration (Days)', 'realized_pnl': 'P&L ($)'},
                        opacity=0.6,
                        color='realized_pnl',
                        color_continuous_scale=['red', 'yellow', 'green']
                    )
                    fig_duration.update_layout(height=350)
                    st.plotly_chart(fig_duration, use_container_width=True)
            else:
                st.info("Duration data not available")
    
    with tab4:
        # Calendar view
        st.subheader("🗓️ Trade Calendar")
        
        # Initialize calendar state
        if 'cal_year' not in st.session_state:
            st.session_state.cal_year = datetime.now().year
        if 'cal_month' not in st.session_state:
            st.session_state.cal_month = datetime.now().month
        
        # Month selection controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("📅 Today", key="cal_today"):
                st.session_state.cal_year = datetime.now().year
                st.session_state.cal_month = datetime.now().month
                st.rerun()
        
        with col2:
            # Month/Year selector
            selected_date = st.date_input(
                "Select Month/Year",
                value=datetime(st.session_state.cal_year, st.session_state.cal_month, 1),
                key="calendar_date_picker"
            )
            
            if selected_date:
                if (selected_date.year != st.session_state.cal_year or 
                    selected_date.month != st.session_state.cal_month):
                    st.session_state.cal_year = selected_date.year
                    st.session_state.cal_month = selected_date.month
                    st.rerun()
        
        # Create and display calendar
        calendar_data = create_calendar_data(filtered_df, st.session_state.cal_year, st.session_state.cal_month)
        
        if calendar_data['weeks']:
            render_calendar(calendar_data)
            
            # Monthly summary
            st.markdown("---")
            st.subheader("📈 Monthly Summary")
            
            # Calculate monthly totals
            month_trades = get_trades_by_day(filtered_df, st.session_state.cal_year, st.session_state.cal_month)
            if not month_trades.empty:
                pnl_col = 'realized_pnl' if 'realized_pnl' in month_trades.columns else 'pnl'
                
                total_pnl = month_trades[pnl_col].sum() if pnl_col in month_trades.columns else 0
                total_trades = len(month_trades)
                winning_trades = len(month_trades[month_trades[pnl_col] > 0]) if pnl_col in month_trades.columns else 0
                losing_trades = len(month_trades[month_trades[pnl_col] < 0]) if pnl_col in month_trades.columns else 0
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                # Monthly metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Monthly P&L", f"${total_pnl:,.2f}", 
                             delta=f"${total_pnl:,.2f}" if total_pnl != 0 else None)
                
                with col2:
                    st.metric("Total Trades", total_trades)
                
                with col3:
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                with col4:
                    avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
                    st.metric("Avg P&L per Trade", f"${avg_pnl:.2f}")
                
                # Trading activity chart for the month
                if len(month_trades) > 0:
                    st.subheader("📊 Daily Trading Activity")
                    
                    # Create daily activity chart
                    daily_data = month_trades.groupby('date').agg({
                        pnl_col: 'sum',
                        'id': 'count'
                    }).reset_index()
                    daily_data.columns = ['Date', 'P&L', 'Trades']
                    
                    # P&L over time
                    fig = go.Figure()
                    
                    # Add P&L bars
                    colors = ['green' if pnl >= 0 else 'red' for pnl in daily_data['P&L']]
                    fig.add_trace(go.Bar(
                        x=daily_data['Date'],
                        y=daily_data['P&L'],
                        name='Daily P&L',
                        marker_color=colors,
                        hovertemplate='<b>%{x}</b><br>P&L: $%{y:.2f}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title=f"Daily P&L - {calendar.month_name[st.session_state.cal_month]} {st.session_state.cal_year}",
                        xaxis_title="Date",
                        yaxis_title="P&L ($)",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No trades found for {calendar.month_name[st.session_state.cal_month]} {st.session_state.cal_year}")
        else:
            st.error("Unable to generate calendar data")
        if 'cal_year' not in st.session_state:
            st.session_state.cal_year = datetime.now().year
        if 'cal_month' not in st.session_state:
            st.session_state.cal_month = datetime.now().month
          # Create and display calendar
        calendar_data = create_calendar_data(filtered_df, st.session_state.cal_year, st.session_state.cal_month)
        
        if calendar_data['weeks']:
            render_calendar(calendar_data)
        else:
            st.error("Unable to generate calendar data")
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit - Simple & Effective Trading Journal*")
    
    # Data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Data Summary")
    st.sidebar.metric("Total Trades", len(trades_df))
    st.sidebar.metric("Filtered Trades", len(filtered_df))
    st.sidebar.metric("Date Range", f"{(end_date - start_date).days} days")

def show_add_trade_form(account_id: int):
    """Show form to add a new trade."""
    st.markdown("### 🚀 Add Your First Trade!")
    st.markdown("Let's get started by adding a trade to your journal.")
    
    with st.form("add_trade_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol", placeholder="e.g., AAPL, TSLA", help="Stock symbol or ticker")
            asset_type = st.selectbox("Asset Type", 
                                    ["stock", "option", "crypto", "forex", "future", "other"])
            action = st.selectbox("Action", 
                                ["buy", "sell", "buy to open", "sell to close", "buy to close", "sell to open"])
            quantity = st.number_input("Quantity", min_value=1, value=100, step=1)
        
        with col2:
            price = st.number_input("Price", min_value=0.01, value=100.0, step=0.01, format="%.2f")
            fees = st.number_input("Fees", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            trade_date = st.date_input("Trade Date", value=datetime.now().date())
            notes = st.text_area("Notes", placeholder="Optional notes about this trade")
        
        # Tags
        tags = st.text_input("Tags", placeholder="e.g., momentum, earnings, swing (comma-separated)")
        
        submitted = st.form_submit_button("🎯 Add Trade", use_container_width=True)
        
        if submitted:
            if not symbol:
                st.error("Please enter a symbol")
                return False
            
            try:                # Import the trade insertion function
                import sys
                sys.path.append('.')
                from utils.db_access import insert_trade, insert_trade_leg
                
                # For personal use, use default user ID
                default_user_id = 13  # Using existing user from database
                
                # Create the trade
                trade_date_str = datetime.combine(trade_date, datetime.now().time()).isoformat()
                trade_id = insert_trade(
                    user_id=default_user_id,
                    account_id=account_id,
                    asset_symbol=symbol.upper(),
                    asset_type=asset_type,
                    opened_at=trade_date_str,
                    notes=notes,
                    tags=tags
                )
                
                # Add the trade leg
                leg_id = insert_trade_leg(
                    trade_id=trade_id,
                    action=action,
                    quantity=quantity,
                    price=price,
                    fees=fees,
                    executed_at=trade_date_str,
                    notes=f"{action} {quantity} shares at ${price}"
                )
                
                st.success(f"✅ Trade added successfully! Trade ID: {trade_id}")
                st.balloons()                
                # Clear cache and rerun to show the new trade
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error adding trade: {e}")
                return False
    
    return True

if __name__ == "__main__":
    main()
