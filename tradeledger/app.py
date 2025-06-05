import streamlit as st
import pandas as pd
from datetime import datetime

from . import db
from . import utils

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

    st.header('Trades')
    trades_df = db.fetch_trades()
    if not trades_df.empty:
        trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date
        st.dataframe(trades_df)
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
