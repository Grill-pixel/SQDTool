# SQDTool – Squad Management Dashboard

SQDTool is a lightweight desktop application (Tkinter) that helps football staff organize a squad list, keep the data editable, and export a structured PDF report. The interface includes modern cards, quick actions, and a theme switcher with multiple color palettes.

Languages: [Français](README.md) | [العربية](README.ar.md) | [License](LICENSE)

## Highlights

- **Editable club name and season** (no hard‑coded “Olympique de Marseille 2025‑2026”).
- **Full roster editor** with add/update/delete and persistent storage.
- **PDF export** grouped by positions, ready to share.
- **Modern UI theming** with 12 curated themes.
- **Autosave settings** (club name, season, theme).

## Requirements

- Python 3.9+
- Internet access (first run may install `fpdf2` automatically)

## Installation

```bash
git clone <your-repo>
cd SQDTool
python marseille.pyw
```

> On first run, the app installs `fpdf2` via `pip` if it is missing.

## Main Features

### 1) Club and Season Settings
Use the **“Paramètres du club”** card to edit:

- **Nom du club** (club name)
- **Saison** (season string)
- **Thème** (theme selector)

Click **Appliquer** to save and update the title, status panel, and PDF header.

### 2) Theme Switcher
The dropdown offers 12 palettes (e.g., “Azur & Or”, “Lavande Moderne”, “Océan Profond”). The chosen theme updates the interface immediately and is saved for next launch.

### 3) Roster Editor
Click **Éditer la composition** to open the editor:

- Add, update, or remove players.
- Data is stored in `composition.json` for persistence.
- The editor behaves like a simple spreadsheet (table + form).

### 4) PDF Export
Click **Générer le PDF** to export the roster.

- Automatically groups players by position.
- Uses the current club name and season in the PDF header.
- PDF is saved to the selected folder (default: `PDFs/`).

## Files and Persistence

- `composition.json`: roster data saved locally.
- `settings.json`: club name, season, and selected theme.
- `om_program_logs.txt`: local debug logs.
- `PDFs/`: export directory.

## Customization

To add new themes, edit the `themes` dictionary in `marseille.pyw`:

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

## Troubleshooting

- **FPDF installation fails**: Run `pip install fpdf2` manually.
- **No PDF output**: Ensure the selected folder is writable.
- **Fonts on non‑Windows systems**: Adjust font paths in `generate_pdf_file()` to available fonts.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
