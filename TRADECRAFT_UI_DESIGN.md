# TradeCraft App UI Redesign (2025)

This document outlines a new, dark, modern visual design for the TradeCraft stock journaling app. The design is inspired by your latest banner image with prominent candlesticks in the background.

---

## 1. Header / Banner

- Use the new banner image as a full-width header (80–120px tall).
- Candlestick chart motif is high-contrast and fully visible.
- Place the app name ("TradeCraft") in bold white or neon blue/green on the left.
- Navigation links (Trade Log, Analytics, Calendar) in light gray/blue, with neon accent or underline on hover.
- Add a soft shadow or glow beneath the header for separation.

## 2. Background

- Main background: Deep, dark gray (`#181C25`).
- Optional: Subtle repeating candlestick chart watermark (low opacity) as a full-page background motif.

## 3. Card & Section Styling

- Cards/panels: Slightly lighter dark (`#222436`–`#23273A`), softly rounded corners (12–16px).
- Box shadows: Subtle neon blue/green for depth.
- Borders: 1–2px accent border on active/focused cards.
- Section titles: White or neon-accented, bold, modern font. Candlestick icon for section branding.

## 4. Filters & Inputs

- Inputs: Dark backgrounds (`#262A3C`), white/blue placeholder, neon accent on focus.
- Primary buttons: Gradient neon blue-green.
- Secondary buttons: Dark gray with blue borders.
- Filter buttons (Today, This Week, etc.): Pill-shaped, neon border when active.

## 5. Chart

- Plot background matches card or is slightly darker.
- Equity curve: Neon blue or green line.
- Axis text: Light gray/white.
- Gridlines: Very faint.
- Highlight recent data: Brighter dot or glow on last value.

## 6. Stats Card

- Same card style as others, slight gradient or neon border.
- Stat labels: Muted blue/gray.
- Stat values: Bright neon for positives, soft red for negatives.
- Icons for wins/losses.

## 7. Trade Table

- Dark table with subtle zebra stripes.
- Text: White or blue, color-coded for status.
- Table header: Neon accent underline or border.
- Icons: Blue/green.
- Row hover: Subtle highlight with accent border.

## 8. Floating Action Button (FAB)

- Neon blue/green, glowing effect, white plus icon. Stronger glow on hover.

## 9. Font & Spacing

- Font: Inter, Roboto, or Montserrat.
- Generous spacing, line height, and padding.

---

## CSS Sample

```css
body {
  background: #181C25;
  color: #F6F8FA;
  font-family: 'Inter', 'Roboto', 'Montserrat', sans-serif;
}

.header {
  background-image: url('YOUR_NEW_BANNER_IMAGE_PATH');
  background-size: cover;
  background-position: center;
  min-height: 100px;
  box-shadow: 0 6px 24px #1aa9e540;
  display: flex;
  align-items: center;
  padding: 0 32px;
}

.header .app-name {
  color: #fff;
  font-size: 2.4rem;
  font-weight: bold;
  letter-spacing: 2px;
  margin-right: 48px;
  text-shadow: 0 2px 16px #00FFCC80;
}

.header .nav-link {
  color: #b0dfff;
  margin: 0 18px;
  font-size: 1.2rem;
  text-decoration: none;
  transition: color 0.2s;
}
.header .nav-link:hover {
  color: #00FFCC;
  border-bottom: 2px solid #00FFCC;
}

.card, .filter-row, .stats {
  background: #23273A;
  border-radius: 16px;
  box-shadow: 0 2px 16px #00FFCC33;
  padding: 18px;
  margin-bottom: 24px;
}

.button-primary {
  background: linear-gradient(90deg, #1AA9E5, #00FFCC);
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 2px 16px #1AA9E566;
}
.button-primary:hover {
  background: #00FFCC;
  box-shadow: 0 2px 32px #00FFCCCC;
}
```

---

## Implementation Steps

1. Replace your old header with the new banner image.
2. Update main CSS/theme to match these styles (adapt for your UI framework as needed).
3. Use candlestick motif as a watermark if desired.
4. Apply accent colors, glow/shadow effects, and font/padding adjustments.
5. Use this document as a reference for Copilot or any developer working on the project.

---

**This design harmonizes with your branding and delivers a modern, pro dashboard look.**
