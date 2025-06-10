---
applyTo: '**'
---
# Dash Project Instructions

This project is a Dash (Plotly) web app for a personal trading journal and analytics dashboard.

---

## Coding Standards

- **Use Python 3.10+ (type hints required for all functions/classes).**
- **Modularize code:** Split into pages, components, callbacks, and utility modules.
- **Dash pages:** Organize each “view” (e.g., Trade Log, Analytics, Dashboard) in its own file/module.
- **Custom components:** Place in `/components/` or `/layout/`.
- **Use `.env` for sensitive config or API keys.**
- **Lint code with flake8 or pylint and format with Black.**

---

## SOLID Principles in Python/Dash

- **Single Responsibility:**  
  Each module, callback, or function should handle one logical task.
- **Open/Closed:**  
  Use function parameters, config files, and class inheritance (if needed) to make code extensible, not rewritable.
- **Liskov Substitution:**  
  When subclassing (rare in Dash), ensure all children honor parent contracts.
- **Interface Segregation:**  
  Avoid massive utility files; split logic by feature.
- **Dependency Inversion:**  
  High-level app logic shouldn’t depend on concrete data sources—use abstraction for DB/API access.

---

## Folder Structure

```
/app.py                # Entry point
/assets/               # CSS, images, favicon, etc.
/components/           # Custom layout or chart components
/pages/                # Each app page (trade log, stats, etc.)
/utils/                # Data loading, analytics, helpers
/data/                 # Local DB (SQLite/CSV), example data files
.env                   # Config/credentials (not in repo)
requirements.txt
```

---

## Best Practices

- **Type everything** (inputs, outputs, variables).
- **All callbacks must be modular and documented.**
- **Use environment variables for secrets/API keys.**
- **Write utility functions for repeated logic.**
- **Keep layout and callback logic separate as much as possible.**
- **Document each function and module.**
- **Test utilities with pytest where practical.**
- **All visuals must be clear, accessible, and labeled.**

---

## Code Review Checklist

- [ ] Code is modular (no huge files).
- [ ] All functions and modules have type hints and docstrings.
- [ ] Layout and logic are cleanly separated.
- [ ] Code passes flake8/pylint and Black.
- [ ] Secrets/config are never hardcoded.

---

## Additional Notes

- Prefer clarity and maintainability over cleverness.
- Aim for extensibility—easy to add new analytics, pages, or charts.

---

*Please follow these instructions for a scalable, maintainable, and professional Dash app.*
