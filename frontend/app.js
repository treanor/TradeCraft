const Dashboard = {
  props: ['trades'],
  computed: {
    wins() {
      return this.trades.filter(t => t.status === 'WIN').length;
    },
    losses() {
      return this.trades.filter(t => t.status === 'LOSS').length;
    },
    pnl() {
      return this.trades.reduce((acc, t) => {
        if (t.legs.length > 1 && (t.status === 'WIN' || t.status === 'LOSS')) {
          const entry = t.legs[0];
          const exit = t.legs[1];
          return acc + (exit.price - entry.price) * entry.quantity;
        }
        return acc;
      }, 0);
    }
  },
  template: `
    <div>
      <div class="stat-block">
        <div class="stat-label">WINS</div>
        <div class="stat-value win">{{ wins }}</div>
      </div>
      <div class="stat-block">
        <div class="stat-label">LOSSES</div>
        <div class="stat-value loss">{{ losses }}</div>
      </div>
      <div class="stat-block">
        <div class="stat-label">PnL</div>
        <div class="stat-value">{{ pnl.toFixed(2) }}</div>
      </div>
    </div>
  `
};

const Stats = {
  props: ['trades'],
  computed: {
    totalTrades() { return this.trades.length; }
  },
  template: `
    <div>
      <p>Total trades: {{ totalTrades }}</p>
      <p>This is a placeholder for a more detailed stats page.</p>
    </div>
  `
};

const app = Vue.createApp({
  data() {
    return {
      trades: [],
      view: 'dashboard'
    };
  },
  computed: {
    currentView() {
      return this.view === 'stats' ? Stats : Dashboard;
    }
  },
  mounted() {
    fetch('sample_trades.json')
      .then(r => r.json())
      .then(data => { this.trades = data; });
  }
});

app.mount('#app');
