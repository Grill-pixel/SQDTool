# SQDTool — Modern Squad Management Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-0F172A)
![License](https://img.shields.io/badge/License-MIT-10B981)

**SQDTool** is a Tkinter desktop app to manage a squad, build a tactical layout, and export clean PDFs ready to share. It features a flexible roster editor, an interactive pitch view, and a modern theme system.

**Languages:** [Français](README.md) · [العربية](README.ar.md) · [License](LICENSE)

---

## Table of contents

- [Features](#features)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Club settings](#club-settings)
  - [Squad editor](#squad-editor)
  - [Disposition (pitch)](#disposition-pitch)
  - [PDF exports](#pdf-exports)
- [Files & persistence](#files--persistence)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Full squad management**: add, edit, delete players in seconds.
- **Interactive tactical disposition**: place players and reposition slots manually.
- **Squad PDF**: structured by positions.
- **Disposition PDF**: a faithful export of the on-screen pitch.
- **Modern themes**: 12 built-in palettes, auto-save settings.
- **Persistent settings**: club name, season, and theme.

---

## Quick start

1. Launch the app: `python marseille.pyw`.
2. Edit the roster in **Edit composition**.
3. Arrange the team in **Disposition**.
4. Export PDFs for the squad and the pitch.

---

## Installation

```bash
git clone <your-repo>
cd SQDTool
python marseille.pyw
```

> On first run, **fpdf2** is installed automatically if needed. The disposition export installs **Pillow** if required.

---

## Usage

### Club settings
In **Club settings**, you can edit:

- **Club name**
- **Season**
- **Theme**

Click **Apply** to refresh the interface and exports.

### Squad editor
Open **Edit composition** to:

- Add a player (name, role, age, nationality, status, option).
- Update existing rows.
- Delete selected entries.
- Save the composition as JSON.

### Disposition (pitch)
The **Disposition** view lets you build a tactical layout on a half pitch:

- **Player placement mode**: select a player, then click a slot.
- **Slot movement mode**: drag slots to fine-tune spacing.
- **Refresh roster**: reloads the squad list if it changes.
- **Reset**: clear placements or slot positions.

### PDF exports

- **Squad PDF**: use **Generate PDF** (grouped by roles).
- **Disposition PDF**: use **Export to PDF** inside the disposition window.

The disposition PDF is a **faithful snapshot** of the pitch (slots, names, layout).

---

## Files & persistence

- `composition.json` (or `effectifOM.json`): squad data.
- `settings.json`: club name, season, theme.
- `om_program_logs.txt`: runtime logs.
- `PDFs/`: PDF exports.

---

## Customization

Add a theme in `marseille.pyw` under the `themes` dictionary:

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

- **PDF export error**: ensure internet access for the initial install of `fpdf2` and `pillow`.
- **Missing PDF**: confirm the export folder you selected.
- **Truncated labels**: expand the window before exporting the disposition.

---

## License

This project is released under the MIT license. See `LICENSE`.
