import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import db
import utils
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Inject custom CSS for dark theme and modern look
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #181c24 !important;
        color: #e0e6f0 !important;
    }
    .css-1d391kg, .css-1lcbmhc, .stSidebar, .css-6qob1r {
        background: #23283a !important;
        color: #e0e6f0 !important;
    }
    .stButton>button, .stDownloadButton>button {
        background: #2d334a !important;
        color: #e0e6f0 !important;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1.2em;
    }
    .stDataFrame, .stTable {
        background: #23283a !important;
        color: #e0e6f0 !important;
        border-radius: 10px;
    }
    .st-bb, .st-cq, .st-dx, .st-e3, .st-em, .st-en, .st-eo, .st-ep, .st-eq, .st-er, .st-es, .st-et, .st-eu, .st-ev, .st-ew, .st-ex, .st-ey, .st-ez, .st-fa, .st-fb, .st-fc, .st-fd, .st-fe, .st-ff, .st-fg, .st-fh, .st-fi, .st-fj, .st-fk, .st-fl, .st-fm, .st-fn, .st-fo, .st-fp, .st-fq, .st-fr, .st-fs, .st-ft, .st-fu, .st-fv, .st-fw, .st-fx, .st-fy, .st-fz, .st-ga, .st-gb, .st-gc, .st-gd, .st-ge, .st-gf, .st-gg, .st-gh, .st-gi, .st-gj, .st-gk, .st-gl, .st-gm, .st-gn, .st-go, .st-gp, .st-gq, .st-gr, .st-gs, .st-gt, .st-gu, .st-gv, .st-gw, .st-gx, .st-gy, .st-gz, .st-ha, .st-hb, .st-hc, .st-hd, .st-he, .st-hf, .st-hg, .st-hh, .st-hi, .st-hj, .st-hk, .st-hl, .st-hm, .st-hn, .st-ho, .st-hp, .st-hq, .st-hr, .st-hs, .st-ht, .st-hu, .st-hv, .st-hw, .st-hx, .st-hy, .st-hz, .st-ia, .st-ib, .st-ic, .st-id, .st-ie, .st-if, .st-ig, .st-ih, .st-ii, .st-ij, .st-ik, .st-il, .st-im, .st-in, .st-io, .st-ip, .st-iq, .st-ir, .st-is, .st-it, .st-iu, .st-iv, .st-iw, .st-ix, .st-iy, .st-iz, .st-ja, .st-jb, .st-jc, .st-jd, .st-je, .st-jf, .st-jg, .st-jh, .st-ji, .st-jj, .st-jk, .st-jl, .st-jm, .st-jn, .st-jo, .st-jp, .st-jq, .st-jr, .st-js, .st-jt, .st-ju, .st-jv, .st-jw, .st-jx, .st-jy, .st-jz, .st-ka, .st-kb, .st-kc, .st-kd, .st-ke, .st-kf, .st-kg, .st-kh, .st-ki, .st-kj, .st-kk, .st-kl, .st-km, .st-kn, .st-ko, .st-kp, .st-kq, .st-kr, .st-ks, .st-kt, .st-ku, .st-kv, .st-kw, .st-kx, .st-ky, .st-kz, .st-la, .st-lb, .st-lc, .st-ld, .st-le, .st-lf, .st-lg, .st-lh, .st-li, .st-lj, .st-lk, .st-ll, .st-lm, .st-ln, .st-lo, .st-lp, .st-lq, .st-lr, .st-ls, .st-lt, .st-lu, .st-lv, .st-lw, .st-lx, .st-ly, .st-lz, .st-ma, .st-mb, .st-mc, .st-md, .st-me, .st-mf, .st-mg, .st-mh, .st-mi, .st-mj, .st-mk, .st-ml, .st-mm, .st-mn, .st-mo, .st-mp, .st-mq, .st-mr, .st-ms, .st-mt, .st-mu, .st-mv, .st-mw, .st-mx, .st-my, .st-mz, .st-na, .st-nb, .st-nc, .st-nd, .st-ne, .st-nf, .st-ng, .st-nh, .st-ni, .st-nj, .st-nk, .st-nl, .st-nm, .st-nn, .st-no, .st-np, .st-nq, .st-nr, .st-ns, .st-nt, .st-nu, .st-nv, .st-nw, .st-nx, .st-ny, .st-nz, .st-oa, .st-ob, .st-oc, .st-od, .st-oe, .st-of, .st-og, .st-oh, .st-oi, .st-oj, .st-ok, .st-ol, .st-om, .st-on, .st-oo, .st-op, .st-oq, .st-or, .st-os, .st-ot, .st-ou, .st-ov, .st-ow, .st-ox, .st-oy, .st-oz, .st-pa, .st-pb, .st-pc, .st-pd, .st-pe, .st-pf, .st-pg, .st-ph, .st-pi, .st-pj, .st-pk, .st-pl, .st-pm, .st-pn, .st-po, .st-pp, .st-pq, .st-pr, .st-ps, .st-pt, .st-pu, .st-pv, .st-pw, .st-px, .st-py, .st-pz, .st-qa, .st-qb, .st-qc, .st-qd, .st-qe, .st-qf, .st-qg, .st-qh, .st-qi, .st-qj, .st-qk, .st-ql, .st-qm, .st-qn, .st-qo, .st-qp, .st-qq, .st-qr, .st-qs, .st-qt, .st-qu, .st-qv, .st-qw, .st-qx, .st-qy, .st-qz, .st-ra, .st-rb, .st-rc, .st-rd, .st-re, .st-rf, .st-rg, .st-rh, .st-ri, .st-rj, .st-rk, .st-rl, .st-rm, .st-rn, .st-ro, .st-rp, .st-rq, .st-rr, .st-rs, .st-rt, .st-ru, .st-rv, .st-rw, .st-rx, .st-ry, .st-rz, .st-sa, .st-sb, .st-sc, .st-sd, .st-se, .st-sf, .st-sg, .st-sh, .st-si, .st-sj, .st-sk, .st-sl, .st-sm, .st-sn, .st-so, .st-sp, .st-sq, .st-sr, .st-ss, .st-st, .st-su, .st-sv, .st-sw, .st-sx, .st-sy, .st-sz, .st-ta, .st-tb, .st-tc, .st-td, .st-te, .st-tf, .st-tg, .st-th, .st-ti, .st-tj, .st-tk, .st-tl, .st-tm, .st-tn, .st-to, .st-tp, .st-tq, .st-tr, .st-ts, .st-tt, .st-tu, .st-tv, .st-tw, .st-tx, .st-ty, .st-tz, .st-ua, .st-ub, .st-uc, .st-ud, .st-ue, .st-uf, .st-ug, .st-uh, .st-ui, .st-uj, .st-uk, .st-ul, .st-um, .st-un, .st-uo, .st-up, .st-uq, .st-ur, .st-us, .st-ut, .st-uu, .st-uv, .st-uw, .st-ux, .st-uy, .st-uz, .st-va, .st-vb, .st-vc, .st-vd, .st-ve, .st-vf, .st-vg, .st-vh, .st-vi, .st-vj, .st-vk, .st-vl, .st-vm, .st-vn, .st-vo, .st-vp, .st-vq, .st-vr, .st-vs, .st-vt, .st-vu, .st-vv, .st-vw, .st-vx, .st-vy, .st-vz, .st-wa, .st-wb, .st-wc, .st-wd, .st-we, .st-wf, .st-wg, .st-wh, .st-wi, .st-wj, .st-wk, .st-wl, .st-wm, .st-wn, .st-wo, .st-wp, .st-wq, .st-wr, .st-ws, .st-wt, .st-wu, .st-wv, .st-ww, .st-wx, .st-wy, .st-wz, .st-xa, .st-xb, .st-xc, .st-xd, .st-xe, .st-xf, .st-xg, .st-xh, .st-xi, .st-xj, .st-xk, .st-xl, .st-xm, .st-xn, .st-xo, .st-xp, .st-xq, .st-xr, .st-xs, .st-xt, .st-xu, .st-xv, .st-xw, .st-xx, .st-xy, .st-xz, .st-ya, .st-yb, .st-yc, .st-yd, .st-ye, .st-yf, .st-yg, .st-yh, .st-yi, .st-yj, .st-yk, .st-yl, .st-ym, .st-yn, .st-yo, .st-yp, .st-yq, .st-yr, .st-ys, .st-yt, .st-yu, .st-yv, .st-yw, .st-yx, .st-yy, .st-yz, .st-za, .st-zb, .st-zc, .st-zd, .st-ze, .st-zf, .st-zg, .st-zh, .st-zi, .st-zj, .st-zk, .st-zl, .st-zm, .st-zn, .st-zo, .st-zp, .st-zq, .st-zr, .st-zs, .st-zt, .st-zu, .st-zv, .st-zw, .st-zx, .st-zy, .st-zz {
        background: #23283a !important;
        color: #e0e6f0 !important;
    }
    .stat-card {
        display: inline-block;
        background: #23283a;
        border-radius: 12px;
        padding: 1.2em 2em;
        margin: 0.5em 1em 0.5em 0;
        min-width: 120px;
        text-align: center;
        box-shadow: 0 2px 8px #0002;
    }
    .stat-title {
        font-size: 0.9em;
        color: #a0aec0;
    }
    .stat-value {
        font-size: 1.5em;
        font-weight: bold;
        color: #e0e6f0;
    }
    .stat-pos { color: #4ade80; }
    .stat-neg { color: #f87171; }
    .stat-neutral { color: #facc15; }
    .badge-win { background: #14532d; color: #4ade80; border-radius: 8px; padding: 2px 10px; font-size: 0.9em; }
    .badge-loss { background: #7f1d1d; color: #f87171; border-radius: 8px; padding: 2px 10px; font-size: 0.9em; }
    .badge-wash { background: #78350f; color: #facc15; border-radius: 8px; padding: 2px 10px; font-size: 0.9em; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Custom App Header (Stonk Journal style) ---
st.markdown('''
<style>
.sj-app-header {
    width: 100vw;
    min-width: 100vw;
    background: #181c24;
    color: #fff;
    padding: 0.7em 2.5em 0.7em 2.2em;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 2.1em;
    font-weight: 800;
    letter-spacing: 0.01em;
    box-shadow: 0 2px 8px #0002;
    border-bottom: 1px solid #23283a;
    display: flex;
    align-items: center;
    gap: 1.1em;
    margin-bottom: 0.5em;
    z-index: 1000;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
}
.sj-app-header-logo {
    font-size: 1.5em;
    margin-right: 0.5em;
    color: #4fc3f7;
    font-weight: 900;
    display: flex;
    align-items: center;
}
.sj-app-header-title {
    font-size: 1.1em;
    font-weight: 800;
    letter-spacing: 0.01em;
    color: #fff;
    margin-right: 1.5em;
}
@media (max-width: 600px) {
  .sj-app-header { font-size: 1.2em; padding: 0.7em 1em 0.7em 1em; }
}
</style>
<div class="sj-app-header">
    <span class="sj-app-header-logo">&#128200;</span>
    <span class="sj-app-header-title">TradeLedger</span>
</div>
<br><br><br>
''', unsafe_allow_html=True)

# --- Sidebar Navigation State ---
NAV_ITEMS = [
    {"label": "Dashboard", "icon": "&#128202;"},
    {"label": "Stats", "icon": "&#128200;"},
    {"label": "Calendar", "icon": "&#128197;"},
    {"label": "Settings", "icon": "&#9881;"},
    {"label": "Help", "icon": "&#10067;"},
]
if 'nav_page' not in st.session_state:
    st.session_state['nav_page'] = 'Dashboard'

def set_nav_page(page):
    st.session_state['nav_page'] = page

# --- Custom Sidebar ---
with st.sidebar:
    st.markdown('''
    <style>
    .sj-sidebar {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #e0e6f0;
        padding: 0 0.5em;
    }
    .sj-account {
        margin-bottom: 1.5em;
        padding: 0.5em 0.5em 0.5em 0.5em;
        background: none;
    }
    .sj-account-label {
        font-size: 0.95em;
        color: #bfc9db;
        background: #23283a;
        border-radius: 8px;
        padding: 2px 10px;
        display: inline-block;
        margin-bottom: 0.2em;
    }
    .sj-balance {
        font-size: 2em;
        color: #4fc3f7;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.3em;
    }
    .sj-balance-edit {
        font-size: 1em;
        color: #7dd3fc;
        cursor: pointer;
    }
    .sj-account-details {
        font-size: 0.95em;
        margin-top: -0.5em;
        margin-bottom: 0.5em;
    }
    .sj-account-details span {
        display: block;
        color: #bfc9db;
        font-size: 0.95em;
    }
    .sj-account-details .sj-cash { color: #60a5fa; }
    .sj-account-details .sj-active { color: #4ade80; }
    .sj-nav {
        margin: 1.5em 0 1em 0;
    }
    .sj-nav-item {
        display: flex;
        align-items: center;
        gap: 0.7em;
        font-size: 1.1em;
        padding: 0.5em 0.7em;
        border-radius: 8px;
        margin-bottom: 0.2em;
        cursor: pointer;
        transition: background 0.15s;
    }
    .sj-nav-item:hover {
        background: #23283a;
    }
    .sj-nav-item.sj-nav-active {
        background: #23283a;
        color: #4fc3f7;
        font-weight: 700;
    }
    .sj-nav-icon {
        font-size: 1.2em;
        width: 1.5em;
        text-align: center;
        opacity: 0.85;
    }
    .sj-action-btn {
        display: flex;
        align-items: center;
        gap: 0.7em;
        font-size: 1.1em;
        font-weight: 500;
        border: none;
        border-radius: 16px;
        padding: 0.6em 1.5em;
        margin-bottom: 0.5em;
        width: 100%;
        cursor: pointer;
        transition: background 0.15s;
        justify-content: flex-start;
    }
    .sj-btn-trade { background: #29405a; color: #e0e6f0; }
    .sj-btn-trade:hover { background: #36506e; }
    .sj-btn-setup { background: #4b2e39; color: #e0e6f0; }
    .sj-btn-setup:hover { background: #6b3c4e; }
    .sj-btn-note { background: #7c6842; color: #e0e6f0; }
    .sj-btn-note:hover { background: #a68c5c; }
    .sj-divider { border: none; border-top: 1px solid #2d334a; margin: 1.2em 0; }
    </style>
    <div class="sj-sidebar">
      <div class="sj-account">
        <div class="sj-account-label">Default Account <span style='float:right;opacity:0.7;'>&#9660;</span></div>
        <div class="sj-balance">$788.00 <span class="sj-balance-edit">&#9998;</span></div>
        <div class="sj-account-details">
          <span class="sj-cash">Cash: <span style="color:#60a5fa;">-$1,185.00</span></span>
          <span class="sj-active">Active: <span style="color:#4ade80;">$1,973.00</span></span>
        </div>
      </div>
      <div class="sj-nav">
    ''', unsafe_allow_html=True)
    # Render nav items as buttons (highlight active)
    for item in NAV_ITEMS:
        nav_label = item["label"]
        nav_icon = item["icon"]
        is_active = st.session_state['nav_page'] == nav_label
        btn_html = f'<div class="sj-nav-item{" sj-nav-active" if is_active else ""}" onclick="window.location.hash=\'#{nav_label}\';window.parent.postMessage({{isStreamlitMessage: true, type: \'streamlit:setComponentValue\', key: \'nav_page\', value: \'{nav_label}\'}}, \'*\')">'
        btn_html += f'<span class="sj-nav-icon">{nav_icon}</span> {nav_label}</div>'
        st.markdown(btn_html, unsafe_allow_html=True)
        # Add a hidden Streamlit button for state update
        if st.button(f" ", key=f"navbtn_{nav_label}", help=nav_label):
            set_nav_page(nav_label)
    st.markdown('''
      </div>
      <button class="sj-action-btn sj-btn-trade">&#11036; New Trade</button>
      <button class="sj-action-btn sj-btn-setup">&#128230; New Setup</button>
      <button class="sj-action-btn sj-btn-note">&#128278; New Note</button>
    </div>
    ''', unsafe_allow_html=True)

# --- Main Content Area ---
st.markdown('<div style="height:2.5em;"></div>', unsafe_allow_html=True)  # Spacer for fixed header
page = st.session_state['nav_page']

if page == 'Dashboard':
    # Sidebar account summary and date filter
    with st.sidebar:
        st.markdown("## Default Account")
        trades_df = db.fetch_trades()
        cash = trades_df['pnl'].sum() if not trades_df.empty else 0
        st.markdown(f"**${cash:,.2f}**")
        st.markdown("Cash: <span style='color:#f87171;'>$-1,185.00</span>", unsafe_allow_html=True)
        st.markdown("Active: <span style='color:#4ade80;'>$1,973.00</span>", unsafe_allow_html=True)
        st.markdown("---")
        date_min = trades_df['date'].min() if not trades_df.empty else datetime.now().date() - timedelta(days=30)
        date_max = trades_df['date'].max() if not trades_df.empty else datetime.now().date()
        date_range = st.date_input('Date Range', [date_min, date_max])

    # Filter trades by date
    if not trades_df.empty:
        trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date
        if isinstance(date_range, list) and len(date_range) == 2:
            trades_df = trades_df[(trades_df['date'] >= date_range[0]) & (trades_df['date'] <= date_range[1])]

    st.header('Performance Dashboard')
    if trades_df.empty:
        st.info('No trades to display.')
    else:
        # --- Performance Chart ---
        trades_df_sorted = trades_df.sort_values('date')
        trades_df_sorted['cum_pnl'] = trades_df_sorted['pnl'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trades_df_sorted['date'], y=trades_df_sorted['cum_pnl'], mode='lines+markers', name='PnL', line=dict(color='#4ade80')))
        fig.update_layout(
            plot_bgcolor='#23283a',
            paper_bgcolor='#23283a',
            font_color='#e0e6f0',
            margin=dict(l=0, r=0, t=30, b=0),
            height=220,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)
        # --- Stat Cards ---
        wins = (trades_df['pnl'] > 0).sum()
        losses = (trades_df['pnl'] < 0).sum()
        washes = (trades_df['pnl'] == 0).sum()
        open_trades = 2  # Placeholder, implement logic if you track open trades
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if wins else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losses else 0
        pnl = trades_df['pnl'].sum()
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        col1.metric("Wins", wins)
        col2.metric("Losses", losses)
        col3.metric("Open", open_trades)
        col4.metric("Wash", washes)
        col5.metric("Avg W", f"${avg_win:.0f}")
        col6.metric("Avg L", f"${avg_loss:.0f}")
        col7.metric("PnL", f"${pnl:.2f}")
        # --- Trades Table ---
        st.markdown("#### Trades")
        # Add/rename columns to match UI
        trades_df['Symbol'] = trades_df['ticker']
        trades_df['Status'] = trades_df['pnl'].apply(lambda x: 'WIN' if x > 0 else ('LOSS' if x < 0 else 'WASH'))
        trades_df['Side'] = trades_df['side']
        trades_df['Qty'] = trades_df['quantity']
        trades_df['Entry'] = trades_df['price']
        trades_df['Exit'] = trades_df['price']  # Placeholder, add exit price logic if available
        trades_df['Ent Tot'] = trades_df['price'] * trades_df['quantity']
        trades_df['Ext Tot'] = trades_df['price'] * trades_df['quantity']  # Placeholder
        trades_df['Pos'] = '-'
        trades_df['Hold'] = '-'
        trades_df['Return'] = trades_df['pnl']
        trades_df['Return %'] = trades_df.apply(lambda row: (row['pnl'] / (row['price'] * row['quantity'])) * 100 if row['price'] * row['quantity'] != 0 else 0, axis=1)
        # Custom cell rendering for status and returns
        status_renderer = JsCode('''
        function(params) {
            if (params.value === 'WIN') return `<span style="background:#14532d;color:#4ade80;padding:2px 10px;border-radius:8px;">WIN</span>`;
            if (params.value === 'LOSS') return `<span style="background:#7f1d1d;color:#f87171;padding:2px 10px;border-radius:8px;">LOSS</span>`;
            return `<span style="background:#78350f;color:#facc15;padding:2px 10px;border-radius:8px;">WASH</span>`;
        }
        ''')
        return_renderer = JsCode('''
        function(params) {
            let color = params.value > 0 ? '#4ade80' : (params.value < 0 ? '#f87171' : '#facc15');
            return `<span style="color:${color}">$${params.value.toFixed(2)}</span>`;
        }
        ''')
        return_pct_renderer = JsCode('''
        function(params) {
            let color = params.value > 0 ? '#4ade80' : (params.value < 0 ? '#f87171' : '#facc15');
            return `<span style="color:${color}">${params.value.toFixed(2)}%</span>`;
        }
        ''')
        gb = GridOptionsBuilder.from_dataframe(trades_df)
        gb.configure_column('Status', cellRenderer=status_renderer)
        gb.configure_column('Return', cellRenderer=return_renderer)
        gb.configure_column('Return %', cellRenderer=return_pct_renderer)
        gb.configure_column('Symbol', width=120)
        gb.configure_column('Entry', width=90)
        gb.configure_column('Exit', width=90)
        gb.configure_column('Ent Tot', width=110)
        gb.configure_column('Ext Tot', width=110)
        gb.configure_column('Pos', width=70)
        gb.configure_column('Hold', width=90)
        gb.configure_column('Qty', width=70)
        gb.configure_column('Side', width=80)
        gb.configure_column('date', header_name='Date', width=110)
        gb.configure_column('notes', header_name='Notes', width=120)
        gb.configure_column('tags', header_name='Tags', width=120)
        gb.configure_grid_options(domLayout='normal')
        grid_options = gb.build()
        AgGrid(
            trades_df[[
                'date', 'Symbol', 'Status', 'Side', 'Qty', 'Entry', 'Exit', 'Ent Tot', 'Ext Tot', 'Pos', 'Hold', 'Return', 'Return %', 'notes', 'tags'
            ]],
            gridOptions=grid_options,
            allow_unsafe_jscode=True,
            theme='alpine',
            fit_columns_on_grid_load=True,
            height=400
        )

elif page == 'Stats':
    st.header('Stats')
    st.info('Stats page coming soon.')
elif page == 'Calendar':
    st.header('Calendar')
    st.info('Calendar page coming soon.')
elif page == 'Settings':
    st.header('Settings')
    st.info('Settings page coming soon.')
elif page == 'Help':
    st.header('Help')
    st.info('Help page coming soon.')
