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

def add_table(pdf, title, headers, data):
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(0, 10, title, 0, 1, 'L', 1)
    pdf.set_font('DejaVu', 'B', 10)

    # Largeur adaptable des colonnes selon contenu
    col_widths = []
    for i, h in enumerate(headers):
        max_len = max(len(str(row[i])) for row in data) if data else 0
        col_widths.append(max(40, min(180, max_len*6)))

    for w, header in zip(col_widths, headers):
        pdf.cell(w, 8, header, 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font('DejaVu', '', 10)
    for row in data:
        for w, item in zip(col_widths, row):
            pdf.cell(w, 8, str(item), 1, 0, 'C')
        pdf.ln()
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
    edit_win.geometry("1200x600")

    tree = ttk.Treeview(edit_win, columns=headers, show='headings')
    for h in headers:
        tree.heading(h, text=h)
        tree.column(h, width=160, anchor="center")
    tree.pack(fill="both", expand=True, side="left")

    vsb = ttk.Scrollbar(edit_win, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    for row in effectif:
        tree.insert("", "end", values=row)

    # Édition directe cellule
    def edit_cell(event):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        x, y, width, height = tree.bbox(row_id, col)
        col_index = int(col.replace("#", "")) - 1
        value = tree.set(row_id, headers[col_index])

        entry = tk.Entry(tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event=None):
            tree.set(row_id, headers[col_index], entry.get())
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    tree.bind("<Double-1>", edit_cell)

    # Boutons
    btn_frame = tk.Frame(edit_win)
    btn_frame.pack(pady=10)

    def save_changes():
        global effectif
        effectif = [list(tree.item(item)['values']) for item in tree.get_children()]
        with open(composition_file, "w", encoding="utf-8") as f:
            json.dump(effectif, f, ensure_ascii=False, indent=2)
        logging.debug("Composition sauvegardée")
        messagebox.showinfo("Succès", "Composition sauvegardée !")

    def add_player():
        tree.insert("", "end", values=[""]*len(headers))

    def delete_player():
        for item in tree.selection():
            tree.delete(item)

    tk.Button(btn_frame, text="Sauvegarder", command=save_changes, bg="#00CC66", width=15).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Ajouter joueur", command=add_player, bg="#3399FF", width=15).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Supprimer joueur", command=delete_player, bg="#CC3333", width=15).pack(side="left", padx=5)

# -----------------------------
# Interface principale
# -----------------------------
root = tk.Tk()
root.title("OM Dashboard")
root.geometry("700x500")
root.resizable(False, False)

tk.Button(root, text="Générer PDF", command=generate_pdf_file, width=35, height=2, bg="#003366", fg="white").pack(pady=10)
tk.Button(root, text="Sélectionner dossier", command=lambda: select_folder(), width=35, height=2, bg="#0066CC", fg="white").pack(pady=5)
tk.Button(root, text="Nom du PDF", command=lambda: set_filename(), width=35, height=2, bg="#3399FF", fg="white").pack(pady=5)
tk.Button(root, text="Visualiser / Éditer composition", command=view_edit_composition, width=35, height=2, bg="#00CC66", fg="white").pack(pady=5)
tk.Button(root, text="Quitter", command=root.destroy, width=35, height=2, bg="#990000", fg="white").pack(pady=5)

lbl_folder = tk.Label(root, text=f"Dossier PDF : {pdf_folder}", fg="black")
lbl_folder.pack(pady=5)
lbl_filename = tk.Label(root, text=f"Nom PDF : {pdf_filename}", fg="black")
lbl_filename.pack(pady=5)

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
