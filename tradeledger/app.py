import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

import db
import utils

# Initialize database
if 'db_initialized' not in st.session_state:
    db.init_db()
    st.session_state['db_initialized'] = True

st.title('TradeLedger')

pages = ['Trade Log', 'Dashboard']
page = st.sidebar.selectbox('Navigation', pages)

if page == 'Trade Log':
    st.header('Add Trade')
    with st.form('add_trade'):
        input_date = st.date_input('Date', datetime.now().date())
        ticker = st.text_input('Ticker')
        side = st.selectbox('Side', ['Buy', 'Sell'])
        quantity = st.number_input('Quantity', value=0.0, step=1.0)
        price = st.number_input('Price', value=0.0, step=0.01, format='%f')
        pnl = st.number_input('PnL', value=0.0, step=0.01, format='%f')
        notes = st.text_area('Notes')
        tags = st.text_input('Tags (comma separated)')
        submitted = st.form_submit_button('Add')
        if submitted:
            if not ticker:
                st.error('Ticker is required')
            else:
                db.add_trade(
                    date=str(input_date),
                    ticker=ticker.upper(),
                    side=side,
                    quantity=quantity,
                    price=price,
                    pnl=pnl,
                    notes=notes,
                    tags=tags,
                )
                st.success('Trade added')

    st.header('Trades')
    trades_df = db.fetch_trades()
    if not trades_df.empty:
        trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date

        st.subheader('Filters')
        filter_ticker = st.text_input('Ticker contains')
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input('Start date', trades_df['date'].min())
        with col2:
            end_date = st.date_input('End date', trades_df['date'].max())

        if filter_ticker:
            trades_df = trades_df[trades_df['ticker'].str.contains(filter_ticker.upper())]
        trades_df = trades_df[(trades_df['date'] >= start_date) & (trades_df['date'] <= end_date)]

        st.dataframe(trades_df, use_container_width=True)
        st.download_button('Export CSV', trades_df.to_csv(index=False),
                           'trades.csv')

        if not trades_df.empty:
            st.subheader('Edit Trade')
            edit_id = st.selectbox('Trade ID', trades_df['id'])
            row = trades_df[trades_df['id'] == edit_id].iloc[0]
            with st.form('edit_trade'):
                e_date = st.date_input('Date', row['date'], key='edit_date')
                e_ticker = st.text_input('Ticker', row['ticker'], key='edit_ticker')
                e_side = st.selectbox('Side', ['Buy', 'Sell'], index=0 if row['side']=='Buy' else 1, key='edit_side')
                e_qty = st.number_input('Quantity', value=float(row['quantity']), step=1.0, key='edit_qty')
                e_price = st.number_input('Price', value=float(row['price']), step=0.01, format='%f', key='edit_price')
                e_pnl = st.number_input('PnL', value=float(row['pnl']), step=0.01, format='%f', key='edit_pnl')
                e_notes = st.text_area('Notes', value=row['notes'], key='edit_notes')
                e_tags = st.text_input('Tags (comma separated)', value=row['tags'], key='edit_tags')
                update_sub = st.form_submit_button('Update')
                if update_sub:
                    if not e_ticker:
                        st.error('Ticker is required')
                    else:
                        db.update_trade(
                            edit_id,
                            str(e_date),
                            e_ticker.upper(),
                            e_side,
                            e_qty,
                            e_price,
                            e_pnl,
                            e_notes,
                            e_tags,
                        )
                        st.success('Trade updated')
                        st.experimental_rerun()

            if st.button('Delete Trade'):
                db.delete_trade(edit_id)
                st.success('Trade deleted')
                st.experimental_rerun()
    else:
        st.info('No trades recorded yet.')

elif page == 'Dashboard':
    st.header('Performance Dashboard')
    trades_df = db.fetch_trades()
    if trades_df.empty:
        st.info('No trades to display.')
    else:
        trades_df['date'] = pd.to_datetime(trades_df['date'])
        daily = utils.aggregate_pnl(trades_df, 'D')
        weekly = utils.aggregate_pnl(trades_df, 'W')
        monthly = utils.aggregate_pnl(trades_df, 'M')

        st.subheader('Daily P&L')
        st.line_chart(daily.set_index('date'))

        st.subheader('Weekly P&L')
        st.bar_chart(weekly.set_index('date'))

        st.subheader('Monthly P&L')
        st.bar_chart(monthly.set_index('date'))

        equity = utils.equity_curve(trades_df)
        st.subheader('Equity Curve')
        st.line_chart(equity.set_index('date'))
