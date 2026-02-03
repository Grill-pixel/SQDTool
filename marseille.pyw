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
        self.cell(0, 10, 'Olympique de Marseille 2025-2026', 0, 1, 'C', 1)
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
root.title("OM Dashboard")
root.geometry("900x620")
root.minsize(820, 560)
root.configure(bg="#F4F6FA")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background="#F4F6FA", foreground="#002B5B")
style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"))
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("Card.TFrame", background="white")
style.configure("CardTitle.TLabel", background="white", font=("Segoe UI", 11, "bold"))

main = ttk.Frame(root, padding=20)
main.pack(fill="both", expand=True)

header = ttk.Label(main, text="Olympique de Marseille - Gestion d'effectif", style="Header.TLabel")
header.pack(anchor="w", pady=(0, 16))

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

root.mainloop()
