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
            utils.rerun()

    trades_df = db.fetch_trades()

    # Handle edit form
    if st.session_state.get('edit_id') is not None:
        trade_to_edit = trades_df[trades_df['id'] == st.session_state['edit_id']]
        if not trade_to_edit.empty:
            trade = trade_to_edit.iloc[0]
            st.subheader('Edit Trade')
            with st.form('edit_trade'):
                date = st.date_input('Date', trade['date'], key='edit_date')
                ticker = st.text_input('Ticker', trade['ticker'], key='edit_ticker')
                side = st.selectbox('Side', ['Buy', 'Sell'], index=0 if trade['side'] == 'Buy' else 1, key='edit_side')
                quantity = st.number_input('Quantity', value=float(trade['quantity']), step=1.0, key='edit_qty')
                price = st.number_input('Price', value=float(trade['price']), step=0.01, format='%f', key='edit_price')
                pnl = st.number_input('PnL', value=float(trade['pnl']), step=0.01, format='%f', key='edit_pnl')
                notes = st.text_area('Notes', trade['notes'], key='edit_notes')
                tags = st.text_input('Tags (comma separated)', trade['tags'], key='edit_tags')
                submitted = st.form_submit_button('Update')
            if submitted:
                db.update_trade(
                    trade_id=int(trade['id']),
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
                st.session_state['edit_id'] = None
                utils.rerun()
            if st.button('Cancel Edit'):
                st.session_state['edit_id'] = None
                utils.rerun()

    # Handle delete confirmation
    if st.session_state.get('delete_id') is not None:
        trade_to_delete = trades_df[trades_df['id'] == st.session_state['delete_id']]
        if not trade_to_delete.empty:
            trade = trade_to_delete.iloc[0]
            st.warning(f"Delete trade {trade['ticker']} on {trade['date']}?")
            col1, col2 = st.columns(2)
            if col1.button('Confirm Delete'):
                db.delete_trade(int(trade['id']))
                st.session_state['delete_id'] = None
                st.success('Trade deleted')
                utils.rerun()
            if col2.button('Cancel'):
                st.session_state['delete_id'] = None
                utils.rerun()

    st.header('Trades')
    if not trades_df.empty:
        trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date
        st.dataframe(trades_df)
        for _, row in trades_df.iterrows():
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(
                f"{row['date']} {row['ticker']} {row['side']} Qty:{row['quantity']} "
                f"Price:{row['price']} PnL:{row['pnl']}"
            )
            if c2.button('Edit', key=f"edit_{row['id']}"):
                st.session_state['edit_id'] = row['id']
                utils.rerun()
            if c3.button('Delete', key=f"delete_{row['id']}"):
                st.session_state['delete_id'] = row['id']
                utils.rerun()
        st.download_button('Export CSV', trades_df.to_csv(index=False),
                           'trades.csv')
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
