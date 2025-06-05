# TradeLedger

A private, customizable trade journal and analytics dashboard for Interactive Brokers (IBKR) and general trading.

## 🚀 Overview

**TradeLedger** is a self-hosted trading journal and performance dashboard inspired by platforms like TraderSync and TraderVue, but with a focus on custom analytics, privacy, and complete user control. Track your trades, visualize performance, and improve your trading process—all in one place.

---

## ✨ Features

- **Import trades** from IBKR (CSV or API).
- **Manual trade log:** Add, edit, and delete trades with notes, tags, and screenshots.
- **Dashboard:** Visualize daily, weekly, and monthly P&L, win rate, average win/loss, equity curve, and drawdowns.
- **Risk management:** Calculate and display current max trade size based on account balance and user-defined rules (e.g., 2% per trade).
- **Filtering:** Search and filter trades by ticker, setup, tag, or date.
- **Scorecard:** Weekly/monthly performance summaries and statistics.
- **Data export:** Export all trade data as CSV.
- **Custom analytics:** Easily extend with new stats or charts.
- **Simple web interface:** Streamlit (default), Dash, or Flask + React.
- **Local storage:** Uses SQLite or flat files for privacy and portability.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, [ib_insync](https://github.com/erdewit/ib_insync) (optional for IBKR API)
- **Frontend:** Streamlit *(easy to swap for Dash or Flask + React)*
- **Data:** SQLite (default), CSV import/export
- **Visualization:** Plotly, Altair, or Matplotlib

---

## ⚡ Getting Started

1. **Clone this repository:**
    ```bash
    git clone https://github.com/yourusername/tradeledger.git
    cd tradeledger
    ```

2. **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

3. **(Optional) Set up IBKR API access:**  
    Follow the [ib_insync guide](https://github.com/erdewit/ib_insync) or use CSV exports from IBKR.

4. **Run the app:**
    ```bash
    streamlit run app.py
    ```

5. **Start journaling!**  
    Import or manually enter your trades and explore your dashboard.

---

## 🎯 Roadmap

- [ ] Import from IBKR API (auto-sync)
- [ ] Tag-based analytics and P&L by setup
- [ ] Screenshots and file uploads for trades
- [ ] Mobile-friendly layout
- [ ] Custom user dashboard (add widgets/metrics)
- [ ] Broker-agnostic import/export

---

## 🤝 Contributing

PRs and issues welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙋‍♂️ Questions or Feature Requests?

Open an issue or start a discussion!

---

