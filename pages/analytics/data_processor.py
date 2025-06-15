"""
Analytics Data Processing Module

Handles data processing and calculations for analytics.
This is part of the Model layer in MVVM pattern.
"""
from typing import List, Any
import pandas as pd
from dash import html, dash_table
import plotly.graph_objs as go
from components.stat_card import stat_card
from components.pnl_line_chart import pnl_over_time_figure


class AnalyticsDataProcessor:
    """
    Handles all data processing and calculations for analytics views.
    """
    
    @staticmethod
    def process_filtered_data(data_json: str) -> pd.DataFrame:
        """
        Process filtered data from JSON string.
        
        Args:
            data_json: JSON string of filtered trades data
            
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        if not data_json:
            return pd.DataFrame()
        
        from io import StringIO
        return pd.read_json(StringIO(data_json), orient="split")
    
    @staticmethod
    def calculate_summary_stats(df: pd.DataFrame) -> List[html.Div]:
        """
        Calculate comprehensive summary statistics.
        
        Args:
            df: DataFrame with trade data
            
        Returns:
            List of HTML components with statistics
        """
        if df.empty or "realized_pnl" not in df.columns:
            return [html.Div("No trades to summarize.")]

        # Basic metrics
        total_trades = len(df)
        wins = (df["realized_pnl"] > 0).sum()
        losses = (df["realized_pnl"] < 0).sum()
        win_rate = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
        expectancy = df["realized_pnl"].mean() if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = df[df["realized_pnl"] > 0]["realized_pnl"].sum()
        gross_loss = abs(df[df["realized_pnl"] < 0]["realized_pnl"].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Average win/loss amounts and percentages
        avg_win = df[df["realized_pnl"] > 0]["realized_pnl"].mean() if wins > 0 else 0
        avg_loss = df[df["realized_pnl"] < 0]["realized_pnl"].mean() if losses > 0 else 0
        avg_win_pct = df[df["realized_pnl"] > 0]["return_pct"].mean() if "return_pct" in df and wins > 0 else 0
        avg_loss_pct = df[df["realized_pnl"] < 0]["return_pct"].mean() if "return_pct" in df and losses > 0 else 0

        # Streaks
        win_streak = AnalyticsDataProcessor._calculate_max_streak(df["realized_pnl"] > 0) if total_trades else 0
        loss_streak = AnalyticsDataProcessor._calculate_max_streak(df["realized_pnl"] < 0) if total_trades else 0
        
        # Best/worst trades
        top_win = df["realized_pnl"].max() if not df.empty else 0
        top_loss = df["realized_pnl"].min() if not df.empty else 0
        top_win_pct = df.loc[df["realized_pnl"].idxmax(), "return_pct"] if not df.empty and "return_pct" in df else 0
        top_loss_pct = df.loc[df["realized_pnl"].idxmin(), "return_pct"] if not df.empty and "return_pct" in df else 0
        
        # Size and volume metrics
        avg_size = int(df["quantity"].mean()) if "quantity" in df and not df.empty else 0
        avg_daily_vol = AnalyticsDataProcessor._calculate_avg_daily_volume(df)
        
        # Hold times
        avg_win_hold, avg_loss_hold = AnalyticsDataProcessor._calculate_hold_times(df)

        # Create stat cards
        stat_cards = [
            stat_card("WIN RATE", f"{win_rate:.0f}%"),
            stat_card("EXPECTANCY", f"${expectancy:.2f}"),
            stat_card("PROFIT FACTOR", f"{profit_factor:.2f}"),
            stat_card("AVG WIN HOLD", avg_win_hold),
            stat_card("AVG LOSS HOLD", avg_loss_hold),
            stat_card("AVG LOSS", f"${avg_loss:.2f} ({avg_loss_pct:.1f}%)"),
            stat_card("AVG WIN", f"${avg_win:.2f} ({avg_win_pct:.1f}%)"),
            stat_card("WIN STREAK", f"{win_streak}"),
            stat_card("LOSS STREAK", f"{loss_streak}"),
            stat_card("TOP LOSS", f"${top_loss:.2f} ({top_loss_pct:.1f}%)"),
            stat_card("TOP WIN", f"${top_win:.2f} ({top_win_pct:.1f}%)"),
            stat_card("AVG DAILY VOL", f"{avg_daily_vol:.1f}"),
            stat_card("AVG SIZE", f"{avg_size}"),
        ]
        
        return [html.Div(stat_cards, className="stats-grid")]
    
    @staticmethod
    def create_asset_allocation_figure(df: pd.DataFrame) -> go.Figure:
        """
        Create asset allocation pie chart.
        
        Args:
            df: DataFrame with trade data
            
        Returns:
            Plotly Figure
        """
        if df.empty or "asset_type" not in df.columns:
            return go.Figure()
            
        asset_counts = df["asset_type"].value_counts()
        fig = go.Figure(go.Pie(
            labels=asset_counts.index,
            values=asset_counts.values,
            hole=0.4,
            marker=dict(colors=["#1AA9E5", "#00FFCC", "#23273A", "#b0dfff", "#FF4C6A"])
        ))
        
        fig.update_layout(
            title="Asset Allocation",
            height=300,
            paper_bgcolor="#23273A",
            font=dict(color="#F6F8FA", family="Inter,Roboto,Montserrat,sans-serif"),
            legend=dict(font=dict(color="#F6F8FA")),
        )
        
        return fig
    
    @staticmethod
    def create_tag_table(df: pd.DataFrame) -> Any:
        """
        Create PnL by tag table.
        
        Args:
            df: DataFrame with trade data
            
        Returns:
            Dash DataTable or Div
        """
        if df.empty or "tags" not in df.columns:
            return html.Div("No tag data available.")
            
        # Process tags (handle both string and list formats)
        tag_rows = []
        for _, row in df.iterrows():
            tags = row["tags"]
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            elif not isinstance(tags, list):
                continue
                
            for tag in tags:
                tag_rows.append({"tag": tag, "pnl": row["realized_pnl"]})
        
        if not tag_rows:
            return html.Div("No tag data available.")
            
        tag_df = pd.DataFrame(tag_rows)
        tag_stats = tag_df.groupby("tag").agg(
            trades=("pnl", "count"), 
            pnl=("pnl", "sum")
        ).reset_index()
        
        return dash_table.DataTable(
            columns=[
                {"name": "Tag", "id": "tag"},
                {"name": "Trades", "id": "trades"},
                {"name": "PnL", "id": "pnl", "type": "numeric", "format": {"specifier": "$.2f"}},
            ],
            data=tag_stats.to_dict("records"),
            style_table={"width": "100%"},
            style_cell={"background": "#23273A", "color": "#F6F8FA", "border": "none"},
            style_header={"background": "#181C25", "color": "#00FFCC", "fontWeight": "bold"},
        )
    
    @staticmethod
    def create_symbol_table(df: pd.DataFrame) -> Any:
        """
        Create PnL by symbol table.
        
        Args:
            df: DataFrame with trade data
            
        Returns:
            Dash DataTable or Div
        """
        if df.empty or "symbol" not in df.columns:
            return html.Div("No symbol data available.")
            
        symbol_stats = df.groupby("symbol").agg(
            trades=("realized_pnl", "count"), 
            pnl=("realized_pnl", "sum")
        ).reset_index()
        
        return dash_table.DataTable(
            columns=[
                {"name": "Symbol", "id": "symbol"},
                {"name": "Trades", "id": "trades"},
                {"name": "PnL", "id": "pnl", "type": "numeric", "format": {"specifier": "$.2f"}},
            ],
            data=symbol_stats.to_dict("records"),            style_table={"width": "100%"},
            style_cell={"background": "#23273A", "color": "#F6F8FA", "border": "none"},
            style_header={"background": "#181C25", "color": "#00FFCC", "fontWeight": "bold"},
        )

    # Helper methods    @staticmethod
    def _calculate_max_streak(series: pd.Series) -> int:
        """Calculate maximum consecutive streak in a boolean series."""
        if series.empty:
            return 0
        
        # Convert to boolean to ensure we have True/False values
        bool_series = series.astype(bool)
        
        # Find groups of consecutive values (both True and False)
        # Create group IDs by cumulative sum of changes
        group_ids = (bool_series != bool_series.shift()).cumsum()
        
        # For each group, get the count of values
        groups = bool_series.groupby(group_ids)
        streak_counts = groups.size()
        
        # Filter to only the groups with the same value as the first occurrence
        # This handles both True and False streaks
        max_streak = 0
        for group_id, group_data in groups:
            if group_data.iloc[0]:  # This is a True streak
                max_streak = max(max_streak, len(group_data))
        
        # Also check False streaks if the series contains False values
        for group_id, group_data in groups:
            if not group_data.iloc[0]:  # This is a False streak
                max_streak = max(max_streak, len(group_data))
        
        return max_streak

    @staticmethod
    def _calculate_avg_daily_volume(df: pd.DataFrame) -> float:
        """Calculate average daily trading volume."""
        if "opened_at" not in df.columns or df.empty:
            return 0
            
        df_copy = df.copy()
        df_copy["opened_at"] = pd.to_datetime(df_copy["opened_at"])
        daily_counts = df_copy.groupby(df_copy["opened_at"].dt.date).size()
        return daily_counts.mean() if not daily_counts.empty else 0
    
    @staticmethod
    def _calculate_hold_times(df: pd.DataFrame) -> tuple[str, str]:
        """Calculate average hold times for wins and losses."""
        if "opened_at" not in df.columns or "closed_at" not in df.columns:
            return "-", "-"
            
        df_copy = df.copy()
        df_copy["opened_at"] = pd.to_datetime(df_copy["opened_at"])
        df_copy["closed_at"] = pd.to_datetime(df_copy["closed_at"])
        
        # Calculate hold times in days
        win_mask = df_copy["realized_pnl"] > 0
        loss_mask = df_copy["realized_pnl"] < 0
        
        win_holds = (df_copy[win_mask]["closed_at"] - df_copy[win_mask]["opened_at"]).dt.days
        loss_holds = (df_copy[loss_mask]["closed_at"] - df_copy[loss_mask]["opened_at"]).dt.days
        
        # Format as days, but fallback to hours if less than 1 day
        def format_hold_time(hold_series):
            if hold_series.empty:
                return "-"
            avg_days = hold_series.mean()
            if avg_days >= 1:
                return f"{avg_days:.1f} days"
            else:
                # Convert to hours for sub-day holdings
                avg_hours = (df_copy[win_mask if hold_series is win_holds else loss_mask]["closed_at"] - 
                           df_copy[win_mask if hold_series is win_holds else loss_mask]["opened_at"]).dt.total_seconds().mean() / 3600
                return f"{avg_hours:.1f}h"
        
        avg_win_hold = format_hold_time(win_holds)
        avg_loss_hold = format_hold_time(loss_holds)
        
        return avg_win_hold, avg_loss_hold
