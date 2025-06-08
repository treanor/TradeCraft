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
    <main class="stats-main">
      <div class="stats-header">
        <FilterButtons v-model="selectedFilter" :options="FILTER_OPTIONS" />
        <div class="stats-cards-grid">
          <div class="stat-card" v-for="card in statCards" :key="card.label">
            <div class="stat-label">{{ card.label }}</div>
            <div class="stat-value" :class="card.class">{{ card.value }}</div>
          </div>
        </div>
      </div>
      <div class="stats-charts-row">
        <div class="stats-chart-card">
          <Line :data="equityCurveData" :options="equityChartOptions" style="height:220px; width:100%;" />
        </div>
      </div>
      <div class="stats-bar-charts-row">
        <div class="stats-bar-card">
          <div class="bar-title">Performance by Day of Week</div>
          <Bar :data="dayOfWeekBarData" :options="dayOfWeekBarChartOptions" style="height:180px; width:100%;" />
        </div>
        <div class="stats-bar-card">
          <div class="bar-title">Performance by Hour</div>
          <Bar :data="hourBarData" :options="hourBarChartOptions" style="height:180px; width:100%;" />
        </div>
      </div>
      <div class="stats-tables-row">
        <div class="stats-table-card">
          <div class="table-title">Tag</div>
          <table class="stats-table">
            <thead>
              <tr><th>Tag</th><th>Trades</th><th>PnL</th><th>PnL %</th><th>Weighted %</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in tagTable" :key="row.tag">
                <td>{{ row.tag }}</td>
                <td>{{ row.trades }}</td>
                <td :class="row.pnlClass">{{ row.pnl }}</td>
                <td>{{ row.pnlPct }}</td>
                <td>{{ row.weightedPct }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="stats-table-card">
          <div class="table-title">Symbol</div>
          <table class="stats-table">
            <thead>
              <tr><th>Symbol</th><th>Trades</th><th>PnL</th><th>PnL %</th><th>Weighted %</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in symbolTable" :key="row.symbol">
                <td>{{ row.symbol }}</td>
                <td>{{ row.trades }}</td>
                <td :class="row.pnlClass">{{ row.pnl }}</td>
                <td>{{ row.pnlPct }}</td>
                <td>{{ row.weightedPct }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import FilterButtons from './FilterButtons.vue';
import { sampleTrades } from '../data/sampleTrades';
import { Line, Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
} from 'chart.js';
ChartJS.register(Title, Tooltip, Legend, LineElement, BarElement, PointElement, CategoryScale, LinearScale, Filler);

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

// --- Stat Cards ---
const statCards = computed(() => [
  { label: 'WIN RATE', value: winRate.value, class: '' },
  { label: 'EXPECTANCY', value: expectancy.value, class: '' },
  { label: 'PROFIT FACTOR', value: profitFactor.value, class: '' },
  { label: 'AVG WIN HOLD', value: avgWinHold.value, class: '' },
  { label: 'AVG LOSS HOLD', value: avgLossHold.value, class: '' },
  { label: 'AVG LOSS', value: avgLoss.value, class: 'neg' },
  { label: 'AVG WIN', value: avgWin.value, class: 'pos' },
  { label: 'WIN STREAK', value: winStreak.value, class: '' },
  { label: 'LOSS STREAK', value: lossStreak.value, class: '' },
  { label: 'TOP LOSS', value: topLoss.value, class: 'neg' },
  { label: 'TOP WIN', value: topWin.value, class: 'pos' },
  { label: 'AVG DAILY VOL', value: avgDailyVol.value, class: '' },
  { label: 'AVG SIZE', value: avgSize.value, class: '' },
]);
// --- Stat Card Calculations ---
const winRate = computed(() => {
  const closed = trades.value.filter(t => t.status === 'WIN' || t.status === 'LOSS');
  if (!closed.length) return '-';
  const wins = closed.filter(t => t.status === 'WIN').length;
  return `${Math.round((wins / closed.length) * 100)}%`;
});
const expectancy = computed(() => {
  const closed = trades.value.filter(t => t.status === 'WIN' || t.status === 'LOSS');
  if (!closed.length) return '-';
  const avgWin = closed.filter(t => t.status === 'WIN').reduce((sum, t) => sum + getPnl(t), 0) / (closed.filter(t => t.status === 'WIN').length || 1);
  const avgLoss = closed.filter(t => t.status === 'LOSS').reduce((sum, t) => sum + getPnl(t), 0) / (closed.filter(t => t.status === 'LOSS').length || 1);
  const winRateNum = closed.filter(t => t.status === 'WIN').length / closed.length;
  const lossRateNum = closed.filter(t => t.status === 'LOSS').length / closed.length;
  return (avgWin * winRateNum + avgLoss * lossRateNum).toFixed(2);
});
const profitFactor = computed(() => {
  const wins = trades.value.filter(t => t.status === 'WIN');
  const losses = trades.value.filter(t => t.status === 'LOSS');
  const winSum = wins.reduce((sum, t) => sum + getPnl(t), 0);
  const lossSum = losses.reduce((sum, t) => sum + Math.abs(getPnl(t)), 0);
  if (lossSum === 0) return '-';
  return (winSum / lossSum).toFixed(2);
});
const avgWinHold = computed(() => {
  const wins = trades.value.filter(t => t.status === 'WIN' && t.legs.length > 1);
  if (!wins.length) return '-';
  const mins = wins.reduce((sum, t) => sum + getHoldMins(t), 0) / wins.length;
  return minsToDuration(mins);
});
const avgLossHold = computed(() => {
  const losses = trades.value.filter(t => t.status === 'LOSS' && t.legs.length > 1);
  if (!losses.length) return '-';
  const mins = losses.reduce((sum, t) => sum + getHoldMins(t), 0) / losses.length;
  return minsToDuration(mins);
});
const avgWin = computed(() => {
  const wins = trades.value.filter(t => t.status === 'WIN');
  if (!wins.length) return '-';
  const avg = wins.reduce((sum, t) => sum + getPnl(t), 0) / wins.length;
  return `$${avg.toFixed(2)}`;
});
const avgLoss = computed(() => {
  const losses = trades.value.filter(t => t.status === 'LOSS');
  if (!losses.length) return '-';
  const avg = losses.reduce((sum, t) => sum + getPnl(t), 0) / losses.length;
  return `$${avg.toFixed(2)}`;
});
const winStreak = computed(() => getStreak(trades.value, 'WIN'));
const lossStreak = computed(() => getStreak(trades.value, 'LOSS'));
const topLoss = computed(() => {
  const losses = trades.value.filter(t => t.status === 'LOSS');
  if (!losses.length) return '-';
  const min = Math.min(...losses.map(getPnl));
  const pct = Math.min(...losses.map(getPnlPct));
  return `$${min.toFixed(2)} (${pct.toFixed(2)}%)`;
});
const topWin = computed(() => {
  const wins = trades.value.filter(t => t.status === 'WIN');
  if (!wins.length) return '-';
  const max = Math.max(...wins.map(getPnl));
  const pct = Math.max(...wins.map(getPnlPct));
  return `$${max.toFixed(2)} (${pct.toFixed(2)}%)`;
});
const avgDailyVol = computed(() => {
  if (!trades.value.length) return '-';
  const days = new Set(trades.value.map(t => new Date(t.created_at).toDateString())).size;
  return Math.round(trades.value.length / days);
});
const avgSize = computed(() => {
  if (!trades.value.length) return '-';
  const total = trades.value.reduce((sum, t) => sum + (t.legs[0]?.quantity || 0), 0);
  return Math.round(total / trades.value.length);
});
// --- Helpers ---
function getPnl(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    return extTot - entTot;
  }
  return 0;
}
function getPnlPct(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const entTot = entry.quantity * entry.price + (entry.fee || 0);
    const extTot = exit.quantity * exit.price - (exit.fee || 0);
    if (entTot !== 0) {
      return ((extTot - entTot) / entTot) * 100;
    }
  }
  return 0;
}
function getHoldMins(trade) {
  const entry = trade.legs[0];
  const exit = trade.legs[1];
  if (entry && exit) {
    const ms = new Date(exit.datetime) - new Date(entry.datetime);
    return Math.floor(ms / 60000);
  }
  return 0;
}
function minsToDuration(mins) {
  if (mins < 1) return '<1 MIN';
  if (mins < 60) return `${Math.round(mins)} MIN`;
  const hours = mins / 60;
  if (hours < 24) return `${hours.toFixed(1)} Hrs`;
  const days = hours / 24;
  return `${days.toFixed(1)} Days`;
}
function getStreak(trades, status) {
  let max = 0, cur = 0;
  for (const t of trades) {
    if (t.status === status) {
      cur++;
      if (cur > max) max = cur;
    } else {
      cur = 0;
    }
  }
  return max;
}
// --- Equity Curve Chart ---
function getEquityCurve(trades) {
  const sorted = [...trades].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
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
const equityCurveData = computed(() => ({
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
}));
const equityChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, title: { display: false } },
  elements: { line: { borderColor: '#4fc3f7', borderWidth: 3, fill: 'start', backgroundColor: 'rgba(79,195,247,0.08)' }, point: { radius: 0 } },
  scales: {
    x: { ticks: { color: '#b0bec5', font: { size: 12 } }, grid: { color: '#232b3b' } },
    y: { ticks: { color: '#b0bec5', font: { size: 12 } }, grid: { color: '#232b3b' } }
  }
};
// --- Bar Charts ---
// Use refs to store chart data for stability
import { ref as vueRef, watch } from 'vue';
const dayOfWeekBarData = vueRef({ labels: [], datasets: [] });
const hourBarData = vueRef({ labels: [], datasets: [] });

function updateDayOfWeekBarData() {
  const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const pnlByDay = Array(7).fill(0);
  trades.value.forEach(t => {
    const d = new Date(t.created_at).getDay();
    pnlByDay[d] += getPnl(t);
  });
  // Find min/max for symmetric axis
  const min = Math.min(0, ...pnlByDay);
  const max = Math.max(0, ...pnlByDay);
  dayOfWeekBarData.value = {
    labels: days,
    datasets: [{
      label: 'PnL',
      data: pnlByDay,
      backgroundColor: pnlByDay.map(v => v >= 0 ? '#4be37a' : '#ff5c5c'),
      borderRadius: 10,
      barThickness: 22,
      categoryPercentage: 0.7,
      minBarLength: 4
    }],
    min,
    max
  };
}
function updateHourBarData() {
  const hourLabels = [
    '8 AM','9 AM','10 AM','11 AM','12 PM','1 PM','2 PM','3 PM','4 PM','5 PM','6 PM','7 PM'
  ];
  const hours = Array(12).fill(0);
  trades.value.forEach(t => {
    const d = new Date(t.created_at).getHours();
    const idx = Math.max(0, Math.min(11, d - 8));
    if (idx >= 0 && idx < 12) hours[idx] += getPnl(t);
  });
  const min = Math.min(0, ...hours);
  const max = Math.max(0, ...hours);
  hourBarData.value = {
    labels: hourLabels,
    datasets: [{
      label: 'PnL',
      data: hours,
      backgroundColor: hours.map(v => v >= 0 ? '#4be37a' : '#ff5c5c'),
      borderRadius: 10,
      barThickness: 22,
      categoryPercentage: 0.7,
      minBarLength: 4
    }],
    min,
    max
  };
}
watch(trades, () => {
  updateDayOfWeekBarData();
  updateHourBarData();
}, { immediate: true });

const dayOfWeekBarChartOptions = computed(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: false },
    tooltip: {
      backgroundColor: '#232b3b',
      titleColor: '#e6eaf3',
      bodyColor: '#e6eaf3',
      borderColor: '#4fc3f7',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      grid: {
        color: '#232b3b',
        borderColor: '#232b3b',
        drawTicks: false,
        zeroLineColor: '#b0bec5',
        zeroLineWidth: 2
      },
      ticks: {
        color: '#b0bec5',
        font: { size: 13 },
        callback: function(value) { return value === 0 ? '0' : value; }
      },
      beginAtZero: true
    },
    y: {
      grid: {
        color: '#232b3b',
        borderColor: '#232b3b',
        drawTicks: false
      },
      ticks: {
        color: '#b0bec5',
        font: { size: 13 }
      }
    }
  }
}));
const hourBarChartOptions = computed(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: false },
    tooltip: {
      backgroundColor: '#232b3b',
      titleColor: '#e6eaf3',
      bodyColor: '#e6eaf3',
      borderColor: '#4fc3f7',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      grid: {
        color: '#232b3b',
        borderColor: '#232b3b',
        drawTicks: false,
        zeroLineColor: '#b0bec5',
        zeroLineWidth: 2
      },
      ticks: {
        color: '#b0bec5',
        font: { size: 13 },
        callback: function(value) { return value === 0 ? '0' : value; }
      },
      beginAtZero: true
    },
    y: {
      grid: {
        color: '#232b3b',
        borderColor: '#232b3b',
        drawTicks: false
      },
      ticks: {
        color: '#b0bec5',
        font: { size: 13 }
      }
    }
  }
}));
// --- Tables ---
const tagTable = computed(() => {
  const tagMap = {};
  trades.value.forEach(t => {
    (t.tags.length ? t.tags : ['--NO TAGS--']).forEach(tag => {
      if (!tagMap[tag]) tagMap[tag] = { tag, trades: 0, pnl: 0, pnlPct: 0 };
      tagMap[tag].trades++;
      tagMap[tag].pnl += getPnl(t);
      tagMap[tag].pnlPct += getPnlPct(t);
    });
  });
  const totalTrades = trades.value.length || 1;
  return Object.values(tagMap).map(row => ({
    ...row,
    pnl: `$${row.pnl.toFixed(2)}`,
    pnlClass: row.pnl >= 0 ? 'pos' : 'neg',
    pnlPct: `${(row.pnlPct / row.trades).toFixed(2)}%`,
    weightedPct: `${((row.trades / totalTrades) * 100).toFixed(2)}%`
  }));
});
const symbolTable = computed(() => {
  const symMap = {};
  trades.value.forEach(t => {
    const sym = t.symbol;
    if (!symMap[sym]) symMap[sym] = { symbol: sym, trades: 0, pnl: 0, pnlPct: 0 };
    symMap[sym].trades++;
    symMap[sym].pnl += getPnl(t);
    symMap[sym].pnlPct += getPnlPct(t);
  });
  const totalTrades = trades.value.length || 1;
  return Object.values(symMap).map(row => ({
    ...row,
    pnl: `$${row.pnl.toFixed(2)}`,
    pnlClass: row.pnl >= 0 ? 'pos' : 'neg',
    pnlPct: `${(row.pnlPct / row.trades).toFixed(2)}%`,
    weightedPct: `${((row.trades / totalTrades) * 100).toFixed(2)}%`
  }));
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
.stats-main {
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
.stats.dark-theme {
  min-height: 100vh;
  background: #11141b;
  color: #e6eaf3;
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
  padding: 0 2vw 2vw 230px;
}
.stats-header {
  margin-top: 1.2rem;
  margin-bottom: 1.5rem;
}
.stats-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 1.1rem;
  margin-top: 1.2rem;
  margin-bottom: 1.2rem;
}
.stat-card {
  background: #232b3b;
  border-radius: 14px;
  padding: 1.1rem 1.3rem 1.1rem 1.3rem;
  min-height: 70px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
  border: 2px solid transparent;
  transition: border 0.2s;
}
.stat-label {
  color: #a3adc2;
  font-size: 0.93rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
  letter-spacing: 0.5px;
}
.stat-value {
  font-size: 1.7rem;
  font-weight: 900;
  color: #fff;
  letter-spacing: 1px;
}
.stat-value.pos { color: #4be37a; }
.stat-value.neg { color: #ff5c5c; }
.stats-charts-row {
  margin-bottom: 1.5rem;
}
.stats-chart-card {
  background: #232b3b;
  border-radius: 18px;
  padding: 1.2rem 1.5rem 1.5rem 1.5rem;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.13);
  min-height: 220px;
  width: 100%;
  margin-bottom: 0.7rem;
}
.stats-bar-charts-row {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 1.5rem;
}
.stats-bar-card {
  background: #232b3b;
  border-radius: 18px;
  padding: 1.2rem 1.5rem 1.5rem 1.5rem;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.13);
  min-width: 0;
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.bar-title {
  color: #a3adc2;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.7rem;
  letter-spacing: 0.5px;
}
.stats-tables-row {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 1.5rem;
}
.stats-table-card {
  background: #232b3b;
  border-radius: 18px;
  padding: 1.2rem 1.5rem 1.5rem 1.5rem;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.13);
  min-width: 0;
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.table-title {
  color: #a3adc2;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.7rem;
  letter-spacing: 0.5px;
}
.stats-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.97rem;
  background: #232b3b;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);
}
.stats-table th, .stats-table td {
  padding: 0.45rem 0.5rem;
  text-align: center;
}
.stats-table th {
  background: #232b3b;
  color: #a3adc2;
  font-weight: 800;
  border-bottom: 2px solid #2e3950;
  font-size: 0.97rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.stats-table tbody tr {
  transition: background 0.2s;
}
.stats-table tbody tr:hover {
  background: #20283a;
}
.pos {
  color: #4be37a;
  font-weight: 700;
}
.neg {
  color: #ff5c5c;
  font-weight: 700;
}
@media (max-width: 1200px) {
  .stats-cards-grid { grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); }
  .stats-bar-charts-row, .stats-tables-row { flex-direction: column; gap: 0.7rem; }
}
</style>
