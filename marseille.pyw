import os
import sys
import logging
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

# -----------------------------
# Vérification des bibliothèques
# -----------------------------
try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from fpdf import FPDF

# -----------------------------
# Logs
# -----------------------------
log_file = os.path.join(os.path.dirname(__file__), "om_program_logs.txt")
logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Programme démarré")

# -----------------------------
# Variables globales
# -----------------------------
pdf_folder = os.path.join(os.path.dirname(__file__), "PDFs")
os.makedirs(pdf_folder, exist_ok=True)
pdf_filename = "OM_Effectif_Pretes_2025_2026.pdf"
composition_file = os.path.join(os.path.dirname(__file__), "composition.json")
settings_file = os.path.join(os.path.dirname(__file__), "settings.json")

default_settings = {
    "club_name": "Olympique de Marseille",
    "season": "2025-2026",
    "theme": "Azur & Or"
}
settings = default_settings.copy()

if os.path.exists(settings_file):
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            stored_settings = json.load(f)
        settings.update({k: v for k, v in stored_settings.items() if k in settings})
        logging.debug("Paramètres chargés depuis settings.json")
    except Exception as e:
        logging.error(f"Erreur chargement settings : {e}")

headers = ['Joueur', 'Poste', 'Âge', 'Nationalité', 'Statut', 'Option d’achat']

# -----------------------------
# Effectif par défaut
# -----------------------------
effectif = [
    ['Gerónimo Rulli', 'Gardien', '33', 'ARG', 'Permanent (2027)', '—'],
    ['Jeffrey de Lange', 'Gardien', '27', 'NED', 'Permanent (2027)', '—'],
    ['Jelle Van Neck', 'Gardien', '21', 'BEL', 'Permanent', '—'],
    ['Théo Vermot', 'Gardien', '28', 'FRA', 'Permanent (2026)', '—'],
    ['CJ Egan-Riley', 'DC', '23', 'ENG', 'Permanent', '—'],
    ['Leonardo Balerdi', 'DC', '27', 'ARG/ITA', 'Permanent', '—'],
    ['Nayef Aguerd', 'DC', '29', 'MAR', 'Permanent', '—'],
    ['Benjamin Pavard', 'DC', '29', 'FRA', 'Prêt entrant', 'OA ~15M€'],
    ['Facundo Medina', 'DC', '26', 'ARG', 'Prêt entrant', 'OA 18M€ + 2M€ bonus'],
    ['Emerson Palmieri', 'DG', '31', 'ITA', 'Permanent', '—'],
    ['Amir Murillo', 'DL', '29', 'PAN', 'Permanent', '—'],
    ['Tochukwu Nnadi', 'MDF', '22', 'NGA', 'Permanent', '—'],
    ['Himad Abdelli', 'MC', '26', 'ALG/MG', 'Permanent', '—'],
    ['Arthur Vermeeren', 'MC', '20', 'BEL', 'Prêt entrant', 'OA 20M€'],
    ['Geoffrey Kondogbia', 'MDF', '32', 'CTA', 'Permanent', '—'],
    ['Pierre-Emile Højbjerg', 'MDF', '30', 'DEN', 'Permanent', '—'],
    ['Bilal Nadir', 'MC', '22', 'MAR', 'Permanent', '—'],
    ['Quinten Timber', 'MC', '24', 'NED', 'Permanent', '—'],
    ['Yanis Sellami', 'MC', '19', 'FRA/ALG', 'Permanent', '—'],
    ['Amine Gouiri', 'AC', '25', 'ALG/FRA', 'Permanent', '—'],
    ['Mason Greenwood', 'Ailier/AC', '24', 'ENG', 'Prêt entrant', 'Sans OA'],
    ['Igor Paixão', 'Ailier', '25', 'BRA', 'Permanent', '—'],
    ['Pierre-Emerick Aubameyang', 'AC', '36', 'GAB', 'Permanent', '—'],
    ['Hamed Junior Traoré', 'Ailier/AC', '25', 'CIV', 'Prêt entrant', 'OA 8M€ + 50% revente'],
    ['Ethan Nwaneri', 'Ailier/AC', '18', 'ENG', 'Prêt entrant', 'Sans OA'],
    ['Tadjidine Mmadi', 'AC', '18-19', 'FRA', 'Permanent', '—'],
    ['Neal Maupay', 'AC', '28', 'Sevilla FC', '30/06/2026', 'Sans OA'],
    ['Angel Gomes', 'MO', '25', 'Wolverhampton', '30/06/2026', 'OA ~6M€'],
    ['Matt O’Riley', 'MC', '23', 'Brighton', 'Prêt terminé', '—']
]

# Charger composition sauvegardée si existante
if os.path.exists(composition_file):
    try:
        with open(composition_file, "r", encoding="utf-8") as f:
            effectif = json.load(f)
        logging.debug("Composition chargée depuis fichier JSON")
    except Exception as e:
        logging.error(f"Erreur chargement composition : {e}")

# -----------------------------
# PDF UTF-8 avec FPDF2
# -----------------------------
class PDF(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 16)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"{settings['club_name']} {settings['season']}", 0, 1, 'C', 1)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def wrap_text(pdf, text, width):
    text = str(text) if text is not None else ""
    if not text:
        return [""]
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdf.get_string_width(candidate) <= width - 2:
            current = candidate
            continue
        if current:
            lines.append(current)
        if pdf.get_string_width(word) <= width - 2:
            current = word
            continue
        segment = ""
        for char in word:
            candidate_segment = segment + char
            if pdf.get_string_width(candidate_segment) <= width - 2:
                segment = candidate_segment
            else:
                if segment:
                    lines.append(segment)
                segment = char
        current = segment
    if current:
        lines.append(current)
    return lines


def compute_column_widths(pdf, headers, data, min_width=20, padding=6):
    widths = []
    for i, header in enumerate(headers):
        max_width = pdf.get_string_width(header)
        for row in data:
            max_width = max(max_width, pdf.get_string_width(str(row[i])))
        widths.append(max_width + padding)
    total = sum(widths)
    available = pdf.w - pdf.l_margin - pdf.r_margin
    if total > available:
        scale = available / total
        widths = [max(min_width, width * scale) for width in widths]
    return widths


def add_table(pdf, title, headers, data):
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(0, 10, title, 0, 1, 'L', 1)
    pdf.set_font('DejaVu', 'B', 10)

    col_widths = compute_column_widths(pdf, headers, data)

    for w, header in zip(col_widths, headers):
        pdf.cell(w, 8, header, 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font('DejaVu', '', 10)
    line_height = pdf.font_size * 1.6
    for row in data:
        wrapped_cells = [wrap_text(pdf, item, width) for item, width in zip(row, col_widths)]
        max_lines = max(len(lines) for lines in wrapped_cells)
        row_height = line_height * max_lines
        start_x = pdf.l_margin
        start_y = pdf.get_y()
        for width, lines in zip(col_widths, wrapped_cells):
            pdf.set_xy(start_x, start_y)
            pdf.multi_cell(width, line_height, "\n".join(lines), border=1, align='C')
            start_x += width
        pdf.set_xy(pdf.l_margin, start_y + row_height)
    pdf.ln(5)

def generate_pdf_file():
    try:
        logging.debug("Début génération PDF")
        pdf = PDF('L', 'mm', 'A4')
        pdf.add_font('DejaVu', '', r'C:\Windows\Fonts\DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', r'C:\Windows\Fonts\DejaVuSans-Bold.ttf', uni=True)
        pdf.add_font('DejaVu', 'I', r'C:\Windows\Fonts\DejaVuSans-Oblique.ttf', uni=True)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        postes = ["Gardien", "DC", "DG", "DL", "MDF", "MC", "Ailier/AC", "AC", "MO"]
        for poste in postes:
            data_poste = [row for row in effectif if poste in row[1]]
            if data_poste:
                add_table(pdf, f"{poste}s", headers, data_poste)

        pdf_path = os.path.join(pdf_folder, pdf_filename)
        pdf.output(pdf_path)
        logging.debug(f"PDF généré : {pdf_path}")
        messagebox.showinfo("Succès", f"PDF généré :\n{pdf_path}")
    except Exception as e:
        logging.exception("Erreur génération PDF")
        messagebox.showerror("Erreur", str(e))

# -----------------------------
# Édition interactive type Excel
# -----------------------------
def view_edit_composition():
    edit_win = tk.Toplevel(root)
    edit_win.title("Édition de la composition")
    edit_win.geometry("1200x700")
    edit_win.minsize(1000, 600)

    container = ttk.Frame(edit_win, padding=12)
    container.pack(fill="both", expand=True)

    title = ttk.Label(container, text="Gestion de l'effectif", style="Header.TLabel")
    title.pack(anchor="w", pady=(0, 10))

    panes = ttk.Panedwindow(container, orient="horizontal")
    panes.pack(fill="both", expand=True)

    table_frame = ttk.Frame(panes)
    form_frame = ttk.Frame(panes, padding=(16, 0, 0, 0))
    panes.add(table_frame, weight=3)
    panes.add(form_frame, weight=2)

    tree = ttk.Treeview(table_frame, columns=headers, show='headings')
    for h in headers:
        tree.heading(h, text=h)
        tree.column(h, width=150, anchor="center", stretch=True)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    for row in effectif:
        tree.insert("", "end", values=row)

    form_title = ttk.Label(form_frame, text="Fiche joueur", style="Section.TLabel")
    form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

    entries = {}
    for idx, header in enumerate(headers, start=1):
        label = ttk.Label(form_frame, text=header)
        label.grid(row=idx, column=0, sticky="w", pady=4)
        entry = ttk.Entry(form_frame)
        entry.grid(row=idx, column=1, sticky="ew", pady=4)
        entries[header] = entry

    form_frame.columnconfigure(1, weight=1)

    def clear_form():
        for entry in entries.values():
            entry.delete(0, tk.END)

    def populate_form(event=None):
        selection = tree.selection()
        if not selection:
            return
        values = tree.item(selection[0], "values")
        for header, value in zip(headers, values):
            entry = entries[header]
            entry.delete(0, tk.END)
            entry.insert(0, value)

    tree.bind("<<TreeviewSelect>>", populate_form)

    def save_changes():
        global effectif
        effectif = [list(tree.item(item)['values']) for item in tree.get_children()]
        with open(composition_file, "w", encoding="utf-8") as f:
            json.dump(effectif, f, ensure_ascii=False, indent=2)
        logging.debug("Composition sauvegardée")
        messagebox.showinfo("Succès", "Composition sauvegardée !")

    def add_player():
        values = [entries[header].get().strip() for header in headers]
        if not any(values):
            messagebox.showwarning("Données manquantes", "Veuillez renseigner au moins un champ.")
            return
        tree.insert("", "end", values=values)
        clear_form()

    def update_player():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Sélection manquante", "Sélectionnez un joueur à modifier.")
            return
        values = [entries[header].get().strip() for header in headers]
        tree.item(selection[0], values=values)

    def delete_player():
        for item in tree.selection():
            tree.delete(item)

    btn_group = ttk.Frame(form_frame)
    btn_group.grid(row=len(headers) + 1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
    btn_group.columnconfigure(0, weight=1)

    ttk.Button(btn_group, text="Ajouter", command=add_player).grid(row=0, column=0, sticky="ew", pady=4)
    ttk.Button(btn_group, text="Mettre à jour", command=update_player).grid(row=1, column=0, sticky="ew", pady=4)
    ttk.Button(btn_group, text="Effacer la sélection", command=delete_player).grid(row=2, column=0, sticky="ew", pady=4)
    ttk.Button(btn_group, text="Réinitialiser le formulaire", command=clear_form).grid(row=3, column=0, sticky="ew", pady=4)

    footer = ttk.Frame(container)
    footer.pack(fill="x", pady=(12, 0))
    ttk.Button(footer, text="Sauvegarder", command=save_changes).pack(side="right")

# -----------------------------
# Interface principale
# -----------------------------
root = tk.Tk()
root.title(f"{settings['club_name']} Dashboard")
root.geometry("980x700")
root.minsize(880, 620)
root.configure(bg="#F4F6FA")

style = ttk.Style(root)
style.theme_use("clam")

themes = {
    "Azur & Or": {
        "bg": "#F3F6FF",
        "card": "#FFFFFF",
        "primary": "#0D3B66",
        "accent": "#F4D35E",
        "text": "#1A1F2B",
        "muted": "#5A6B82",
        "button": "#0D3B66",
        "button_text": "#FFFFFF"
    },
    "Soleil & Mer": {
        "bg": "#FFF8F0",
        "card": "#FFFFFF",
        "primary": "#FF7A00",
        "accent": "#4CB7FF",
        "text": "#2B2B2B",
        "muted": "#6B7280",
        "button": "#FF7A00",
        "button_text": "#FFFFFF"
    },
    "Émeraude Nuit": {
        "bg": "#F1F7F4",
        "card": "#FFFFFF",
        "primary": "#0F766E",
        "accent": "#134E4A",
        "text": "#0F172A",
        "muted": "#64748B",
        "button": "#0F766E",
        "button_text": "#FFFFFF"
    },
    "Lavande Moderne": {
        "bg": "#F7F4FF",
        "card": "#FFFFFF",
        "primary": "#6D28D9",
        "accent": "#F59E0B",
        "text": "#1F2937",
        "muted": "#6B7280",
        "button": "#6D28D9",
        "button_text": "#FFFFFF"
    },
    "Ardoise & Cuivre": {
        "bg": "#F3F4F6",
        "card": "#FFFFFF",
        "primary": "#374151",
        "accent": "#D97706",
        "text": "#111827",
        "muted": "#6B7280",
        "button": "#374151",
        "button_text": "#FFFFFF"
    },
    "Rosé Sport": {
        "bg": "#FFF1F2",
        "card": "#FFFFFF",
        "primary": "#BE123C",
        "accent": "#EC4899",
        "text": "#1F2937",
        "muted": "#6B7280",
        "button": "#BE123C",
        "button_text": "#FFFFFF"
    },
    "Forêt & Sable": {
        "bg": "#F6F4EF",
        "card": "#FFFFFF",
        "primary": "#2F5D50",
        "accent": "#C9A66B",
        "text": "#1E293B",
        "muted": "#6B7280",
        "button": "#2F5D50",
        "button_text": "#FFFFFF"
    },
    "Tech Indigo": {
        "bg": "#EEF2FF",
        "card": "#FFFFFF",
        "primary": "#4338CA",
        "accent": "#22D3EE",
        "text": "#1E1B4B",
        "muted": "#64748B",
        "button": "#4338CA",
        "button_text": "#FFFFFF"
    },
    "Menthe & Graphite": {
        "bg": "#F0FDFA",
        "card": "#FFFFFF",
        "primary": "#0F172A",
        "accent": "#2DD4BF",
        "text": "#0F172A",
        "muted": "#64748B",
        "button": "#0F172A",
        "button_text": "#FFFFFF"
    },
    "Rouge Urbain": {
        "bg": "#FFF5F5",
        "card": "#FFFFFF",
        "primary": "#B91C1C",
        "accent": "#F97316",
        "text": "#1F2937",
        "muted": "#6B7280",
        "button": "#B91C1C",
        "button_text": "#FFFFFF"
    },
    "Océan Profond": {
        "bg": "#EFF6FF",
        "card": "#FFFFFF",
        "primary": "#1E3A8A",
        "accent": "#38BDF8",
        "text": "#0F172A",
        "muted": "#64748B",
        "button": "#1E3A8A",
        "button_text": "#FFFFFF"
    },
    "Citrus Graphique": {
        "bg": "#FFFBEB",
        "card": "#FFFFFF",
        "primary": "#B45309",
        "accent": "#65A30D",
        "text": "#1F2937",
        "muted": "#6B7280",
        "button": "#B45309",
        "button_text": "#FFFFFF"
    }
}

def apply_theme(theme_name):
    palette = themes.get(theme_name, themes["Azur & Or"])
    root.configure(bg=palette["bg"])
    style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), background=palette["bg"], foreground=palette["primary"])
    style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), background=palette["card"], foreground=palette["primary"])
    style.configure("TLabel", background=palette["bg"], foreground=palette["text"])
    style.configure("Muted.TLabel", background=palette["card"], foreground=palette["muted"])
    style.configure("TButton", font=("Segoe UI", 10), padding=8, background=palette["button"], foreground=palette["button_text"])
    style.map("TButton", background=[("active", palette["accent"])], foreground=[("active", palette["text"])])
    style.configure("Card.TFrame", background=palette["card"])
    style.configure("CardTitle.TLabel", background=palette["card"], font=("Segoe UI", 11, "bold"), foreground=palette["primary"])
    style.configure("TEntry", fieldbackground="#FFFFFF", background=palette["card"], foreground=palette["text"])
    style.configure("TCombobox", fieldbackground="#FFFFFF", background=palette["card"], foreground=palette["text"])
    style.configure("TFrame", background=palette["bg"])
    settings["theme"] = theme_name
    save_settings()

def save_settings():
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        logging.debug("Paramètres sauvegardés")
    except Exception as e:
        logging.error(f"Erreur sauvegarde settings : {e}")

main = ttk.Frame(root, padding=22)
main.pack(fill="both", expand=True)

header = ttk.Label(main, text=f"{settings['club_name']} - Gestion d'effectif", style="Header.TLabel")
header.pack(anchor="w", pady=(0, 16))

settings_card = ttk.Frame(main, style="Card.TFrame", padding=16)
settings_card.pack(fill="x", pady=(0, 16))
ttk.Label(settings_card, text="Paramètres du club", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

settings_grid = ttk.Frame(settings_card)
settings_grid.pack(fill="x")
settings_grid.columnconfigure(1, weight=1)
settings_grid.columnconfigure(3, weight=1)

club_var = tk.StringVar(value=settings["club_name"])
season_var = tk.StringVar(value=settings["season"])
theme_var = tk.StringVar(value=settings["theme"])

ttk.Label(settings_grid, text="Nom du club").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
club_entry = ttk.Entry(settings_grid, textvariable=club_var)
club_entry.grid(row=0, column=1, sticky="ew", pady=4)

ttk.Label(settings_grid, text="Saison").grid(row=0, column=2, sticky="w", padx=(16, 8), pady=4)
season_entry = ttk.Entry(settings_grid, textvariable=season_var)
season_entry.grid(row=0, column=3, sticky="ew", pady=4)

ttk.Label(settings_grid, text="Thème").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
theme_box = ttk.Combobox(settings_grid, textvariable=theme_var, values=sorted(themes.keys()), state="readonly")
theme_box.grid(row=1, column=1, sticky="w", pady=4)

def refresh_status():
    lbl_folder.config(text=f"Dossier PDF : {pdf_folder}")
    lbl_filename.config(text=f"Nom PDF : {pdf_filename}")
    lbl_club.config(text=f"Club : {settings['club_name']}")
    lbl_season.config(text=f"Saison : {settings['season']}")

def update_club_settings():
    settings["club_name"] = club_var.get().strip() or default_settings["club_name"]
    settings["season"] = season_var.get().strip() or default_settings["season"]
    header.config(text=f"{settings['club_name']} - Gestion d'effectif")
    root.title(f"{settings['club_name']} Dashboard")
    refresh_status()
    save_settings()

def on_theme_change(event=None):
    apply_theme(theme_var.get())

theme_box.bind("<<ComboboxSelected>>", on_theme_change)

ttk.Button(settings_grid, text="Appliquer", command=update_club_settings).grid(row=1, column=3, sticky="e", pady=4)

card = ttk.Frame(main, style="Card.TFrame", padding=16)
card.pack(fill="x", pady=(0, 16))

card_title = ttk.Label(card, text="Actions rapides", style="CardTitle.TLabel")
card_title.pack(anchor="w", pady=(0, 8))

actions = ttk.Frame(card)
actions.pack(fill="x")
actions.columnconfigure(0, weight=1)
actions.columnconfigure(1, weight=1)

ttk.Button(actions, text="Générer le PDF", command=generate_pdf_file).grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=6)
ttk.Button(actions, text="Sélectionner un dossier", command=lambda: select_folder()).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=6)
ttk.Button(actions, text="Nommer le PDF", command=lambda: set_filename()).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=6)
ttk.Button(actions, text="Éditer la composition", command=view_edit_composition).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=6)

status_card = ttk.Frame(main, style="Card.TFrame", padding=16)
status_card.pack(fill="x", pady=(0, 16))
ttk.Label(status_card, text="Paramètres actuels", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
lbl_folder = ttk.Label(status_card, text=f"Dossier PDF : {pdf_folder}")
lbl_folder.pack(anchor="w")
lbl_filename = ttk.Label(status_card, text=f"Nom PDF : {pdf_filename}")
lbl_filename.pack(anchor="w", pady=(4, 0))
lbl_club = ttk.Label(status_card, text=f"Club : {settings['club_name']}")
lbl_club.pack(anchor="w", pady=(4, 0))
lbl_season = ttk.Label(status_card, text=f"Saison : {settings['season']}")
lbl_season.pack(anchor="w")

footer = ttk.Frame(main)
footer.pack(fill="x")
ttk.Button(footer, text="Quitter", command=root.destroy).pack(side="right")

# -----------------------------
# Fonctions PDF / nom du fichier / dossier
# -----------------------------
def select_folder():
    global pdf_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        pdf_folder = folder_selected
        lbl_folder.config(text=f"Dossier PDF : {pdf_folder}")
        logging.debug(f"Dossier PDF sélectionné : {pdf_folder}")

def set_filename():
    global pdf_filename
    name = simpledialog.askstring("Nom du PDF", "Entrez le nom du fichier PDF :")
    if name:
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        pdf_filename = name
        lbl_filename.config(text=f"Nom PDF : {pdf_filename}")
        logging.debug(f"Nom PDF défini : {pdf_filename}")

apply_theme(settings["theme"])
refresh_status()

root.mainloop()
