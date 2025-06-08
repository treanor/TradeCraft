<template>
  <div class="dashboard dark-theme">
    <aside class="sidebar">
      <div class="logo">🦾 <span>Stonk Journal</span></div>
      <div class="account-section">
        <div class="account-label">Default Account</div>
        <div class="account-balance">$788.00</div>
        <div class="account-cash">Cash: <span class="neg">-$1,185.00</span></div>
        <div class="account-active">Active: <span class="pos">$1,973.00</span></div>
      </div>
      <nav class="sidebar-nav">
        <RouterLink to="/">🏠 Dashboard</RouterLink>
        <RouterLink to="/stats">📊 Stats</RouterLink>
        <a class="disabled">📅 Calendar</a>
        <a class="disabled">⚙️ Settings</a>
        <a class="disabled">❓ Help</a>
      </nav>
      <div class="sidebar-actions">
        <button class="btn btn-blue"><span class="icon">＋</span> New Trade</button>
        <button class="btn btn-red"><span class="icon">★</span> New Setup</button>
        <button class="btn btn-yellow"><span class="icon">📝</span> New Note</button>
      </div>
      <div class="sidebar-footer">
        <small>Support this free platform with a <span>☕</span> donation or membership.</small>
      </div>
    </aside>
    <main class="dashboard-main">
      <div class="dashboard-header">
        <FilterButtons v-model="selectedFilter" :options="FILTER_OPTIONS" />
        <div class="dashboard-metrics">
          <div class="metric-card wins"><span class="metric-label">WINS</span><span class="metric-value">{{ wins }}</span></div>
          <div class="metric-card losses"><span class="metric-label">LOSSES</span><span class="metric-value">{{ losses }}</span></div>
          <div class="metric-card open"><span class="metric-label">OPEN</span><span class="metric-value">{{ open }}</span></div>
          <div class="metric-card wash"><span class="metric-label">WASH</span><span class="metric-value">{{ wash }}</span></div>
          <div class="metric-card avgw"><span class="metric-label">AVG W</span><span class="metric-value">{{ avgW }}</span></div>
          <div class="metric-card avgl"><span class="metric-label">AVG L</span><span class="metric-value">{{ avgL }}</span></div>
          <div class="metric-card pnl"><span class="metric-label">PnL</span><span class="metric-value">{{ pnl }}</span></div>
        </div>
      </div>
      <div class="dashboard-chart-block chart-shadow">
        <Line
          v-if="equityCurve.data.length > 0"
          :data="{ labels: equityCurve.labels, datasets: [{ data: equityCurve.data, label: 'PnL', fill: true, borderColor: '#4fc3f7', backgroundColor: 'rgba(79,195,247,0.08)' }] }"
          :options="chartOptions"
          style="height:220px; width:100%;"
        />
        <div v-else class="chart-empty">No trades to display.</div>
      </div>
      <div class="dashboard-table-container">
        <table class="dashboard-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Symbol</th>
              <th>Status</th>
              <th>Side</th>
              <th>Qty</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>Ent Tot</th>
              <th>Ext Tot</th>
              <th>Pos</th>
              <th>Hold</th>
              <th>Return</th>
              <th>Return %</th>
              <th>Tags</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in trades" :key="trade.trade_id">
              <td>{{ formatDate(trade.created_at) }}</td>
              <td class="symbol">{{ trade.symbol }}</td>
              <td>
                <span :class="['status-badge', trade.status.toLowerCase()]">
                  {{ trade.status }}
                </span>
              </td>
              <td>{{ getSide(trade) }}</td>
              <td>{{ getQty(trade) }}</td>
              <td>{{ getEntry(trade) }}</td>
              <td>{{ getExit(trade) }}</td>
              <td>{{ getEntTot(trade) }}</td>
              <td>{{ getExtTot(trade) }}</td>
              <td>-</td>
              <td>{{ getHold(trade) }}</td>
              <td :class="returnColorClass(trade)">{{ getReturn(trade) }}</td>
              <td :class="returnColorClass(trade)">{{ getReturnPct(trade) }}</td>
              <td>{{ trade.tags.join(', ') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { sampleTrades } from '../data/sampleTrades';
import { computed, ref } from 'vue';
import FilterButtons from './FilterButtons.vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler);

const FILTER_OPTIONS = [
  { label: 'All', value: 'all' },
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'This wk.', value: 'this_week' },
  { label: 'Last wk.', value: 'last_week' },
  { label: 'This mo.', value: 'this_month' },
  { label: 'Last mo.', value: 'last_month' },
];

const selectedFilter = ref('all');

function filterTrades(trades, filter) {
  const now = new Date();
  switch (filter) {
    case 'today': {
      return trades.filter(t => {
        const d = new Date(t.created_at);
        return d.toDateString() === now.toDateString();
      });
    }
    case 'yesterday': {
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);
      return trades.filter(t => {
        const d = new Date(t.created_at);
        return d.toDateString() === yesterday.toDateString();
      });
    }
    case 'this_week': {
      const start = new Date(now);
      start.setDate(now.getDate() - now.getDay());
      start.setHours(0,0,0,0);
      const end = new Date(start);
      end.setDate(start.getDate() + 7);
      return trades.filter(t => {
        const d = new Date(t.created_at);
        return d >= start && d < end;
      });
    }
    case 'last_week': {
      const start = new Date(now);
      start.setDate(now.getDate() - now.getDay() - 7);
      start.setHours(0,0,0,0);
      const end = new Date(start);
      end.setDate(start.getDate() + 7);
      return trades.filter(t => {
        const d = new Date(t.created_at);
        return d >= start && d < end;
      });
    }
    case 'this_month': {
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 1);
      return trades.filter(t => {
        const d = new Date(t.created_at);
        return d >= start && d < end;
      });
    }
    case 'last_month': {
      const start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const end = new Date(now.getFullYear(), now.getMonth(), 1);
      return trades.filter(t => {
        const d = new Date(t.created_at);
        return d >= start && d < end;
      });
    }
    case 'all':
    default:
      return trades;
  }
}

const trades = computed(() => filterTrades(sampleTrades, selectedFilter.value));

const wins = computed(() => trades.value.filter(t => t.status === 'WIN').length);
const losses = computed(() => trades.value.filter(t => t.status === 'LOSS').length);
const open = computed(() => trades.value.filter(t => t.status === 'OPEN').length);
const wash = computed(() => trades.value.filter(t => t.status === 'WASH').length);
const avgW = computed(() => {
  const winTrades = trades.value.filter(t => t.status === 'WIN' && t.legs.length > 1);
  if (!winTrades.length) return '-';
  const total = winTrades.reduce((sum, t) => {
    const entry = t.legs[0];
    const exit = t.legs[1];
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    return sum + (extTot - entTot);
  }, 0);
  return `$${(total / winTrades.length).toFixed(0)}`;
});
const avgL = computed(() => {
  const lossTrades = trades.value.filter(t => t.status === 'LOSS' && t.legs.length > 1);
  if (!lossTrades.length) return '-';
  const total = lossTrades.reduce((sum, t) => {
    const entry = t.legs[0];
    const exit = t.legs[1];
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    return sum + (extTot - entTot);
  }, 0);
  return `$${(total / lossTrades.length).toFixed(0)}`;
});
const pnl = computed(() => {
  let total = 0;
  trades.value.forEach(t => {
    if (t.legs.length > 1) {
      const entry = t.legs[0];
      const exit = t.legs[1];
      const entTot = entry.quantity * entry.price + (entry.fee || 0);
      const extTot = exit.quantity * exit.price - (exit.fee || 0);
      total += (extTot - entTot);
    }
  });
  return `$${total.toFixed(2)}`;
});

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString();
}
function getSide(trade) {
  const entry = trade.legs[0];
  return entry ? entry.action.charAt(0).toUpperCase() + entry.action.slice(1) : '-';
}
function getQty(trade) {
  const entry = trade.legs[0];
  return entry ? entry.quantity : 0;
}
function getEntry(trade) {
  const entry = trade.legs[0];
  return entry ? `$${entry.price.toFixed(2)}` : '-';
}
function getExit(trade) {
  const exit = trade.legs[1];
  return exit ? `$${exit.price.toFixed(2)}` : '-';
}
function getEntTot(trade) {
  const entry = trade.legs[0];
  return entry ? `$${(entry.quantity * entry.price + (entry.fee || 0)).toFixed(2)}` : '-';
}
function getExtTot(trade) {
  const exit = trade.legs[1];
  return exit ? `$${(exit.quantity * exit.price - (exit.fee || 0)).toFixed(2)}` : '-';
}
function getReturn(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    return `$${(extTot - entTot).toFixed(2)}`;
  }
  return '-';
}
function getReturnPct(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    if (entTot !== 0) {
      return `${(((extTot - entTot) / entTot) * 100).toFixed(2)}%`;
    }
  }
  return '-';
}
function getHold(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const ms = new Date(exit.datetime) - new Date(entry.datetime);
    const mins = Math.floor(ms / 60000);
    if (mins < 1) return '<1 MIN';
    if (mins < 60) return `${mins} MIN`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} HR${hours !== 1 ? 'S' : ''}`;
    const days = Math.floor(hours / 24);
    return `${days} DAY${days !== 1 ? 'S' : ''}`;
  }
  return '-';
}
function returnColorClass(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    if (extTot - entTot > 0) return 'pos';
    if (extTot - entTot < 0) return 'neg';
  }
  return '';
}

// PnL chart data based on filtered trades
function getEquityCurve(trades) {
  // Sort trades by date ascending
  const sorted = [...trades].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  let equity = 0;
  const labels = [];
  const data = [];
  for (const t of sorted) {
    if (t.legs.length > 1) {
      const entry = t.legs[0];
      const exit = t.legs[1];
      const entTot = entry.quantity * entry.price + (entry.fee || 0);
      const extTot = exit.quantity * exit.price - (exit.fee || 0);
      equity += extTot - entTot;
      labels.push(new Date(t.created_at).toLocaleDateString());
      data.push(equity);
    }
  }
  return { labels, data };
}
const equityCurve = computed(() => getEquityCurve(trades.value));
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: false }
  },
  elements: {
    line: { borderColor: '#4fc3f7', borderWidth: 3, fill: 'start', backgroundColor: 'rgba(79,195,247,0.08)' },
    point: { radius: 0 }
  },
  scales: {
    x: {
      ticks: { color: '#b0bec5', font: { size: 12 } },
      grid: { color: '#232b3b' }
    },
    y: {
      ticks: { color: '#b0bec5', font: { size: 12 } },
      grid: { color: '#232b3b' }
    }
  }
};
const equityCurveData = computed(() => {
  return {
    labels: equityCurve.value.labels,
    datasets: [
      {
        label: 'Equity Curve',
        data: equityCurve.value.data,
        borderColor: '#4fc3f7',
        backgroundColor: 'rgba(79,195,247,0.08)',
        borderWidth: 3,
        fill: 'start',
        tension: 0.4
      }
    ]
  };
});
</script>

<style scoped>
.dashboard.dark-theme {
  min-height: 100vh;
  background: #11141b;
  color: #e6eaf3;
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 210px;
  background: #181f2a;
  padding: 1.5rem 0.7rem 1rem 0.7rem;
  border-right: 1px solid #232b3b;
  box-shadow: 2px 0 16px 0 rgba(0,0,0,0.10);
}
.logo {
  font-size: 1.7rem;
  font-weight: 900;
  color: #fff;
  margin-bottom: 2rem;
  letter-spacing: 1.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
  width: 100%;
}
.logo span { font-weight: 800; letter-spacing: 2px; }
.account-section {
  margin-bottom: 1.2rem;
  width: 100%;
}
.account-label {
  color: #a3adc2;
  font-size: 0.93rem;
  margin-bottom: 0.15rem;
}
.account-balance {
  color: #4be37a;
  font-size: 1.25rem;
  font-weight: 700;
}
.account-cash, .account-active {
  font-size: 0.93rem;
  margin-top: 0.1rem;
}
.account-cash .neg { color: #ff5c5c; }
.account-active .pos { color: #4be37a; }
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
  margin-bottom: 1.2rem;
}
.sidebar-nav a, .sidebar-nav .router-link-active {
  color: #a3adc2;
  text-decoration: none;
  font-size: 1.05rem;
  padding: 0.45rem 0.7rem;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.sidebar-nav .router-link-active, .sidebar-nav a:hover {
  background: #232b3b;
  color: #fff;
}
.sidebar-nav .disabled {
  opacity: 0.5;
  pointer-events: none;
}
.sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.2rem;
  align-items: center;
  width: 100%;
}
.btn {
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  padding: 0.6rem 0;
  cursor: pointer;
  transition: background 0.2s;
  width: 160px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.07);
}
.btn-blue { background: #2b6cb0; color: #fff; }
.btn-blue:hover { background: #3182ce; }
.btn-red { background: #c53030; color: #fff; }
.btn-red:hover { background: #e53e3e; }
.btn-yellow { background: #ecc94b; color: #181f2a; }
.btn-yellow:hover { background: #faf089; }
.btn .icon { font-size: 1.1em; }
.sidebar-footer {
  margin-top: auto;
  color: #a3adc2;
  font-size: 0.9rem;
  text-align: center;
  width: 100%;
}
.dashboard-main {
  position: fixed;
  top: 0;
  left: 210px;
  right: 0;
  bottom: 0;
  width: auto;
  min-width: 0;
  padding: 0 2vw 2vw 2vw;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #181f2a;
  box-sizing: border-box;
  overflow-x: auto;
}
.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  margin-bottom: 1.5rem;
  margin-top: 1.2rem;
}
.dashboard-metrics {
  display: flex;
  gap: 1.1rem;
  flex-wrap: wrap;
  background: transparent;
  border-radius: 12px;
  padding: 0;
  align-items: center;
  box-shadow: none;
}
.metric-card {
  background: #232b3b;
  border-radius: 14px;
  padding: 0.8rem 1.3rem 0.7rem 1.3rem;
  min-width: 90px;
  min-height: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
  margin-bottom: 0.2rem;
  border: 2px solid transparent;
  transition: border 0.2s;
}
.metric-card.wins { background: #1e2e1e; border-color: #4be37a33; }
.metric-card.losses { background: #2e1e1e; border-color: #ff5c5c33; }
.metric-card.open { background: #1e2e2e; border-color: #4be37a33; }
.metric-card.wash { background: #2e2e1e; border-color: #ffe06633; }
.metric-card.avgw { background: #1e2e1e; border-color: #4be37a33; }
.metric-card.avgl { background: #2e1e1e; border-color: #ff5c5c33; }
.metric-card.pnl { background: #1e2e1e; border-color: #4be37a33; }
.metric-label {
  color: #a3adc2;
  font-size: 0.93rem;
  font-weight: 600;
  margin-bottom: 0.1rem;
  letter-spacing: 0.5px;
}
.metric-value {
  font-size: 1.7rem;
  font-weight: 900;
  margin-top: 0.1rem;
  color: #fff;
  letter-spacing: 1px;
}
.metric-card.wins .metric-value, .metric-card.open .metric-value, .metric-card.avgw .metric-value, .metric-card.pnl .metric-value { color: #4be37a; }
.metric-card.losses .metric-value, .metric-card.avgl .metric-value { color: #ff5c5c; }
.metric-card.wash .metric-value { color: #ffe066; }
.dashboard-chart-block {
  background: #232b3b;
  border-radius: 18px;
  margin: 1.2rem 0 1.7rem 0;
  padding: 1.2rem 1.5rem 1.5rem 1.5rem;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.13);
  min-height: 220px;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}
.chart-shadow {
  box-shadow: 0 8px 32px 0 rgba(79,195,247,0.08), 0 2px 8px 0 rgba(0,0,0,0.10);
}
.chart-empty {
  color: #b0bec5;
  text-align: center;
  font-size: 1.1rem;
  padding: 2rem 0;
}
.dashboard-table-container {
  background: #232b3b;
  border-radius: 18px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.12);
  margin: 0;
  padding: 0.7rem 0.5vw 0.5rem 0.5vw;
  width: 100%;
  box-sizing: border-box;
}
.dashboard-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.97rem;
  background: #232b3b;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
}
.dashboard-table th, .dashboard-table td {
  padding: 0.45rem 0.5rem;
  text-align: center;
}
.dashboard-table th {
  background: #232b3b;
  color: #a3adc2;
  font-weight: 800;
  border-bottom: 2px solid #2e3950;
  font-size: 0.97rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.dashboard-table tbody tr {
  transition: background 0.2s;
}
.dashboard-table tbody tr:hover {
  background: #20283a;
}
.symbol {
  color: #6cb4ff;
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
  text-decoration: underline;
}
.status-badge {
  display: inline-block;
  min-width: 60px;
  padding: 0.22em 0.7em;
  border-radius: 10px;
  font-size: 0.97em;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border: 1.5px solid transparent;
}
.status-badge.win {
  background: #1e2e1e;
  color: #4be37a;
  border-color: #4be37a;
}
.status-badge.loss {
  background: #2e1e1e;
  color: #ff5c5c;
  border-color: #ff5c5c;
}
.status-badge.open {
  background: #232b3b;
  color: #e6eaf3;
  border-color: #a3adc2;
}
.status-badge.wash {
  background: #2e2e1e;
  color: #ffe066;
  border-color: #ffe066;
}
.pos {
  color: #4be37a;
  font-weight: 700;
}
.neg {
  color: #ff5c5c;
  font-weight: 700;
}
@media (max-width: 900px) {
  .dashboard-main { padding: 0 0.5vw 2vw 0.5vw; }
  .sidebar { width: 54px; padding: 1rem 0.2rem; }
  .logo, .account-section, .sidebar-footer, .sidebar-actions, .sidebar-nav a span { display: none !important; }
  .sidebar-nav a, .sidebar-nav .router-link-active { font-size: 1.2rem; justify-content: center; padding: 0.7rem 0; }
  .dashboard-metrics { flex-wrap: wrap; gap: 0.7rem; padding: 0.5rem 0.5rem; }
  .metric-card { min-width: 70px; min-height: 50px; padding: 0.5rem 0.7rem; }
}
</style>
