import streamlit as st
import pandas as pd
from datetime import datetime

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
    # --- Edit mode state ---
    if 'edit_trade_id' not in st.session_state:
        st.session_state['edit_trade_id'] = None
    if 'edit_trade_data' not in st.session_state:
        st.session_state['edit_trade_data'] = None

    # --- Fetch trades for table and edit/delete actions ---
    trades_df = db.fetch_trades()
    if not trades_df.empty:
        trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date
        # Add action columns
        for idx, row in trades_df.iterrows():
            col1, col2 = st.columns([1,1], gap="small")
            with col1:
                if st.button(f"Edit {row['id']}", key=f"edit_{row['id']}"):
                    st.session_state['edit_trade_id'] = row['id']
                    st.session_state['edit_trade_data'] = row
            with col2:
                if st.button(f"Delete {row['id']}", key=f"delete_{row['id']}"):
                    if st.confirm(f"Delete trade {row['id']}? This cannot be undone."):
                        db.delete_trade(row['id'])
                        st.success(f"Trade {row['id']} deleted.")
                        st.rerun()
        st.dataframe(trades_df)
        st.download_button('Export CSV', trades_df.to_csv(index=False),
                           'trades.csv')
    else:
        st.info('No trades recorded yet.')

    # --- Add/Edit Trade Form ---
    if st.session_state['edit_trade_id']:
        st.subheader('Edit Trade')
        edit_row = st.session_state['edit_trade_data']
        with st.form('edit_trade'):
            date = st.date_input('Date', edit_row['date'])
            ticker = st.text_input('Ticker', edit_row['ticker'])
            side = st.selectbox('Side', ['Buy', 'Sell'], index=0 if edit_row['side'].lower() == 'buy' else 1)
            quantity = st.number_input('Quantity', value=edit_row['quantity'], step=1.0)
            price = st.number_input('Price', value=edit_row['price'], step=0.01, format='%f')
            pnl = st.number_input('PnL', value=edit_row['pnl'], step=0.01, format='%f')
            notes = st.text_area('Notes', value=edit_row['notes'])
            tags = st.text_input('Tags (comma separated)', value=edit_row['tags'])
            submitted = st.form_submit_button('Update')
            cancel = st.form_submit_button('Cancel')
            if submitted and ticker:
                db.update_trade(
                    trade_id=edit_row['id'],
                    date=str(date),
                    ticker=ticker.upper(),
                    side=side,
                    quantity=quantity,
                    price=price,
                    pnl=pnl,
                    notes=notes,
                    tags=tags,
                )
                st.success('Trade updated')
                st.session_state['edit_trade_id'] = None
                st.session_state['edit_trade_data'] = None
                st.rerun()
            elif cancel:
                st.session_state['edit_trade_id'] = None
                st.session_state['edit_trade_data'] = None
                st.rerun()
    else:
        st.header('Add Trade')
        with st.form('add_trade'):
            date = st.date_input('Date', datetime.now().date())
            ticker = st.text_input('Ticker')
            side = st.selectbox('Side', ['Buy', 'Sell'])
            quantity = st.number_input('Quantity', value=0.0, step=1.0)
            price = st.number_input('Price', value=0.0, step=0.01, format='%f')
            pnl = st.number_input('PnL', value=0.0, step=0.01, format='%f')
            notes = st.text_area('Notes')
            tags = st.text_input('Tags (comma separated)')
            submitted = st.form_submit_button('Add')
            if submitted and ticker:
                db.add_trade(
                    date=str(date),
                    ticker=ticker.upper(),
                    side=side,
                    quantity=quantity,
                    price=price,
                    pnl=pnl,
                    notes=notes,
                    tags=tags,
                )
                st.success('Trade added')
                st.rerun()

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
