// src/data/sampleTrades.js
// Sample trade data converted from Python for the Vue app
export const sampleTrades = [
  // Example trade, more will be added
  {
    trade_id: "1",
    user_id: "user1",
    symbol: "AAPL250601C150",
    asset_type: "option",
    created_at: "2025-06-01T10:30:00",
    status: "WIN",
    legs: [
      { action: "buy", datetime: "2025-06-01T10:30:00", quantity: 2, price: 100, fee: 0 },
      { action: "sell", datetime: "2025-06-02T14:00:00", quantity: 2, price: 120, fee: 0 }
    ],
    tags: ["Fidelity"]
  },
  // --- 3 months of sample trades, 1 per weekday ---
  ...(() => {
    const trades = [];
    const start = new Date('2025-03-10'); // 3 months before June 7, 2025
    const end = new Date('2025-06-07');
    let id = 2;
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      // Skip weekends
      if (d.getDay() === 0 || d.getDay() === 6) continue;
      const symbol = ["AAPL", "MSFT", "TSLA", "SPY", "QQQ"][Math.floor(Math.random() * 5)] +
        d.getFullYear().toString().slice(-2) +
        (d.getMonth() + 1).toString().padStart(2, '0') +
        d.getDate().toString().padStart(2, '0') +
        "C" + (100 + Math.floor(Math.random() * 100));
      const entryPrice = 100 + Math.random() * 100;
      const exitPrice = entryPrice + (Math.random() - 0.5) * 40;
      const qty = 1 + Math.floor(Math.random() * 3);
      const status = exitPrice > entryPrice ? "WIN" : (exitPrice < entryPrice ? "LOSS" : "WASH");
      trades.push({
        trade_id: id.toString(),
        user_id: "user1",
        symbol,
        asset_type: "option",
        created_at: d.toISOString(),
        status,
        legs: [
          { action: "buy", datetime: d.toISOString(), quantity: qty, price: entryPrice, fee: 0 },
          { action: "sell", datetime: new Date(d.getTime() + 1000 * 60 * 60 * (1 + Math.random() * 48)).toISOString(), quantity: qty, price: exitPrice, fee: 0 }
        ],
        tags: ["Fidelity"]
      });
      id++;
    }
    return trades;
  })()
];
