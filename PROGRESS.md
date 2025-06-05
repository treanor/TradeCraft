# TradeLedger Project Progress

_Last updated: 2025-06-05_

## ✅ Completed
- Designed trade data model (SQLite schema in `db.py`).
- Implemented basic CRUD functions: add, view, edit, delete trades.
- Created Streamlit app with manual trade entry form and trade table display.
- Basic P&L aggregation and dashboard charts (daily/weekly/monthly).

## 🚧 In Progress / Next Steps
- Add edit and delete functionality to the UI (Streamlit table actions).
- Add basic data validation for trade entries (required fields, positive numbers).
- Add filtering/searching by ticker, date, or tags in the trade table.
- CSV import/export (start with IBKR format).
- More analytics: equity curve, drawdown, win rate, best/worst trades, etc.
- Risk management logic and warnings.
- Tagging, notes, and journaling enhancements.
- Modular dashboard widgets.

## 📝 Notes
- Code is modular and uses type hints/docstrings.
- All code is self-hosted, no cloud dependencies.
- See `readme.md` for full feature list and roadmap.

---

Feel free to update this file as progress is made or priorities change.
