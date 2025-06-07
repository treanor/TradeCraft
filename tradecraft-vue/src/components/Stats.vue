<template>
  <div class="stats">
    <FilterButtons v-model="selectedFilter" :options="FILTER_OPTIONS" />
    <h1>Trade Stats</h1>
    <div class="stats-grid">
      <div class="stat-card">
        <h2>Total Trades</h2>
        <p>{{ totalTrades }}</p>
      </div>
      <div class="stat-card">
        <h2>Wins</h2>
        <p>{{ winCount }}</p>
      </div>
      <div class="stat-card">
        <h2>Losses</h2>
        <p>{{ lossCount }}</p>
      </div>
      <div class="stat-card">
        <h2>Open</h2>
        <p>{{ openCount }}</p>
      </div>
      <div class="stat-card">
        <h2>Win Rate</h2>
        <p>{{ winRate }}%</p>
      </div>
      <div class="stat-card">
        <h2>Avg Return</h2>
        <p>{{ avgReturn }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { sampleTrades } from '../data/sampleTrades';
import { computed, ref } from 'vue';
import FilterButtons from './FilterButtons.vue';

const FILTER_OPTIONS = [
  { label: 'All', value: 'all' },
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'This wk.', value: 'this_week' },
  { label: 'Last wk.', value: 'last_week' },
  { label: 'This mo.', value: 'this_month' },
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
    case 'all':
    default:
      return trades;
  }
}

const filteredTrades = computed(() => filterTrades(sampleTrades, selectedFilter.value));

const totalTrades = computed(() => filteredTrades.value.length);
const winCount = computed(() => filteredTrades.value.filter(t => t.status === 'WIN').length);
const lossCount = computed(() => filteredTrades.value.filter(t => t.status === 'LOSS').length);
const openCount = computed(() => filteredTrades.value.filter(t => t.status === 'OPEN').length);
const winRate = computed(() => totalTrades.value ? ((winCount.value / totalTrades.value) * 100).toFixed(2) : '0.00');
const avgReturn = computed(() => {
  let total = 0, count = 0;
  filteredTrades.value.forEach(trade => {
    if (trade.legs.length > 1) {
      const entry = trade.legs[0];
      const exit = trade.legs[1];
      const entTot = entry.quantity * entry.price + (entry.fee || 0);
      const extTot = exit.quantity * exit.price - (exit.fee || 0);
      total += (extTot - entTot);
      count++;
    }
  });
  return count ? `$${(total / count).toFixed(2)}` : '-';
});
</script>

<style scoped>
.stats {
  padding: 2rem;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}
.stat-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 1.5rem;
  text-align: center;
}
.stat-card h2 {
  font-size: 1.1rem;
  color: #888;
  margin-bottom: 0.5rem;
}
.stat-card p {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
}
</style>
