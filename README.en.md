# SQDTool — Modern Squad Management Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-0F172A)
![License](https://img.shields.io/badge/License-MIT-10B981)

**SQDTool** is a Tkinter desktop application built to manage a squad, create a tactical lineup visually, and export clean, shareable PDFs. It combines a roster editor, an interactive pitch view, and theming for a polished experience.

**Languages:** [Français](README.md) · [العربية](README.ar.md) · [License](LICENSE)

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick Installation](#quick-installation)
- [User Guide](#user-guide)
  - [1) Club settings](#1-club-settings)
  - [2) Squad management](#2-squad-management)
  - [3) Tactical layout](#3-tactical-layout)
  - [4) PDF exports](#4-pdf-exports)
- [Files, persistence, formats](#files-persistence-formats)
- [Theme customization](#theme-customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Full squad management**: add, edit, delete in one click.
- **Rich editor**: live search, player form, JSON save/load.
- **Interactive tactical layout**: role-based placement + manual position tweaks.
- **PDF exports**:
  - **Squad PDF** (structured columns)
  - **Lineup PDF** (faithful capture of the pitch view)
- **Modern themes**: 12 built-in palettes, auto-saved.
- **Persistence**: club name, season, theme, composition, and layout saved.

---

## Requirements

- **Python 3.9+**
- **pip** access (to install dependencies if missing)

> Dependencies: `fpdf2` (PDF export) and `Pillow` (lineup capture). They are installed automatically when needed.

---

## Quick Installation

```bash
git clone <your-repo>
cd SQDTool
python marseille.pyw
```

---

## User Guide

### 1) Club settings
In the **Settings** tab you can edit:

- **Club name**
- **Season**
- **Theme**

Click **Apply** to update the UI and exports.

### 2) Squad management
Open **Edit squad** to:

- Add a player (name, position, age, nationality, status, option).
- Update an existing row.
- Delete selected entries.
- Load/Save squad data as JSON.

### 3) Tactical layout
The **Pitch layout** view lets you build a lineup on a half-pitch:

- **Player placement mode**: select a player, click a role to assign.
- **Slot move mode**: drag role slots to fine-tune spacing.
- **Save / Load**: store placements and positions per formation.
- **Reset**: clear assignments or positions.

### 4) PDF exports

- **Squad PDF**: click **Squad PDF** from the sidebar or Actions tab.
- **Lineup PDF**: click **Export to PDF** in the layout window.

Exports match the **current UI state** (titles, theme, positions).

---

## Files, persistence, formats

| File / folder | Purpose |
| --- | --- |
| `effectifOM.json` | Default squad if `composition.json` does not exist |
| `composition.json` | Saved squad data (array or dictionary formats) |
| `settings.json` | Club name, season, theme |
| `disposition_layout.json` | Saved layout positions by formation |
| `PDFs/` | PDF exports |
| `om_program_logs.txt` | Runtime logs |

### Supported squad formats
The squad file can be:
- a list of rows `[[player, position, age, nationality, status, option], ...]`,
- or a dictionary of categories, which is normalized automatically.

---

## Theme customization

Themes are defined in `marseille.pyw` via the `themes` dictionary:

```python
"My Theme": {
    "bg": "#...",
    "card": "#...",
    "primary": "#...",
    "accent": "#...",
    "text": "#...",
    "muted": "#...",
    "button": "#...",
    "button_text": "#...",
}
```

---

## Troubleshooting

- **PDF export fails**: ensure `fpdf2` is installed (network required on first run).
- **Lineup export error**: `Pillow` is required; offline installs may fail.
- **Truncated labels**: enlarge the layout window before exporting.
- **Missing fonts**: on some systems the PDF export may use a fallback font.

---

## License

This project is licensed under MIT. See `LICENSE`.
