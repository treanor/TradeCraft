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
def load_trades(user_id: int = 3, account_id: Optional[int] = None) -> pd.DataFrame:
    """Load trades from database with P&L calculations."""
    try:
        conn = sqlite3.connect("data/tradecraft.db")
        
        query = """
        SELECT * FROM trades 
        WHERE user_id = ?
        """
        params = [user_id]
        
        if account_id:
            query += " AND account_id = ?"
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
    """Load available accounts."""
    try:
        conn = sqlite3.connect("data/tradecraft.db")
        df = pd.read_sql_query("SELECT id, name FROM accounts ORDER BY name", conn)
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
    """Calculate portfolio statistics."""
    # Default stats structure
    default_stats = {
        'total_trades': 0,
        'total_pnl': 0.0,
        'win_rate': 0.0,
        'avg_win': 0.0,
        'avg_loss': 0.0,
        'largest_win': 0.0,
        'largest_loss': 0.0
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
    
    return {
        'total_trades': len(df_clean),
        'total_pnl': df_clean[pnl_col].sum(),
        'win_rate': len(wins) / len(df_clean) * 100 if len(df_clean) > 0 else 0,
        'avg_win': wins[pnl_col].mean() if len(wins) > 0 else 0,
        'avg_loss': losses[pnl_col].mean() if len(losses) > 0 else 0,
        'largest_win': df_clean[pnl_col].max() if len(df_clean) > 0 else 0,
        'largest_loss': df_clean[pnl_col].min() if len(df_clean) > 0 else 0
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
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Refresh Data", help="Clear cache and reload data"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Toggle Stats", help="Show/hide summary statistics"):
            st.session_state.show_summary = not st.session_state.get('show_summary', True)
    
    # Initialize session state
    if 'show_summary' not in st.session_state:
        st.session_state.show_summary = True
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    st.sidebar.markdown("---")
    
    # Load accounts
    accounts_df = load_accounts()
    if not accounts_df.empty:
        account_options = {f"{row['name']} (ID: {row['id']})": row['id'] 
                         for _, row in accounts_df.iterrows()}
        selected_account_display = st.sidebar.selectbox("Account", list(account_options.keys()))
        selected_account = account_options[selected_account_display]
    else:
        st.sidebar.warning("No accounts found")
        selected_account = None
    
    # Load trades
    trades_df = load_trades(user_id=3, account_id=selected_account)
    
    if trades_df.empty:
        st.warning("No trades found. Add some trades to your database to get started!")
        st.stop()
    
    # Get filter options
    all_symbols = get_unique_symbols(trades_df)
    all_tags = get_unique_tags(trades_df)
    
    # Date range filter
    min_date = trades_df['opened_at'].min().date() if 'opened_at' in trades_df.columns else datetime.now().date()
    max_date = trades_df['opened_at'].max().date() if 'opened_at' in trades_df.columns else datetime.now().date()
    
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
    
    # Symbol filter
    if all_symbols:
        selected_symbols = st.sidebar.multiselect("Symbols", all_symbols, default=[])
    else:
        selected_symbols = []
    
    # Tag filter
    if all_tags:
        selected_tags = st.sidebar.multiselect("Tags", all_tags, default=[])
    else:
        selected_tags = []
    
    # Apply filters
    filtered_df = filter_trades(trades_df, selected_symbols, selected_tags, start_date, end_date)
    
    # Main content
    if filtered_df.empty:
        st.warning("No trades match your filters.")
        return
    
    # Stats overview
    stats = calculate_portfolio_stats(filtered_df)
    
    if st.session_state.show_summary:
        st.markdown("### 📊 Portfolio Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Trades", 
                f"{stats['total_trades']:,}", 
                help="Total number of trades in selected period"
            )
        
        with col2:
            pnl_delta = f"${stats['total_pnl']:,.2f}" if stats['total_pnl'] != 0 else None
            st.metric(
                "Total P&L", 
                f"${stats['total_pnl']:,.2f}",
                delta=pnl_delta,
                help="Total profit/loss for selected trades"
            )
        
        with col3:
            win_rate_color = "🟢" if stats['win_rate'] >= 50 else "🔴"
            st.metric(
                "Win Rate", 
                f"{win_rate_color} {stats['win_rate']:.1f}%",
                help="Percentage of winning trades"
            )
        
        with col4:
            profit_factor = abs(stats['avg_win'] / stats['avg_loss']) if stats.get('avg_loss', 0) != 0 else 0
            pf_color = "🟢" if profit_factor >= 1.5 else "🟡" if profit_factor >= 1.0 else "🔴"
            st.metric(
                "Profit Factor", 
                f"{pf_color} {profit_factor:.2f}",
                help="Average win divided by average loss"
            )
        
        # Additional metrics row
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                "Avg Win", 
                f"${stats['avg_win']:.2f}" if stats['avg_win'] > 0 else "$0.00",
                help="Average profit per winning trade"
            )
        
        with col6:
            st.metric(
                "Avg Loss", 
                f"${stats['avg_loss']:.2f}" if stats['avg_loss'] < 0 else "$0.00",
                help="Average loss per losing trade"
            )
        
        with col7:
            st.metric(
                "Best Trade", 
                f"${stats['largest_win']:.2f}",
                help="Largest winning trade"
            )
        
        with col8:
            st.metric(
                "Worst Trade", 
                f"${stats['largest_loss']:.2f}",
                help="Largest losing trade"
            )
        
        st.markdown("---")
    
    # Main content in tabs
    tab1, tab2, tab3 = st.tabs(["📈 Charts", "📋 Trades", "📊 Analytics"])
    
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
        
        if display_cols:
            display_df = filtered_df[display_cols].head(20).copy()
            
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
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(filtered_df.head(20), use_container_width=True)
    
    with tab3:
        st.subheader("📊 Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Symbol performance
            if 'asset_symbol' in filtered_df.columns and 'realized_pnl' in filtered_df.columns:
                symbol_pnl = filtered_df.groupby('asset_symbol')['realized_pnl'].agg(['sum', 'count', 'mean']).reset_index()
                symbol_pnl.columns = ['Symbol', 'Total P&L', 'Trades', 'Avg P&L']
                symbol_pnl = symbol_pnl.sort_values('Total P&L', ascending=False)
                
                st.write("**Top Performing Symbols**")
                st.dataframe(symbol_pnl.head(10), use_container_width=True)
        
        with col2:
            # Trading frequency by day of week
            if 'opened_at' in filtered_df.columns:
                df_with_dates = filtered_df.dropna(subset=['opened_at']).copy()
                if not df_with_dates.empty:
                    df_with_dates['day_of_week'] = df_with_dates['opened_at'].dt.day_name()
                    day_counts = df_with_dates['day_of_week'].value_counts()
                    
                    fig_days = px.bar(
                        x=day_counts.values, 
                        y=day_counts.index,
                        orientation='h',
                        title="Trading Activity by Day of Week",
                        labels={'x': 'Number of Trades', 'y': 'Day of Week'}
                    )
                    fig_days.update_layout(height=300)
                    st.plotly_chart(fig_days, use_container_width=True)
        
        # Trade duration analysis
        if 'opened_at' in filtered_df.columns and 'closed_at' in filtered_df.columns:
            duration_df = filtered_df.dropna(subset=['opened_at', 'closed_at']).copy()
            if not duration_df.empty:
                duration_df['duration_days'] = (duration_df['closed_at'] - duration_df['opened_at']).dt.total_seconds() / (24 * 3600)
                
                col3, col4 = st.columns(2)
                
                with col3:
                    fig_duration = px.histogram(
                        duration_df, 
                        x='duration_days',
                        nbins=20,
                        title="Trade Duration Distribution",
                        labels={'duration_days': 'Duration (Days)', 'count': 'Number of Trades'}
                    )
                    fig_duration.update_layout(height=400)
                    st.plotly_chart(fig_duration, use_container_width=True)
                
                with col4:
                    # Duration vs P&L scatter
                    if 'realized_pnl' in duration_df.columns:
                        fig_scatter = px.scatter(
                            duration_df,
                            x='duration_days',
                            y='realized_pnl',
                            title="Trade Duration vs P&L",
                            labels={'duration_days': 'Duration (Days)', 'realized_pnl': 'P&L ($)'}
                        )
                        fig_scatter.update_layout(height=400)
                        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit - Simple & Effective Trading Journal*")
    
    # Data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Data Summary")
    st.sidebar.metric("Total Trades", len(trades_df))
    st.sidebar.metric("Filtered Trades", len(filtered_df))
    st.sidebar.metric("Date Range", f"{len((end_date - start_date).days)} days")

if __name__ == "__main__":
    main()
