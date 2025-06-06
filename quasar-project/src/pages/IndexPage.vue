<template>
  <div class="dashboard-root row no-wrap" style="height:100vh; background:#181e29; color:white;">
    <!-- Sidebar -->
    <aside class="dashboard-sidebar bg-blue-grey-10 text-white" style="width:260px; border-right:2px solid #222b36; display:flex; flex-direction:column; justify-content:space-between;">
      <div class="q-pa-md">
        <q-select label="Default Account" filled dense :options="[ 'Default Account' ]" v-model="account" class="q-mb-md" color="cyan-3" />
        <div class="text-h5 text-cyan-3 q-mb-xs">$788.00 <q-icon name="trending_up" color="cyan-3" size="18px" class="q-ml-xs" /></div>
        <div class="text-caption">Cash: <span class="text-red-4">$-1,185.00</span></div>
        <div class="text-caption q-mb-md">Active: <span class="text-cyan-3">$1,973.00</span></div>
        <q-btn label="New Trade" color="primary" class="full-width q-mb-sm" icon="add" :unelevated="true" rounded @click="showSnackbar('New Trade clicked!')" style="font-weight:600; font-size:16px;" />
        <q-btn label="New Note" color="amber-7" text-color="black" class="full-width q-mb-md" icon="note" :unelevated="true" rounded @click="showSnackbar('New Note clicked!')" style="font-weight:600; font-size:16px;" />
        <q-separator class="q-my-md" />
        <q-list>
          <q-item v-for="item in sidebarItems" :key="item.label" clickable :active="activeSidebar === item.label" @click="activeSidebar = item.label" :class="['rounded-borders', activeSidebar === item.label ? 'bg-cyan-10 text-dark' : '']" style="margin-bottom:2px;">
            <q-item-section avatar><q-icon :name="item.icon" /></q-item-section>
            <q-item-section>{{ item.label }}</q-item-section>
          </q-item>
        </q-list>
      </div>
      <div class="q-pa-md">
        <q-separator class="q-my-md" />
        <div class="text-caption text-grey-5 q-mb-sm" style="background:#1a222b; border-radius:8px; padding:8px 12px;">Support this free platform with a 🎃 donation or <a href="#" class="text-cyan-3">membership</a>.</div>
        <q-btn round flat icon="delete" color="blue-grey-4" size="md" class="q-mt-sm" />
      </div>
    </aside>

    <!-- Main Content -->
    <main class="dashboard-main col" style="min-width:0; flex:1; display:flex; flex-direction:column;">
      <!-- Top Bar -->
      <header class="dashboard-header bg-blue-grey-10 q-px-lg q-py-sm flex items-center justify-between" style="border-bottom:2px solid #222b36;">
        <div class="row items-center">
          <img src="/icons/favicon-32x32.png" style="height:36px; margin-right:12px;" />
          <span class="text-h4 text-weight-bold q-mr-xl" style="letter-spacing:0.5px;">Stonk Journal</span>
          <div class="row q-gutter-xs">
            <q-btn v-for="label in filters" :key="label" :label="label" size="md"
              :color="activeFilter === label ? 'cyan-3' : 'blue-grey-9'"
              :text-color="activeFilter === label ? 'dark' : 'white'"
              :unelevated="true" rounded class="q-px-xl text-weight-bold" style="min-width:110px; font-size:15px;"
              @click="activeFilter = label"
            />
          </div>
        </div>
        <div class="row items-center q-gutter-md">
          <q-avatar size="38px" class="shadow-2">
            <img src="https://randomuser.me/api/portraits/men/32.jpg" />
          </q-avatar>
        </div>
      </header>
      <!-- Main Dashboard Content -->
      <div class="q-pa-lg" style="flex:1; overflow:auto;">
        <!-- Chart and Stat Row -->
        <div class="row q-gutter-md q-mb-md items-center">
          <q-card flat class="bg-blue-grey-10 q-pa-md" style="flex:2; min-width:400px; height:180px; border-radius:14px;">
            <div v-if="equityX.length && equityY.length">
              <canvas ref="equityChart" style="width:100%;height:120px;"></canvas>
            </div>
            <div v-else class="text-center text-cyan-3">No equity data</div>
          </q-card>
          <div class="col-auto flex column q-gutter-sm" style="min-width:320px;">
            <div class="row q-gutter-sm">
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">OPEN</div>
                <div class="text-h5 text-yellow-4 text-weight-bold">{{ openCount }}</div>
              </q-card>
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">CLOSED</div>
                <div class="text-h5 text-cyan-3 text-weight-bold">{{ closedCount }}</div>
              </q-card>
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">WINS</div>
                <div class="text-h5 text-green-4 text-weight-bold">{{ winCount }}</div>
              </q-card>
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">LOSSES</div>
                <div class="text-h5 text-red-4 text-weight-bold">{{ lossCount }}</div>
              </q-card>
            </div>
            <div class="row q-gutter-sm q-mt-sm">
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">PnL</div>
                <div class="text-h5 text-cyan-3 text-weight-bold">${{ pnl.toFixed(2) }}</div>
              </q-card>
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">WIN %</div>
                <div class="text-h5 text-green-3 text-weight-bold">{{ winRate }}</div>
              </q-card>
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">AVG WIN</div>
                <div class="text-h5 text-green-3 text-weight-bold">${{ avgWin }}</div>
              </q-card>
              <q-card class="bg-blue-grey-10 text-center q-pa-md" style="min-width:90px; border-radius:10px;">
                <div class="text-caption text-grey-4">AVG LOSS</div>
                <div class="text-h5 text-red-3 text-weight-bold">${{ avgLoss }}</div>
              </q-card>
            </div>
          </div>
        </div>
        <!-- Trades Table -->
        <q-card flat class="bg-blue-grey-10 q-pa-md" style="border-radius:14px;">
          <div class="text-h6 text-white q-mb-sm">Trades</div>
          <q-table
            :rows="trades"
            :columns="columns"
            row-key="Symbol"
            flat
            dense
            color="primary"
            class="bg-blue-grey-10 text-white rounded-borders"
            style="border-radius:12px;"
          >
            <template v-slot:body-cell-Status="props">
              <q-td :props="props">
                <q-badge :color="statusColorClass(props.row.Status)" rounded class="q-px-md text-weight-bold text-uppercase" style="font-size:13px;">
                  {{ props.row.Status }}
                </q-badge>
              </q-td>
            </template>
          </q-table>
        </q-card>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useQuasar } from 'quasar'

const filters = ['All', 'Today', 'Yesterday', 'This wk.', 'Last wk.', 'This mo.']
const activeFilter = ref('All')

const sidebarItems = [
  { label: 'Dashboard', icon: 'dashboard' },
  { label: 'Stats', icon: 'bar_chart' },
  { label: 'Calendar', icon: 'calendar_today' },
  { label: 'Settings', icon: 'settings' },
  { label: 'Help', icon: 'help' }
]
const activeSidebar = ref('Dashboard')
const account = ref('Default Account')

const columns = [
  { name: 'Date', label: 'Date', field: 'Date' },
  { name: 'Time', label: 'Time', field: 'Time' },
  { name: 'Symbol', label: 'Symbol', field: 'Symbol' },
  { name: 'Status', label: 'Status', field: 'Status' },
  { name: 'Side', label: 'Side', field: 'Side' },
  { name: 'Qty', label: 'Qty', field: 'Qty' },
  { name: 'Entry', label: 'Entry', field: 'Entry' },
  { name: 'Exit', label: 'Exit', field: 'Exit' },
  { name: 'Ent Tot', label: 'Ent Tot', field: 'Ent Tot' },
  { name: 'Ext Tot', label: 'Ext Tot', field: 'Ext Tot' },
  { name: 'Pos', label: 'Pos', field: 'Pos' },
  { name: 'Hold', label: 'Hold', field: 'Hold' },
  { name: 'Return', label: 'Return', field: 'Return' },
  { name: 'Return %', label: 'Return %', field: 'Return %' },
  { name: 'Exit Date', label: 'Exit Date', field: 'Exit Date' },
  { name: 'Exit Time', label: 'Exit Time', field: 'Exit Time' },
]

const allTrades = ref([])
const equityX = ref([])
const equityY = ref([])
const equityChart = ref(null)

const trades = computed(() => {
  if (activeFilter.value === 'All') return allTrades.value
  if (activeFilter.value === 'Today') return allTrades.value.filter(t => isToday(t.Date))
  if (activeFilter.value === 'Yesterday') return allTrades.value.filter(t => isYesterday(t.Date))
  if (activeFilter.value === 'This wk.') return allTrades.value.filter(t => isThisWeek(t.Date))
  if (activeFilter.value === 'Last wk.') return allTrades.value.filter(t => isLastWeek(t.Date))
  if (activeFilter.value === 'This mo.') return allTrades.value.filter(t => isThisMonth(t.Date))
  return allTrades.value
})

const winCount = computed(() => trades.value.filter(t => t.Status === 'WIN').length)
const lossCount = computed(() => trades.value.filter(t => t.Status === 'LOSS').length)
const openCount = computed(() => trades.value.filter(t => t.Status === 'OPEN').length)
const closedCount = computed(() => trades.value.filter(t => t.Status === 'WIN' || t.Status === 'LOSS').length)
const winRate = computed(() => {
  const total = winCount.value + lossCount.value;
  if (!total) return '0%';
  return Math.round((winCount.value / total) * 100) + '%';
})
const avgWin = computed(() => {
  const wins = trades.value.filter(t => t.Status === 'WIN');
  if (!wins.length) return '0.00';
  const sum = wins.reduce((acc, t) => {
    if (typeof t.Return === 'string' && t.Return.startsWith('$')) {
      return acc + (parseFloat(t.Return.replace(/[$,]/g, '')) || 0);
    }
    return acc;
  }, 0);
  return (sum / wins.length).toFixed(2);
})
const avgLoss = computed(() => {
  const losses = trades.value.filter(t => t.Status === 'LOSS');
  if (!losses.length) return '0.00';
  const sum = losses.reduce((acc, t) => {
    if (typeof t.Return === 'string' && t.Return.startsWith('$')) {
      return acc + (parseFloat(t.Return.replace(/[$,]/g, '')) || 0);
    }
    return acc;
  }, 0);
  return (sum / losses.length).toFixed(2);
})
const pnl = computed(() => {
  let total = 0
  trades.value.forEach(t => {
    if (typeof t.Return === 'string' && t.Return.startsWith('$')) {
      total += parseFloat(t.Return.replace(/[$,]/g, '')) || 0
    }
  })
  return total
})

watch(trades, () => {
  // Build equity curve from filtered trades
  // Only use closed trades (WIN/LOSS)
  const closed = trades.value.filter(t => (t.Status === 'WIN' || t.Status === 'LOSS') && t['Exit Date'] && t['Exit Date'] !== '-')

  let x = [];
  let y = [];
  let equity = 0;

  // For daily aggregation on certain filters
  const dailyAggregate = ['All', 'This wk.', 'Last wk.', 'This mo.'].includes(activeFilter.value);
  // For hourly aggregation on today/yesterday
  const hourlyAggregate = ['Today', 'Yesterday'].includes(activeFilter.value);

  if (hourlyAggregate) {
    // Group by exit date + hour (mm/dd/yyyy HH)
    const byHour = {};
    closed.forEach(t => {
      const date = t['Exit Date'];
      const time = t['Exit Time'] || t['Time'] || '00:00';
      // Extract hour (HH) from time (assume HH:MM or H:MM)
      const hour = time.split(':')[0].padStart(2, '0');
      const key = `${date} ${hour}`;
      if (!byHour[key]) byHour[key] = [];
      byHour[key].push(t);
    });
    // Sort keys ascending (date + hour)
    const sortedKeys = Object.keys(byHour).sort((a, b) => {
      // a, b: 'mm/dd/yyyy HH'
      const [adate, ahour] = a.split(' ');
      const [bdate, bhour] = b.split(' ');
      const da = adate.split('/');
      const db = bdate.split('/');
      const d1 = new Date(+da[2], +da[0] - 1, +da[1], +ahour);
      const d2 = new Date(+db[2], +db[0] - 1, +db[1], +bhour);
      return d1 - d2;
    });
    sortedKeys.forEach(key => {
      // Sum returns for this hour
      let hourSum = 0;
      byHour[key].forEach(t => {
        if (typeof t.Return === 'string' && t.Return.startsWith('$')) {
          hourSum += parseFloat(t.Return.replace(/[$,]/g, '')) || 0;
        }
      });
      equity += hourSum;
      x.push(key); // label: 'mm/dd/yyyy HH'
      y.push(equity);
    });
  } else if (dailyAggregate) {
    // Group by exit date (mm/dd/yyyy)
    const byDay = {};
    closed.forEach(t => {
      const date = t['Exit Date'];
      if (!byDay[date]) byDay[date] = [];
      byDay[date].push(t);
    });
    // Sort dates ascending
    const sortedDates = Object.keys(byDay).sort((a, b) => {
      const da = a.split('/');
      const db = b.split('/');
      const d1 = new Date(+da[2], +da[0] - 1, +da[1]);
      const d2 = new Date(+db[2], +db[0] - 1, +db[1]);
      return d1 - d2;
    });
    sortedDates.forEach(date => {
      // Sum returns for this day
      let daySum = 0;
      byDay[date].forEach(t => {
        if (typeof t.Return === 'string' && t.Return.startsWith('$')) {
          daySum += parseFloat(t.Return.replace(/[$,]/g, '')) || 0;
        }
      });
      equity += daySum;
      x.push(date);
      y.push(equity);
    });
  } else {
    // Sort by exit date ascending
    closed.sort((a, b) => {
      const da = a['Exit Date'].split('/');
      const db = b['Exit Date'].split('/');
      // mm/dd/yyyy
      const d1 = new Date(+da[2], +da[0] - 1, +da[1]);
      const d2 = new Date(+db[2], +db[0] - 1, +db[1]);
      return d1 - d2;
    });
    closed.forEach(t => {
      let ret = 0;
      if (typeof t.Return === 'string' && t.Return.startsWith('$')) {
        ret = parseFloat(t.Return.replace(/[$,]/g, '')) || 0;
      }
      equity += ret;
      x.push(t['Exit Date']);
      y.push(equity);
    });
  }
  equityX.value = x;
  equityY.value = y;
  nextTick().then(renderEquityChart);
});

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/trades')
    if (!res.ok) throw new Error('Failed to fetch trades')
    allTrades.value = await res.json()
    console.log('Loaded trade dates:', allTrades.value.map(t => t.Date));
    await nextTick();
    renderEquityChart();
  } catch {
    allTrades.value = []
    $q.notify({ message: 'Could not load trades from API', color: 'red', position: 'top' })
  }
})

watch(activeFilter, async () => {
  // Also update trades to match filter
  // (trades is a computed property, so it will update automatically)
  await nextTick();
  renderEquityChart();
})

watch([equityX, equityY], async () => {
  await nextTick()
  renderEquityChart()
})

function renderEquityChart() {
  const canvas = equityChart.value;
  if (!canvas || !equityX.value.length || !equityY.value.length) return;
  // Set canvas size to match its display size
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const w = canvas.width;
  const h = canvas.height;
  const minY = Math.min(...equityY.value);
  const maxY = Math.max(...equityY.value);
  const pad = 20;
  const n = equityY.value.length;
  ctx.strokeStyle = '#00bcd4';
  ctx.lineWidth = 2;
  ctx.beginPath();
  const points = [];
  equityY.value.forEach((y, i) => {
    const x = n === 1 ? w / 2 : pad + (w - 2 * pad) * (i / (n - 1));
    const yNorm = (y - minY) / (maxY - minY || 1);
    const yPx = h - pad - yNorm * (h - 2 * pad);
    points.push({ x, y: yPx, label: equityX.value[i], pnl: y });
    if (i === 0) ctx.moveTo(x, yPx);
    else ctx.lineTo(x, yPx);
  });
  ctx.stroke();
  // Draw points
  ctx.fillStyle = '#00bcd4';
  points.forEach(pt => {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 4, 0, 2 * Math.PI);
    ctx.fill();
  });
  // Tooltip logic
  if (canvas._tooltipHandler) {
    canvas.removeEventListener('mousemove', canvas._tooltipHandler);
    canvas.removeEventListener('mouseleave', canvas._tooltipLeaveHandler);
  }
  canvas._tooltipHandler = function (e) {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    // Find closest point within 12px
    let found = null;
    let minDist = 13; // px
    for (const pt of points) {
      const dist = Math.sqrt((mx - pt.x) ** 2 + (my - pt.y) ** 2);
      if (dist < minDist) {
        minDist = dist;
        found = pt;
      }
    }
    let tooltip = document.getElementById('equity-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'equity-tooltip';
      tooltip.style.position = 'fixed';
      tooltip.style.pointerEvents = 'none';
      tooltip.style.background = '#232b3e';
      tooltip.style.color = '#fff';
      tooltip.style.padding = '7px 14px';
      tooltip.style.borderRadius = '8px';
      tooltip.style.fontSize = '14px';
      tooltip.style.boxShadow = '0 2px 8px #0006';
      tooltip.style.zIndex = 1000;
      document.body.appendChild(tooltip);
    }
    if (found) {
      tooltip.style.display = 'block';
      tooltip.style.left = (e.clientX + 12) + 'px';
      tooltip.style.top = (e.clientY - 10) + 'px';
      tooltip.innerHTML = `<b>${found.label}</b><br/>Equity: $${found.pnl.toFixed(2)}`;
    } else {
      tooltip.style.display = 'none';
    }
  };
  canvas._tooltipLeaveHandler = function () {
    const tooltip = document.getElementById('equity-tooltip');
    if (tooltip) tooltip.style.display = 'none';
  };
  canvas.addEventListener('mousemove', canvas._tooltipHandler);
  canvas.addEventListener('mouseleave', canvas._tooltipLeaveHandler);
}

function isToday(dateStr) {
  const today = new Date();
  const [mm, dd, yyyy] = dateStr.split('/');
  const isMatch = today.getFullYear() === +yyyy && today.getMonth()+1 === +mm && today.getDate() === +dd;
  // Debug log
  if (activeFilter.value === 'Today') {
    console.log('Checking isToday:', {dateStr, today: today.toLocaleDateString(), isMatch});
  }
  return isMatch;
}
function isYesterday(dateStr) {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  const [mm, dd, yyyy] = dateStr.split('/')
  return yesterday.getFullYear() === +yyyy && yesterday.getMonth()+1 === +mm && yesterday.getDate() === +dd
}
function isThisWeek(dateStr) {
  // Use ISO week: Monday as the first day of the week
  const today = new Date();
  const [mm, dd, yyyy] = dateStr.split('/');
  const d = new Date(`${yyyy}-${mm}-${dd}`);
  // Get Monday of this week
  const day = today.getDay();
  const diffToMonday = (day === 0 ? -6 : 1) - day; // Sunday (0) -> last Monday
  const weekStart = new Date(today);
  weekStart.setHours(0,0,0,0);
  weekStart.setDate(today.getDate() + diffToMonday);
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekStart.getDate() + 6);
  weekEnd.setHours(23,59,59,999);
  return d >= weekStart && d <= weekEnd;
}
function isLastWeek(dateStr) {
  const today = new Date()
  const [mm, dd, yyyy] = dateStr.split('/')
  const d = new Date(`${yyyy}-${mm}-${dd}`)
  const weekStart = new Date(today)
  weekStart.setDate(today.getDate() - today.getDay() - 7)
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6)
  return d >= weekStart && d <= weekEnd
}
function isThisMonth(dateStr) {
  const today = new Date();
  const [mm, , yyyy] = dateStr.split('/');
  return today.getFullYear() === +yyyy && (today.getMonth() + 1) === +mm;
}

function statusColorClass(status) {
  if (status === 'WIN') return 'text-green-4'
  if (status === 'LOSS') return 'text-red-4'
  if (status === 'OPEN') return 'text-yellow-4'
  return ''
}

function showSnackbar(msg) {
  $q.notify({ message: msg, color: 'cyan-3', textColor: 'black', position: 'top' })
}

const { $q } = useQuasar()
</script>

<style>
body, #q-app {
  background: #181e29 !important;
  min-height: 100vh;
  margin: 0 !important;
  padding: 0 !important;
}
.dashboard-root {
  min-height: 100vh;
  width: 100vw;
  overflow: hidden;
}
.dashboard-sidebar {
  box-shadow: none !important;
  left: 0 !important;
}
.dashboard-header {
  width: 100%;
}
</style>
