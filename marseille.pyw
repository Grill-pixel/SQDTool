import os
import sys
import logging
import json
import subprocess
import re
import tempfile
import time
import importlib.util
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

PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None
ImageGrab = None
if PIL_AVAILABLE:
    from PIL import Image, ImageGrab

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
default_composition = os.path.join(os.path.dirname(__file__), "composition.json")
legacy_composition = os.path.join(os.path.dirname(__file__), "effectifOM.json")
composition_file = legacy_composition if os.path.exists(legacy_composition) else default_composition
settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
disposition_state_file = os.path.join(os.path.dirname(__file__), "disposition_layout.json")
edit_window = None
disposition_window = None
disposition_exporter = None
PDF_FONT_FAMILY = "DejaVu"

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

formations = {
    "4-4-2": [4, 4, 2],
    "4-3-3": [4, 3, 3],
    "4-2-3-1": [4, 2, 3, 1],
    "4-1-4-1": [4, 1, 4, 1],
    "4-5-1": [4, 5, 1],
    "3-5-2": [3, 5, 2],
    "3-4-3": [3, 4, 3],
    "5-3-2": [5, 3, 2],
    "5-4-1": [5, 4, 1]
}

def normalize_effectif(data):
    def build_row(entry):
        if isinstance(entry, (list, tuple)):
            row = [str(value) for value in entry]
            if len(row) < len(headers):
                row += [""] * (len(headers) - len(row))
            return row[:len(headers)]
        if isinstance(entry, dict):
            joueur = entry.get("joueur") or entry.get("name") or entry.get("nom") or ""
            poste = entry.get("poste_principal") or entry.get("poste") or ""
            age = entry.get("age", "")
            nationalite = entry.get("nationalite") or entry.get("nationalité") or ""
            statut = entry.get("statut") or ""
            option = entry.get("option_achat") or entry.get("option d’achat") or entry.get("option") or ""
            return [str(joueur), str(poste), str(age), str(nationalite), str(statut), str(option)]
        return None

    if isinstance(data, list):
        rows = []
        for entry in data:
            row = build_row(entry)
            if row:
                rows.append(row)
        return rows

    if isinstance(data, dict):
        rows = []
        for key, entries in data.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    row = build_row(entry)
                    if row:
                        rows.append(row)
                    continue
                row = build_row(entry)
                if row:
                    if key == "prets_sortants":
                        club = entry.get("club_pret") or ""
                        fin = entry.get("fin_pret") or ""
                        row[3] = row[3] or ""
                        row[4] = row[4] or f"Prêt sortant : {club} ({fin})".strip()
                    rows.append(row)
        return rows
    return []


def safe_cell(row, index, default=""):
    if isinstance(row, (list, tuple)) and len(row) > index:
        return row[index]
    return default


def load_effectif_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    normalized = normalize_effectif(data)
    if not normalized:
        raise ValueError("Composition vide ou format non reconnu.")
    return normalized


def load_disposition_state():
    if not os.path.exists(disposition_state_file):
        return {"player_overrides_by_formation": {}, "slot_offsets_by_formation": {}}
    try:
        with open(disposition_state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        player_overrides = data.get("player_overrides_by_formation", {}) or {}
        slot_offsets = data.get("slot_offsets_by_formation", {}) or {}
        cleaned_offsets = {}
        for formation, offsets in slot_offsets.items():
            if not isinstance(offsets, dict):
                continue
            cleaned_offsets[formation] = {
                slot_id: tuple(value) for slot_id, value in offsets.items()
                if isinstance(value, (list, tuple)) and len(value) == 2
            }
        return {
            "player_overrides_by_formation": player_overrides,
            "slot_offsets_by_formation": cleaned_offsets
        }
    except Exception as e:
        logging.error(f"Erreur chargement disposition : {e}")
        return {"player_overrides_by_formation": {}, "slot_offsets_by_formation": {}}


def save_disposition_state(player_overrides, slot_offsets):
    try:
        serialized_offsets = {}
        for formation, offsets in slot_offsets.items():
            if not isinstance(offsets, dict):
                continue
            serialized_offsets[formation] = {
                slot_id: list(value) for slot_id, value in offsets.items()
            }
        payload = {
            "player_overrides_by_formation": player_overrides,
            "slot_offsets_by_formation": serialized_offsets
        }
        with open(disposition_state_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logging.debug(f"Disposition sauvegardée : {disposition_state_file}")
        return True
    except Exception as e:
        logging.error(f"Erreur sauvegarde disposition : {e}")
        return False


def normalize_poste_text(value):
    if not value:
        return ""
    text = str(value).lower()
    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
        "‑": "-",
        "–": "-",
    }
    return "".join(replacements.get(char, char) for char in text)


def map_poste_to_role(poste):
    poste_lower = normalize_poste_text(poste)
    if "gardien" in poste_lower or "goal" in poste_lower:
        return "GK"
    if "defenseur" in poste_lower or "arriere" in poste_lower:
        if "central" in poste_lower or "axe" in poste_lower or "axial" in poste_lower or "dc" in poste_lower:
            return "CB"
        if "gauche" in poste_lower or "dg" in poste_lower:
            return "LB"
        if "droit" in poste_lower or "dl" in poste_lower:
            return "RB"
    if "lateral" in poste_lower:
        if "gauche" in poste_lower or "dg" in poste_lower:
            return "LB"
        if "droit" in poste_lower or "dl" in poste_lower:
            return "RB"
    if "milieu" in poste_lower or "mid" in poste_lower:
        if "defensif" in poste_lower or "sentinelle" in poste_lower or "mdf" in poste_lower:
            return "DM"
        if "offensif" in poste_lower or "meneur" in poste_lower or "mo" in poste_lower:
            return "AM"
        if "central" in poste_lower or "relayeur" in poste_lower or "mc" in poste_lower:
            return "CM"
    if "ailier" in poste_lower or "exterieur" in poste_lower or "couloir" in poste_lower:
        return "W"
    if "avant" in poste_lower or "attaquant" in poste_lower or "buteur" in poste_lower or "neuf" in poste_lower or "ac" in poste_lower:
        return "ST"
    return "OTHER"


def line_positions(count, padding=0.1):
    if count <= 1:
        return [0.5]
    step = (1 - 2 * padding) / (count - 1)
    return [padding + step * idx for idx in range(count)]


def line_positions_for_line(count, line_type):
    if line_type in {"att", "am"}:
        if count == 2:
            return [0.42, 0.58]
        if count == 3:
            return [0.25, 0.5, 0.75]
        return line_positions(count, padding=0.2)
    if line_type == "dm":
        return line_positions(count, padding=0.2)
    if line_type == "def":
        return line_positions(count, padding=0.08)
    return line_positions(count, padding=0.12)


def roles_for_line(count, line_type):
    if line_type == "def":
        if count == 5:
            return ["LB", "CB", "CB", "CB", "RB"]
        if count == 4:
            return ["LB", "CB", "CB", "RB"]
        if count == 3:
            return ["CB", "CB", "CB"]
        return ["CB"] * count
    if line_type == "mid":
        if count == 5:
            return ["LM", "CM", "CM", "CM", "RM"]
        if count == 4:
            return ["LM", "CM", "CM", "RM"]
        if count == 3:
            return ["CM", "CM", "CM"]
        return ["CM"] * count
    if line_type == "dm":
        return ["DM"] * count
    if line_type == "am":
        if count == 3:
            return ["LW", "AM", "RW"]
        if count == 2:
            return ["AM", "AM"]
        return ["AM"] * count
    if line_type == "att":
        if count == 3:
            return ["LW", "ST", "RW"]
        if count == 2:
            return ["ST", "ST"]
        return ["ST"] * count
    return ["CM"] * count


def build_formation_slots(formation_key):
    counts = formations.get(formation_key, [4, 4, 2])
    slots = [{"id": "slot-0", "role": "GK", "x": 0.5, "y": 0.1}]
    if len(counts) == 3:
        line_types = ["def", "mid", "att"]
        y_values = [0.28, 0.55, 0.82]
    elif len(counts) == 4:
        line_types = ["def", "dm", "am", "att"]
        y_values = [0.26, 0.45, 0.65, 0.84]
    else:
        line_types = ["def", "mid", "att"]
        y_values = [0.28, 0.55, 0.82]

    for count, line_type, y in zip(counts, line_types, y_values):
        roles = roles_for_line(count, line_type)
        xs = line_positions_for_line(count, line_type)
        for role, x in zip(roles, xs):
            slots.append({"id": f"slot-{len(slots)}", "role": role, "x": x, "y": y})
    return slots


def candidate_roles_for_slot(slot_role):
    if slot_role == "GK":
        return ["GK"]
    if slot_role == "CB":
        return ["CB"]
    if slot_role == "LB":
        return ["LB", "CB"]
    if slot_role == "RB":
        return ["RB", "CB"]
    if slot_role in {"LM", "RM"}:
        return ["W", "CM", "AM"]
    if slot_role == "CM":
        return ["CM", "DM", "AM"]
    if slot_role == "DM":
        return ["DM", "CM"]
    if slot_role == "AM":
        return ["AM", "CM", "W"]
    if slot_role in {"LW", "RW"}:
        return ["W", "ST", "AM"]
    if slot_role == "ST":
        return ["ST", "W"]
    return ["CM", "AM", "W", "ST"]


def slot_roles_for_player(player_role):
    if player_role == "GK":
        return ["GK"]
    if player_role == "CB":
        return ["CB", "LB", "RB"]
    if player_role == "LB":
        return ["LB", "CB"]
    if player_role == "RB":
        return ["RB", "CB"]
    if player_role == "DM":
        return ["DM", "CM"]
    if player_role == "CM":
        return ["CM", "DM", "AM"]
    if player_role == "AM":
        return ["AM", "CM", "LW", "RW"]
    if player_role == "W":
        return ["LW", "RW", "LM", "RM", "ST", "AM"]
    if player_role == "ST":
        return ["ST", "LW", "RW"]
    return ["CM", "AM", "ST", "LW", "RW"]


def assign_players_to_slots(slots, players, player_overrides=None):
    overrides = player_overrides or {}
    players_by_role = {}
    for row in players:
        if not row:
            continue
        name = str(safe_cell(row, 0)).strip()
        poste = str(safe_cell(row, 1)).strip()
        if not name:
            continue
        role = map_poste_to_role(poste)
        players_by_role.setdefault(role, []).append(name)

    assignments = [[] for _ in slots]
    slot_id_to_index = {slot["id"]: idx for idx, slot in enumerate(slots)}

    for name, slot_id in overrides.items():
        idx = slot_id_to_index.get(slot_id)
        if idx is None:
            continue
        for role, names in players_by_role.items():
            if name in names:
                names.remove(name)
                break
        assignments[idx].append(name)

    for idx, slot in enumerate(slots):
        for role in candidate_roles_for_slot(slot["role"]):
            if players_by_role.get(role):
                assignments[idx].append(players_by_role[role].pop(0))
                break

    leftovers = []
    for role, names in players_by_role.items():
        for name in names:
            leftovers.append((role, name))

    for role, name in leftovers:
        compatible = slot_roles_for_player(role)
        candidate_indices = [
            idx for idx, slot in enumerate(slots)
            if slot["role"] in compatible
        ]
        if not candidate_indices:
            continue
        best_index = min(candidate_indices, key=lambda idx: len(assignments[idx]))
        assignments[best_index].append(name)

    return assignments


# Charger composition sauvegardée si existante
if os.path.exists(composition_file):
    try:
        effectif = load_effectif_from_file(composition_file)
        logging.debug("Composition chargée depuis fichier JSON")
    except Exception as e:
        logging.error(f"Erreur chargement composition : {e}")

# -----------------------------
# PDF UTF-8 avec FPDF2
# -----------------------------
class PDF(FPDF):
    def header(self):
        self.set_font(PDF_FONT_FAMILY, 'B', 16)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"{settings['club_name']} {settings['season']}", 0, 1, 'C', 1)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(PDF_FONT_FAMILY, 'I', 8)
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
            cell = row[i] if isinstance(row, (list, tuple)) and len(row) > i else ""
            max_width = max(max_width, pdf.get_string_width(str(cell)))
        widths.append(max_width + padding)
    total = sum(widths)
    available = pdf.w - pdf.l_margin - pdf.r_margin
    if total > available:
        scale = available / total
        widths = [max(min_width, width * scale) for width in widths]
    return widths


def add_table(pdf, title, headers, data):
    pdf.set_font(PDF_FONT_FAMILY, 'B', 12)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(0, 10, title, 0, 1, 'L', 1)
    col_widths = compute_column_widths(pdf, headers, data)

    def render_header():
        pdf.set_font(PDF_FONT_FAMILY, 'B', 10)
        for w, header in zip(col_widths, headers):
            pdf.cell(w, 8, header, 1, 0, 'C', 1)
        pdf.ln()

    render_header()
    pdf.set_font(PDF_FONT_FAMILY, '', 10)
    line_height = pdf.font_size * 1.6
    for row in data:
        wrapped_cells = [wrap_text(pdf, item, width) for item, width in zip(row, col_widths)]
        max_lines = max(len(lines) for lines in wrapped_cells)
        row_height = line_height * max_lines
        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            render_header()
        start_x = pdf.l_margin
        start_y = pdf.get_y()
        for width, lines in zip(col_widths, wrapped_cells):
            pdf.set_xy(start_x, start_y)
            pdf.multi_cell(width, line_height, "\n".join(lines), border=1, align='C')
            start_x += width
        pdf.set_xy(pdf.l_margin, start_y + row_height)
    pdf.ln(5)

def extract_contract_end(statut_text):
    if not statut_text:
        return ""
    text = str(statut_text)
    match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
    if match:
        return match.group(0)
    match = re.search(r"\b20\d{2}\b", text)
    if match:
        return match.group(0)
    return ""


def build_composition_rows():
    rows = []
    for row in effectif:
        if not row:
            continue
        joueur = safe_cell(row, 0)
        poste = safe_cell(row, 1)
        age = safe_cell(row, 2)
        nationalite = safe_cell(row, 3)
        statut = safe_cell(row, 4)
        clause = safe_cell(row, 5)
        fin_contrat = extract_contract_end(statut)
        rows.append([joueur, poste, age, nationalite, statut, clause, fin_contrat])
    return rows


def find_font_file(paths):
    for path in paths:
        if path and os.path.exists(path):
            return path
    return None


def resolve_font_paths():
    font_dirs = [
        r"C:\Windows\Fonts",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/local/share/fonts",
        "/Library/Fonts",
        "/System/Library/Fonts/Supplemental"
    ]
    regular_candidates = [
        os.path.join(directory, "DejaVuSans.ttf") for directory in font_dirs
    ]
    bold_candidates = [
        os.path.join(directory, "DejaVuSans-Bold.ttf") for directory in font_dirs
    ]
    italic_candidates = [
        os.path.join(directory, "DejaVuSans-Oblique.ttf") for directory in font_dirs
    ]
    regular = find_font_file(regular_candidates)
    bold = find_font_file(bold_candidates)
    italic = find_font_file(italic_candidates)
    if regular and not bold:
        bold = regular
    if regular and not italic:
        italic = regular
    return {"regular": regular, "bold": bold, "italic": italic}


def generate_composition_pdf():
    global PDF_FONT_FAMILY
    try:
        logging.debug("Début génération PDF composition")
        pdf = PDF('L', 'mm', 'A4')
        font_paths = resolve_font_paths()
        if font_paths["regular"]:
            pdf.add_font('DejaVu', '', font_paths["regular"], uni=True)
            pdf.add_font('DejaVu', 'B', font_paths["bold"], uni=True)
            pdf.add_font('DejaVu', 'I', font_paths["italic"], uni=True)
            PDF_FONT_FAMILY = "DejaVu"
        else:
            PDF_FONT_FAMILY = "Helvetica"
            logging.warning("Police DejaVu introuvable, utilisation d'Helvetica (UTF-8 limité).")
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        composition_headers = [
            "Joueur",
            "Poste",
            "Âge",
            "Nationalité",
            "Type de contrat",
            "Type de clause",
            "Fin de contrat"
        ]
        data = build_composition_rows()
        add_table(pdf, "Composition de l'équipe", composition_headers, data)

        pdf_path = os.path.join(pdf_folder, pdf_filename)
        pdf.output(pdf_path)
        logging.debug(f"PDF composition généré : {pdf_path}")
        messagebox.showinfo("Succès", f"PDF composition généré :\n{pdf_path}")
    except Exception as e:
        logging.exception("Erreur génération PDF composition")
        messagebox.showerror("Erreur", str(e))

# -----------------------------
# Édition interactive type Excel
# -----------------------------
def view_edit_composition():
    global edit_window
    if edit_window is not None and edit_window.winfo_exists():
        edit_window.lift()
        edit_window.focus_force()
        return
    edit_win = tk.Toplevel(root)
    edit_window = edit_win
    edit_win.title("Édition de la composition")
    edit_win.geometry("1200x700")
    edit_win.minsize(1000, 600)
    edit_win.configure(bg=get_palette()["bg"])

    def handle_close():
        global edit_window
        if edit_window is not None:
            edit_window.destroy()
        edit_window = None

    edit_win.protocol("WM_DELETE_WINDOW", handle_close)

    container = ttk.Frame(edit_win, padding=16)
    container.pack(fill="both", expand=True)

    header_frame = ttk.Frame(container)
    header_frame.pack(fill="x", pady=(0, 12))

    title = ttk.Label(header_frame, text="Gestion de l'effectif", style="Header.TLabel")
    title.pack(anchor="w")
    subtitle = ttk.Label(
        header_frame,
        text="Ajoute, modifie ou filtre les joueurs pour garder la composition toujours à jour.",
        style="Subheader.TLabel"
    )
    subtitle.pack(anchor="w", pady=(4, 0))

    toolbar = ttk.Frame(container)
    toolbar.pack(fill="x", pady=(0, 12))
    toolbar.columnconfigure(1, weight=1)

    ttk.Label(toolbar, text="Recherche rapide").grid(row=0, column=0, sticky="w", padx=(0, 10))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(toolbar, textvariable=search_var)
    search_entry.grid(row=0, column=1, sticky="ew")

    status_var = tk.StringVar(value="0 joueurs")
    status_label = ttk.Label(toolbar, textvariable=status_var, style="Muted.TLabel")
    status_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

    panes = ttk.Panedwindow(container, orient="horizontal")
    panes.pack(fill="both", expand=True)

    table_wrapper = ttk.Labelframe(panes, text="Tableau effectif")
    form_frame = ttk.Labelframe(panes, text="Fiche joueur", padding=(12, 8))
    panes.add(table_wrapper, weight=3)
    panes.add(form_frame, weight=2)

    table_frame = ttk.Frame(table_wrapper)
    table_frame.pack(fill="both", expand=True, padx=8, pady=8)

    tree = ttk.Treeview(table_frame, columns=headers, show='headings', style="Treeview")
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

    entries = {}
    for idx, header in enumerate(headers, start=0):
        label = ttk.Label(form_frame, text=header)
        label.grid(row=idx, column=0, sticky="w", pady=6)
        entry = ttk.Entry(form_frame)
        entry.grid(row=idx, column=1, sticky="ew", pady=6)
        entries[header] = entry

    form_frame.columnconfigure(1, weight=1)

    all_rows = [list(row) for row in effectif]

    def refresh_tree(rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)
        status_var.set(f"{len(rows)} joueurs")

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
        global effectif, composition_file
        effectif = [list(row) for row in all_rows]
        save_path = filedialog.asksaveasfilename(
            title="Enregistrer la composition",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if not save_path:
            return
        composition_file = save_path
        with open(composition_file, "w", encoding="utf-8") as f:
            json.dump(effectif, f, ensure_ascii=False, indent=2)
        logging.debug(f"Composition sauvegardée : {composition_file}")
        messagebox.showinfo("Succès", f"Composition sauvegardée :\n{composition_file}")

    def load_composition():
        global effectif, composition_file
        load_path = filedialog.askopenfilename(
            title="Charger une composition",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if not load_path:
            return
        try:
            effectif = load_effectif_from_file(load_path)
            composition_file = load_path
            all_rows.clear()
            all_rows.extend([list(row) for row in effectif])
            refresh_tree(all_rows)
            clear_form()
            logging.debug(f"Composition chargée : {composition_file}")
            messagebox.showinfo("Succès", f"Composition chargée :\n{composition_file}")
        except Exception as e:
            logging.exception("Erreur chargement composition")
            messagebox.showerror("Erreur", str(e))

    def add_player():
        values = [entries[header].get().strip() for header in headers]
        if not any(values):
            messagebox.showwarning("Données manquantes", "Veuillez renseigner au moins un champ.")
            return
        all_rows.append(values)
        refresh_tree(all_rows)
        clear_form()

    def update_player():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Sélection manquante", "Sélectionnez un joueur à modifier.")
            return
        values = [entries[header].get().strip() for header in headers]
        selected_values = list(tree.item(selection[0], "values"))
        updated = False
        for index, row in enumerate(all_rows):
            if list(row) == selected_values:
                all_rows[index] = values
                updated = True
                break
        if not updated:
            all_rows.append(values)
        refresh_tree(all_rows)

    def delete_player():
        selected_values = [list(tree.item(item, "values")) for item in tree.selection()]
        all_rows[:] = [row for row in all_rows if list(row) not in selected_values]
        refresh_tree(all_rows)

    def apply_filter(*_):
        query = search_var.get().strip().lower()
        if not query:
            refresh_tree(all_rows)
            return
        filtered = []
        for row in all_rows:
            joined = " ".join(str(item) for item in row).lower()
            if query in joined:
                filtered.append(row)
        refresh_tree(filtered)

    search_var.trace_add("write", apply_filter)
    refresh_tree(all_rows)

    btn_group = ttk.Frame(form_frame)
    btn_group.grid(row=len(headers), column=0, columnspan=2, sticky="ew", pady=(12, 0))
    btn_group.columnconfigure(0, weight=1)

    ttk.Button(btn_group, text="Ajouter", command=add_player, style="Primary.TButton").grid(row=0, column=0, sticky="ew", pady=4)
    ttk.Button(btn_group, text="Mettre à jour", command=update_player).grid(row=1, column=0, sticky="ew", pady=4)
    ttk.Button(btn_group, text="Effacer la sélection", command=delete_player).grid(row=2, column=0, sticky="ew", pady=4)
    ttk.Button(btn_group, text="Réinitialiser le formulaire", command=clear_form, style="Secondary.TButton").grid(row=3, column=0, sticky="ew", pady=4)

    footer = ttk.Frame(container)
    footer.pack(fill="x", pady=(12, 0))
    ttk.Button(footer, text="Charger un fichier", command=load_composition).pack(side="left")
    ttk.Button(footer, text="Sauvegarder sous...", command=save_changes, style="Primary.TButton").pack(side="right")


def view_disposition():
    global disposition_window, disposition_exporter
    if disposition_window is not None and disposition_window.winfo_exists():
        disposition_window.deiconify()
        disposition_window.lift()
        disposition_window.focus_force()
        return

    disp_win = tk.Toplevel(root)
    disposition_window = disp_win
    disp_win.title("Disposition")
    disp_win.geometry("1100x760")
    disp_win.minsize(960, 680)
    disp_win.configure(bg=get_palette()["bg"])

    def handle_close():
        global disposition_window
        if disposition_window is not None:
            disposition_window.destroy()
        disposition_window = None

    disp_win.protocol("WM_DELETE_WINDOW", handle_close)

    container = ttk.Frame(disp_win, padding=16)
    container.pack(fill="both", expand=True)

    header_frame = ttk.Frame(container)
    header_frame.pack(fill="x", pady=(0, 12))

    title = ttk.Label(header_frame, text="Disposition sur demi-terrain", style="Header.TLabel")
    title.pack(anchor="w")
    subtitle = ttk.Label(
        header_frame,
        text="Glisse les joueurs ou les postes pour créer une disposition claire et exportable.",
        style="Subheader.TLabel"
    )
    subtitle.pack(anchor="w", pady=(4, 0))

    content = ttk.Frame(container)
    content.pack(fill="both", expand=True)

    canvas_frame = ttk.Frame(content)
    canvas_frame.pack(side="left", fill="both", expand=True)

    controls_container = ttk.Frame(content)
    controls_container.pack(side="right", fill="y")
    controls_canvas = tk.Canvas(
        controls_container,
        highlightthickness=0,
        bg=get_palette()["bg"],
        width=280
    )
    controls_canvas.pack(side="left", fill="y", expand=True)
    controls_scrollbar = ttk.Scrollbar(controls_container, orient="vertical", command=controls_canvas.yview)
    controls_scrollbar.pack(side="right", fill="y")
    controls_canvas.configure(yscrollcommand=controls_scrollbar.set)

    controls = ttk.Frame(controls_canvas, padding=(16, 0, 0, 0))
    controls_window = controls_canvas.create_window((0, 0), window=controls, anchor="nw")

    def sync_controls_scrollregion(event=None):
        controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))

    def sync_controls_width(event):
        controls_canvas.itemconfigure(controls_window, width=event.width)

    def on_controls_mousewheel(event):
        controls_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_controls_mousewheel(event):
        controls_canvas.bind_all("<MouseWheel>", on_controls_mousewheel)

    def unbind_controls_mousewheel(event):
        controls_canvas.unbind_all("<MouseWheel>")

    controls.bind("<Configure>", sync_controls_scrollregion)
    controls_canvas.bind("<Configure>", sync_controls_width)
    controls_canvas.bind("<Enter>", bind_controls_mousewheel)
    controls_canvas.bind("<Leave>", unbind_controls_mousewheel)

    formation_var = tk.StringVar(value="4-4-2")
    formation_frame = ttk.Labelframe(controls, text="Formation")
    formation_frame.pack(fill="x", pady=(0, 12))
    formation_box = ttk.Combobox(
        formation_frame,
        textvariable=formation_var,
        values=sorted(formations.keys()),
        state="readonly"
    )
    formation_box.pack(fill="x", padx=8, pady=(8, 4))
    refresh_button = ttk.Button(formation_frame, text="Rafraîchir l'effectif", style="Secondary.TButton")
    refresh_button.pack(fill="x", padx=8, pady=(0, 8))

    players_frame = ttk.Labelframe(controls, text="Joueurs non placés")
    players_frame.pack(fill="both", pady=(0, 12))
    leftover_list = tk.Listbox(players_frame, height=14)
    leftover_list.pack(fill="both", expand=True, padx=8, pady=8)

    mode_var = tk.StringVar(value="players")
    mode_frame = ttk.Labelframe(controls, text="Mode d'interaction")
    mode_frame.pack(fill="x", pady=(0, 12))
    ttk.Radiobutton(
        mode_frame,
        text="Placement joueurs",
        value="players",
        variable=mode_var
    ).pack(anchor="w", padx=8, pady=(4, 2))
    ttk.Radiobutton(
        mode_frame,
        text="Déplacement postes",
        value="slots",
        variable=mode_var
    ).pack(anchor="w", padx=8, pady=(0, 8))

    selected_player_var = tk.StringVar(value="Aucun")
    selection_frame = ttk.Labelframe(controls, text="Sélection")
    selection_frame.pack(fill="x", pady=(0, 12))
    ttk.Label(selection_frame, textvariable=selected_player_var, style="Muted.TLabel").pack(anchor="w", padx=8, pady=(6, 6))
    clear_selection_button = ttk.Button(selection_frame, text="Effacer sélection", style="Secondary.TButton")
    clear_selection_button.pack(fill="x", padx=8, pady=(0, 8))

    actions_frame = ttk.Labelframe(controls, text="Actions")
    actions_frame.pack(fill="x", pady=(0, 12))
    reset_assignments_button = ttk.Button(actions_frame, text="Réinitialiser placements")
    reset_assignments_button.pack(fill="x", padx=8, pady=(8, 6))
    reset_positions_button = ttk.Button(actions_frame, text="Réinitialiser postes")
    reset_positions_button.pack(fill="x", padx=8, pady=(0, 8))

    help_text = ttk.Label(
        controls,
        text=(
            "Sélectionne un joueur puis clique sur un poste pour le placer. "
            "Tu peux aussi cliquer un poste pour déplacer un joueur déjà assigné. "
            "En mode déplacement, fais glisser un poste pour ajuster sa position."
        ),
        style="Muted.TLabel",
        wraplength=220,
        justify="left"
    )
    help_text.pack(anchor="w")

    canvas = tk.Canvas(canvas_frame, bg="#2E7D32", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    saved_state = load_disposition_state()
    player_overrides_by_formation = dict(saved_state.get("player_overrides_by_formation", {}))
    slot_offsets_by_formation = dict(saved_state.get("slot_offsets_by_formation", {}))
    slot_positions = {}
    current_slots = []
    current_assignments = []
    drag_state = {"type": None, "player": None, "slot_id": None, "start": (0, 0), "base_offset": (0, 0)}
    selected_slot_id = {"value": None}
    player_menu = tk.Menu(disp_win, tearoff=0)

    def clamp(value, min_value=0.05, max_value=0.95):
        return max(min_value, min(max_value, value))

    def current_overrides():
        return player_overrides_by_formation.setdefault(formation_var.get(), {})

    def current_offsets():
        return slot_offsets_by_formation.setdefault(formation_var.get(), {})

    def cleanup_overrides():
        valid_names = {str(row[0]).strip() for row in effectif if row}
        overrides = current_overrides()
        stale = [name for name in overrides.keys() if name not in valid_names]
        for name in stale:
            overrides.pop(name, None)

    def get_slot_at(x, y):
        for slot_id, (sx, sy) in slot_positions.items():
            if (x - sx) ** 2 + (y - sy) ** 2 <= 24 ** 2:
                return slot_id
        return None

    def pick_player_from_slot(slot_id, event=None):
        slot_index = next((idx for idx, slot in enumerate(current_slots) if slot["id"] == slot_id), None)
        if slot_index is None:
            return
        players = current_assignments[slot_index]
        if not players:
            return
        if len(players) == 1:
            start_player_drag(players[0], slot_id)
            return
        player_menu.delete(0, tk.END)
        for player_name in players:
            player_menu.add_command(
                label=player_name,
                command=lambda p=player_name: start_player_drag(p, slot_id)
            )
        if event is not None:
            player_menu.post(event.x_root, event.y_root)

    def start_player_drag(player_name, slot_id=None):
        drag_state.update({"type": "player", "player": player_name, "slot_id": slot_id})
        selected_player_var.set(player_name)

    def assign_player_to_slot(player_name, slot_id):
        if not player_name or not slot_id:
            return
        overrides = current_overrides()
        overrides[player_name] = slot_id
        drag_state.update({"type": None, "player": None, "slot_id": None})
        update_view()

    def reset_assignments():
        current_overrides().clear()
        selected_player_var.set("Aucun")
        update_view()

    def reset_positions():
        current_offsets().clear()
        selected_slot_id["value"] = None
        update_view()

    def clear_player_selection():
        selected_player_var.set("Aucun")
        drag_state.update({"type": None, "player": None, "slot_id": None})

    def save_current_disposition(show_message=True):
        if save_disposition_state(player_overrides_by_formation, slot_offsets_by_formation):
            if show_message:
                messagebox.showinfo("Disposition sauvegardée", "Les placements ont été enregistrés.")
        elif show_message:
            messagebox.showerror("Erreur", "Impossible d'enregistrer la disposition.")

    def reload_disposition():
        state = load_disposition_state()
        player_overrides_by_formation.clear()
        slot_offsets_by_formation.clear()
        player_overrides_by_formation.update(state.get("player_overrides_by_formation", {}))
        slot_offsets_by_formation.update(state.get("slot_offsets_by_formation", {}))
        selected_player_var.set("Aucun")
        selected_slot_id["value"] = None
        update_view()

    def draw_pitch():
        canvas.delete("pitch")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        margin = 24
        pitch_left = margin
        pitch_top = margin
        pitch_right = width - margin
        pitch_bottom = height - margin

        canvas.create_rectangle(
            pitch_left, pitch_top, pitch_right, pitch_bottom,
            outline="white", width=3, tags="pitch"
        )
        canvas.create_line(
            pitch_left, pitch_bottom, pitch_right, pitch_bottom,
            fill="white", width=2, tags="pitch"
        )

        penalty_width = (pitch_right - pitch_left) * 0.55
        penalty_height = (pitch_bottom - pitch_top) * 0.22
        penalty_left = (width - penalty_width) / 2
        penalty_top = pitch_top
        canvas.create_rectangle(
            penalty_left, penalty_top,
            penalty_left + penalty_width, penalty_top + penalty_height,
            outline="white", width=2, tags="pitch"
        )

        goal_width = penalty_width * 0.55
        goal_height = penalty_height * 0.45
        goal_left = (width - goal_width) / 2
        canvas.create_rectangle(
            goal_left, penalty_top,
            goal_left + goal_width, penalty_top + goal_height,
            outline="white", width=2, tags="pitch"
        )

        spot_y = penalty_top + penalty_height * 0.72
        canvas.create_oval(
            width / 2 - 4, spot_y - 4,
            width / 2 + 4, spot_y + 4,
            fill="white", outline="white", tags="pitch"
        )

        arc_radius = (pitch_right - pitch_left) * 0.18
        canvas.create_arc(
            width / 2 - arc_radius,
            pitch_bottom - arc_radius,
            width / 2 + arc_radius,
            pitch_bottom + arc_radius,
            start=0,
            extent=180,
            style="arc",
            outline="white",
            width=2,
            tags="pitch"
        )

    def update_view():
        canvas.delete("player")
        draw_pitch()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        margin = 24
        cleanup_overrides()
        slots = build_formation_slots(formation_var.get())
        offsets = current_offsets()
        slot_positions.clear()
        valid_slot_ids = {slot["id"] for slot in slots}
        if selected_slot_id["value"] not in valid_slot_ids:
            selected_slot_id["value"] = None
        overrides = current_overrides()
        for name, slot_id in list(overrides.items()):
            if slot_id not in valid_slot_ids:
                overrides.pop(name, None)
        for slot in slots:
            dx, dy = offsets.get(slot["id"], (0.0, 0.0))
            slot["x"] = clamp(slot["x"] + dx)
            slot["y"] = clamp(slot["y"] + dy, 0.08, 0.92)
        assignments = assign_players_to_slots(slots, effectif, overrides)
        current_slots[:] = slots
        current_assignments[:] = assignments

        leftover_list.delete(0, tk.END)
        placed_names = {name for group in assignments for name in group}
        for row in effectif:
            if not row:
                continue
            name = str(row[0]).strip()
            if name and name not in placed_names:
                leftover_list.insert(tk.END, name)

        for slot, players in zip(slots, assignments):
            x = margin + slot["x"] * (width - 2 * margin)
            y = margin + slot["y"] * (height - 2 * margin)
            slot_positions[slot["id"]] = (x, y)
            canvas.create_oval(
                x - 22, y - 22, x + 22, y + 22,
                fill="#0B3D2E", outline="white", width=2, tags="player"
            )
            if selected_slot_id["value"] == slot["id"]:
                canvas.create_oval(
                    x - 26, y - 26, x + 26, y + 26,
                    outline="#F4D35E", width=2, tags="player"
                )
            label = "\n".join(players) if players else slot["role"]
            canvas.create_text(
                x, y,
                text=label,
                fill="white",
                font=("Segoe UI", 8, "bold"),
                width=130,
                tags="player"
            )

    def schedule_update(event=None):
        if hasattr(disp_win, "_update_job"):
            disp_win.after_cancel(disp_win._update_job)
        disp_win._update_job = disp_win.after(120, update_view)

    def on_leftover_select(event=None):
        selection = leftover_list.curselection()
        if not selection:
            return
        player_name = leftover_list.get(selection[0])
        selected_player_var.set(player_name)

    def on_canvas_press(event):
        slot_id = get_slot_at(event.x, event.y)
        if mode_var.get() == "slots":
            if slot_id:
                selected_slot_id["value"] = slot_id
                width = canvas.winfo_width()
                height = canvas.winfo_height()
                margin = 24
                offsets = current_offsets()
                base_offset = offsets.get(slot_id, (0.0, 0.0))
                drag_state.update({
                    "type": "slot",
                    "slot_id": slot_id,
                    "start": (event.x, event.y),
                    "base_offset": base_offset,
                })
                update_view()
            else:
                selected_slot_id["value"] = None
                update_view()
            return
        if mode_var.get() == "players":
            if slot_id:
                player_name = selected_player_var.get()
                if player_name and player_name != "Aucun":
                    assign_player_to_slot(player_name, slot_id)
                else:
                    pick_player_from_slot(slot_id, event)

    def on_canvas_drag(event):
        if drag_state["type"] != "slot":
            return
        slot_id = drag_state["slot_id"]
        if not slot_id:
            return
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        margin = 24
        pitch_w = max(1, width - 2 * margin)
        pitch_h = max(1, height - 2 * margin)
        dx = (event.x - drag_state["start"][0]) / pitch_w
        dy = (event.y - drag_state["start"][1]) / pitch_h
        base_dx, base_dy = drag_state["base_offset"]
        offsets = current_offsets()
        offsets[slot_id] = (base_dx + dx, base_dy + dy)
        update_view()

    def on_canvas_release(event):
        if drag_state["type"] == "player":
            slot_id = get_slot_at(event.x, event.y)
            if slot_id:
                assign_player_to_slot(drag_state["player"], slot_id)
        drag_state.update({"type": None, "player": None, "slot_id": None})

    def ensure_pillow_available():
        global PIL_AVAILABLE, Image, ImageGrab
        if PIL_AVAILABLE:
            return
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            from PIL import Image, ImageGrab
            PIL_AVAILABLE = True
        except Exception as exc:
            logging.exception("Installation Pillow impossible.")
            raise RuntimeError("Installation de Pillow impossible. Vérifie ta connexion ou installe-le manuellement.") from exc

    def is_mostly_dark(image, threshold=12):
        try:
            extrema = image.convert("RGB").getextrema()
        except Exception:
            return False
        max_channel = max(channel[1] for channel in extrema)
        return max_channel <= threshold

    def get_display_scale():
        try:
            scale = float(disp_win.tk.call("tk", "scaling"))
        except Exception:
            scale = 1.0
        if scale <= 0:
            scale = 1.0
        return scale

    def capture_via_imagegrab(width, height):
        if ImageGrab is None:
            return None
        scale = get_display_scale()
        x = int(canvas.winfo_rootx() * scale)
        y = int(canvas.winfo_rooty() * scale)
        grab_width = int(width * scale)
        grab_height = int(height * scale)
        image = None
        for _ in range(4):
            canvas.update_idletasks()
            canvas.update()
            time.sleep(0.05)
            try:
                image = ImageGrab.grab(
                    bbox=(x, y, x + grab_width, y + grab_height),
                    all_screens=True
                )
            except TypeError:
                image = ImageGrab.grab(bbox=(x, y, x + grab_width, y + grab_height))
            if image and not is_mostly_dark(image):
                return image.convert("RGB")
        if image and not is_mostly_dark(image):
            return image.convert("RGB")
        return None

    def capture_via_postscript(width, height):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                ps_path = os.path.join(temp_dir, "disposition.ps")
                canvas.postscript(
                    file=ps_path,
                    colormode="color",
                    x=0,
                    y=0,
                    width=width,
                    height=height,
                    pagewidth=width,
                    pageheight=height
                )
                image = Image.open(ps_path)
                image.load()
                image = image.convert("RGB")
                if not is_mostly_dark(image):
                    return image
                logging.warning("Image PostScript trop sombre.")
        except Exception:
            logging.exception("Erreur conversion PostScript.")
        return None

    def capture_canvas_image():
        ensure_pillow_available()
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow n'est pas disponible pour l'export PDF.")
        wait_for_canvas_ready()
        canvas.update_idletasks()
        canvas.update()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1 or height <= 1:
            raise RuntimeError("Surface de canvas invalide pour l'export PDF.")

        image = capture_via_imagegrab(width, height)
        if image:
            return image

        image = capture_via_postscript(width, height)
        if image:
            return image

        raise RuntimeError(
            "Impossible de capturer la disposition (capture écran et PostScript en échec)."
        )

    def focus_disposition_window(keep_topmost=False):
        disp_win.deiconify()
        disp_win.lift()
        disp_win.focus_force()
        if keep_topmost:
            disp_win.attributes("-topmost", True)
        else:
            disp_win.attributes("-topmost", False)
        disp_win.update_idletasks()
        disp_win.update()

    def wait_for_canvas_ready():
        for _ in range(6):
            disp_win.update_idletasks()
            disp_win.update()
            if canvas.winfo_viewable() and canvas.winfo_width() > 1 and canvas.winfo_height() > 1:
                return
            time.sleep(0.05)
        if canvas.winfo_width() <= 1 or canvas.winfo_height() <= 1:
            raise RuntimeError("Surface de canvas invalide pour l'export PDF.")

    def export_disposition_pdf():
        global pdf_folder
        focus_disposition_window(keep_topmost=False)
        disp_win.attributes("-topmost", False)
        disp_win.update_idletasks()
        disp_win.update()

        folder_selected = filedialog.askdirectory(
            parent=disp_win,
            title="Choisir le dossier de sauvegarde"
        )
        if not folder_selected:
            return
        pdf_folder = folder_selected
        refresh_status()
        logging.debug(f"Dossier PDF sélectionné pour la disposition : {pdf_folder}")

        filename = filedialog.asksaveasfilename(
            parent=disp_win,
            title="Enregistrer la disposition en PDF",
            initialdir=pdf_folder,
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"Disposition_{formation_var.get()}.pdf"
        )
        if not filename:
            return

        try:
            focus_disposition_window(keep_topmost=True)
            schedule_update()
            wait_for_canvas_ready()
            time.sleep(0.08)
            image = capture_canvas_image()
            with tempfile.TemporaryDirectory() as temp_dir:
                png_path = os.path.join(temp_dir, "disposition.png")
                image.save(png_path, "PNG")

                pdf = FPDF(unit="pt", format=[image.width, image.height])
                pdf.add_page()
                pdf.image(png_path, 0, 0, image.width, image.height)
                pdf.output(filename)

            messagebox.showinfo("PDF généré", f"Disposition exportée vers :\n{filename}")
        except Exception as exc:
            logging.exception("Erreur export disposition PDF")
            messagebox.showerror(
                "Erreur",
                f"Impossible d'exporter la disposition en PDF.\n{exc}"
            )
        finally:
            disp_win.attributes("-topmost", False)

    disposition_exporter = export_disposition_pdf
    reset_assignments_button.config(command=reset_assignments)
    reset_positions_button.config(command=reset_positions)
    clear_selection_button.config(command=clear_player_selection)
    ttk.Button(actions_frame, text="Sauvegarder la disposition", command=save_current_disposition, style="Primary.TButton").pack(fill="x", padx=8, pady=(0, 6))
    ttk.Button(actions_frame, text="Charger la disposition", command=reload_disposition, style="Secondary.TButton").pack(fill="x", padx=8, pady=(0, 6))
    ttk.Button(actions_frame, text="Exporter en PDF", command=export_disposition_pdf, style="Primary.TButton").pack(fill="x", padx=8, pady=(0, 8))

    formation_box.bind("<<ComboboxSelected>>", schedule_update)
    refresh_button.config(command=schedule_update)
    canvas.bind("<Configure>", schedule_update)
    canvas.bind("<ButtonPress-1>", on_canvas_press)
    canvas.bind("<B1-Motion>", on_canvas_drag)
    canvas.bind("<ButtonRelease-1>", on_canvas_release)
    leftover_list.bind("<<ListboxSelect>>", on_leftover_select)
    schedule_update()


def export_disposition_from_sidebar():
    view_disposition()
    if disposition_exporter and disposition_window is not None:
        disposition_window.deiconify()
        disposition_window.lift()
        disposition_window.focus_force()
        disposition_window.update_idletasks()
        disposition_window.after(150, disposition_exporter)
    else:
        messagebox.showwarning(
            "Disposition indisponible",
            "Ouvre la fenêtre de disposition pour exporter le PDF."
        )

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

def get_palette(theme_name=None):
    return themes.get(theme_name or settings.get("theme"), themes["Azur & Or"])

def apply_theme(theme_name):
    palette = get_palette(theme_name)
    root.configure(bg=palette["bg"])
    style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), background=palette["bg"], foreground=palette["primary"])
    style.configure("Subheader.TLabel", font=("Segoe UI", 12, "bold"), background=palette["bg"], foreground=palette["text"])
    style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), background=palette["card"], foreground=palette["primary"])
    style.configure("TLabel", background=palette["bg"], foreground=palette["text"])
    style.configure("Muted.TLabel", background=palette["card"], foreground=palette["muted"])
    style.configure("Tag.TLabel", font=("Segoe UI", 9, "bold"), background=palette["accent"], foreground=palette["text"], padding=(6, 2))
    style.configure("TButton", font=("Segoe UI", 10), padding=10, background=palette["button"], foreground=palette["button_text"])
    style.map("TButton", background=[("active", palette["accent"])], foreground=[("active", palette["text"])])
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=10, background=palette["primary"], foreground=palette["button_text"])
    style.map("Primary.TButton", background=[("active", palette["accent"])], foreground=[("active", palette["text"])])
    style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=10, background=palette["card"], foreground=palette["primary"])
    style.map("Secondary.TButton", background=[("active", palette["accent"])], foreground=[("active", palette["text"])])
    style.configure("Sidebar.TFrame", background=palette["primary"])
    style.configure("Sidebar.TLabel", background=palette["primary"], foreground=palette["button_text"], font=("Segoe UI", 11, "bold"))
    style.configure("SidebarMuted.TLabel", background=palette["primary"], foreground=palette["button_text"], font=("Segoe UI", 9))
    style.configure("Sidebar.TButton", font=("Segoe UI", 10, "bold"), padding=8, background=palette["accent"], foreground=palette["text"])
    style.map("Sidebar.TButton", background=[("active", palette["card"])], foreground=[("active", palette["primary"])])
    style.configure("Card.TFrame", background=palette["card"])
    style.configure("CardTitle.TLabel", background=palette["card"], font=("Segoe UI", 11, "bold"), foreground=palette["primary"])
    style.configure("App.TFrame", background=palette["bg"])
    style.configure("TEntry", fieldbackground="#FFFFFF", background=palette["card"], foreground=palette["text"])
    style.configure("TCombobox", fieldbackground="#FFFFFF", background=palette["card"], foreground=palette["text"])
    style.configure("TFrame", background=palette["bg"])
    style.configure("TLabelframe", background=palette["bg"], foreground=palette["primary"])
    style.configure("TLabelframe.Label", background=palette["bg"], foreground=palette["primary"], font=("Segoe UI", 10, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background=palette["card"], fieldbackground=palette["card"], foreground=palette["text"])
    style.map("Treeview", background=[("selected", palette["accent"])], foreground=[("selected", palette["text"])])
    style.configure("TNotebook", background=palette["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(14, 8), background=palette["card"], foreground=palette["primary"])
    style.map("TNotebook.Tab", background=[("selected", palette["accent"])], foreground=[("selected", palette["text"])])
    settings["theme"] = theme_name
    if "theme_var" in globals():
        theme_var.set(theme_name)
    save_settings()

def save_settings():
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        logging.debug("Paramètres sauvegardés")
    except Exception as e:
        logging.error(f"Erreur sauvegarde settings : {e}")

def get_effectif_metrics():
    total = len(effectif)
    loaned = sum(1 for row in effectif if "prêt" in str(safe_cell(row, 4)).lower())
    ages = []
    for row in effectif:
        age_text = str(safe_cell(row, 2))
        digits = [int(x) for x in age_text.replace(" ", "").split("-") if x.isdigit()]
        if digits:
            ages.append(sum(digits) / len(digits))
    avg_age = round(sum(ages) / len(ages), 1) if ages else "-"
    return total, loaned, avg_age

app = ttk.Frame(root, style="App.TFrame")
app.pack(fill="both", expand=True)
app.columnconfigure(1, weight=1)
app.rowconfigure(0, weight=1)

sidebar = ttk.Frame(app, style="Sidebar.TFrame", padding=(18, 24))
sidebar.grid(row=0, column=0, sticky="ns")

content = ttk.Frame(app, style="App.TFrame", padding=(24, 20))
content.grid(row=0, column=1, sticky="nsew")
content.columnconfigure(0, weight=1)
content.rowconfigure(1, weight=1)

theme_var = tk.StringVar(value=settings["theme"])

sidebar_title = ttk.Label(sidebar, text=settings["club_name"], style="Sidebar.TLabel")
sidebar_title.pack(anchor="w")
sidebar_season = ttk.Label(sidebar, text=f"Saison {settings['season']}", style="SidebarMuted.TLabel")
sidebar_season.pack(anchor="w", pady=(4, 16))

header = ttk.Label(content, text=f"Centre de contrôle · {settings['club_name']}", style="Header.TLabel")
header.grid(row=0, column=0, sticky="w", pady=(0, 12))

notebook = ttk.Notebook(content)
notebook.grid(row=1, column=0, sticky="nsew")

overview_tab = ttk.Frame(notebook)
settings_tab = ttk.Frame(notebook)
actions_tab = ttk.Frame(notebook)
status_tab = ttk.Frame(notebook)

notebook.add(overview_tab, text="Accueil")
notebook.add(settings_tab, text="Paramètres")
notebook.add(actions_tab, text="Actions")
notebook.add(status_tab, text="Statut")

def open_tab(tab):
    notebook.select(tab)
    notebook.focus_set()

def open_overview():
    open_tab(overview_tab)

def open_settings():
    open_tab(settings_tab)

def open_actions():
    open_tab(actions_tab)

def open_status():
    open_tab(status_tab)

sidebar_nav = ttk.Frame(sidebar, style="Sidebar.TFrame")
sidebar_nav.pack(fill="x", pady=(0, 12))
ttk.Label(sidebar_nav, text="Navigation", style="SidebarMuted.TLabel").pack(anchor="w", pady=(0, 6))
ttk.Button(sidebar_nav, text="Accueil", command=open_overview, style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_nav, text="Paramètres", command=open_settings, style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_nav, text="Actions", command=open_actions, style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_nav, text="Statut", command=open_status, style="Sidebar.TButton").pack(fill="x", pady=4)

ttk.Separator(sidebar).pack(fill="x", pady=12)

sidebar_manage = ttk.Frame(sidebar, style="Sidebar.TFrame")
sidebar_manage.pack(fill="x", pady=(0, 12))
ttk.Label(sidebar_manage, text="Gestion de l'effectif", style="SidebarMuted.TLabel").pack(anchor="w", pady=(0, 6))
ttk.Button(sidebar_manage, text="Éditer l'effectif", command=view_edit_composition, style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_manage, text="Disposition terrain", command=view_disposition, style="Sidebar.TButton").pack(fill="x", pady=4)

ttk.Separator(sidebar).pack(fill="x", pady=12)

sidebar_exports = ttk.Frame(sidebar, style="Sidebar.TFrame")
sidebar_exports.pack(fill="x", pady=(0, 12))
ttk.Label(sidebar_exports, text="Exports rapides", style="SidebarMuted.TLabel").pack(anchor="w", pady=(0, 6))
ttk.Button(sidebar_exports, text="PDF composition", command=generate_composition_pdf, style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_exports, text="PDF disposition", command=export_disposition_from_sidebar, style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_exports, text="Dossier PDF", command=lambda: select_folder(), style="Sidebar.TButton").pack(fill="x", pady=4)
ttk.Button(sidebar_exports, text="Nom du PDF", command=lambda: set_filename(), style="Sidebar.TButton").pack(fill="x", pady=4)

ttk.Separator(sidebar).pack(fill="x", pady=12)

sidebar_theme = ttk.Frame(sidebar, style="Sidebar.TFrame")
sidebar_theme.pack(fill="x", pady=(0, 12))
ttk.Label(sidebar_theme, text="Thème", style="SidebarMuted.TLabel").pack(anchor="w", pady=(0, 6))
sidebar_theme_box = ttk.Combobox(sidebar_theme, textvariable=theme_var, values=sorted(themes.keys()), state="readonly")
sidebar_theme_box.pack(fill="x", pady=4)

ttk.Button(sidebar, text="Quitter", command=root.destroy, style="Sidebar.TButton").pack(fill="x", pady=(8, 0))

overview_tab.columnconfigure(0, weight=1)

hero_card = ttk.Frame(overview_tab, style="Card.TFrame", padding=18)
hero_card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
ttk.Label(hero_card, text="Tableau de bord modernisé", style="CardTitle.TLabel").pack(anchor="w")
ttk.Label(
    hero_card,
    text="Centralise toutes les opérations : effectif, disposition visuelle et exports.",
    style="Muted.TLabel"
).pack(anchor="w", pady=(4, 12))
ttk.Button(hero_card, text="Ouvrir l'éditeur de composition", command=view_edit_composition, style="Primary.TButton").pack(anchor="w")

stats_frame = ttk.Frame(overview_tab)
stats_frame.grid(row=1, column=0, sticky="ew")
stats_frame.columnconfigure((0, 1, 2), weight=1)

total_players, loaned_players, avg_age = get_effectif_metrics()

def build_stat_card(parent, title, value):
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
    ttk.Label(card, text=value, style="Header.TLabel").pack(anchor="w", pady=(6, 0))
    return card

build_stat_card(stats_frame, "Joueurs", total_players).grid(row=0, column=0, sticky="ew", padx=(0, 8))
build_stat_card(stats_frame, "Prêts en cours", loaned_players).grid(row=0, column=1, sticky="ew", padx=8)
build_stat_card(stats_frame, "Âge moyen", avg_age).grid(row=0, column=2, sticky="ew", padx=(8, 0))

settings_tab.columnconfigure(0, weight=1)
settings_card = ttk.Frame(settings_tab, style="Card.TFrame", padding=16)
settings_card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
ttk.Label(settings_card, text="Paramètres du club", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

settings_grid = ttk.Frame(settings_card)
settings_grid.pack(fill="x")
settings_grid.columnconfigure(1, weight=1)
settings_grid.columnconfigure(3, weight=1)

club_var = tk.StringVar(value=settings["club_name"])
season_var = tk.StringVar(value=settings["season"])

ttk.Label(settings_grid, text="Nom du club").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
club_entry = ttk.Entry(settings_grid, textvariable=club_var)
club_entry.grid(row=0, column=1, sticky="ew", pady=6)

ttk.Label(settings_grid, text="Saison").grid(row=0, column=2, sticky="w", padx=(16, 8), pady=6)
season_entry = ttk.Entry(settings_grid, textvariable=season_var)
season_entry.grid(row=0, column=3, sticky="ew", pady=6)

ttk.Label(settings_grid, text="Thème").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
theme_box = ttk.Combobox(settings_grid, textvariable=theme_var, values=sorted(themes.keys()), state="readonly")
theme_box.grid(row=1, column=1, sticky="w", pady=6)

apply_button = ttk.Button(settings_grid, text="Appliquer", command=lambda: update_club_settings(), style="Primary.TButton")
apply_button.grid(row=1, column=3, sticky="e", pady=6)

actions_tab.columnconfigure(0, weight=1)
actions_card = ttk.Frame(actions_tab, style="Card.TFrame", padding=16)
actions_card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
ttk.Label(actions_card, text="Actions rapides", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

actions = ttk.Frame(actions_card)
actions.pack(fill="x")
actions.columnconfigure(0, weight=1)
actions.columnconfigure(1, weight=1)

ttk.Button(actions, text="Imprimer la composition", command=generate_composition_pdf, style="Primary.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=6)
ttk.Button(actions, text="Exporter la disposition", command=export_disposition_from_sidebar, style="Secondary.TButton").grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=6)
ttk.Button(actions, text="Sélectionner un dossier", command=lambda: select_folder(), style="Secondary.TButton").grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=6)
ttk.Button(actions, text="Nommer le PDF", command=lambda: set_filename()).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=6)
ttk.Button(actions, text="Éditer la composition", command=view_edit_composition).grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=6)
ttk.Button(actions, text="Disposition", command=view_disposition).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=6)

status_tab.columnconfigure(0, weight=1)
status_card = ttk.Frame(status_tab, style="Card.TFrame", padding=16)
status_card.grid(row=0, column=0, sticky="ew")
ttk.Label(status_card, text="Paramètres actuels", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

lbl_folder = ttk.Label(status_card, text="")
lbl_folder.pack(anchor="w")
lbl_filename = ttk.Label(status_card, text="")
lbl_filename.pack(anchor="w", pady=(4, 0))
lbl_club = ttk.Label(status_card, text="")
lbl_club.pack(anchor="w", pady=(4, 0))
lbl_season = ttk.Label(status_card, text="")
lbl_season.pack(anchor="w")
lbl_theme = ttk.Label(status_card, text="")
lbl_theme.pack(anchor="w", pady=(4, 0))

def refresh_status():
    lbl_folder.config(text=f"Dossier PDF : {pdf_folder}")
    lbl_filename.config(text=f"Nom PDF : {pdf_filename}")
    lbl_club.config(text=f"Club : {settings['club_name']}")
    lbl_season.config(text=f"Saison : {settings['season']}")
    lbl_theme.config(text=f"Thème : {settings['theme']}")
    sidebar_title.config(text=settings["club_name"])
    sidebar_season.config(text=f"Saison {settings['season']}")

def update_club_settings():
    settings["club_name"] = club_var.get().strip() or default_settings["club_name"]
    settings["season"] = season_var.get().strip() or default_settings["season"]
    root.title(f"{settings['club_name']} Dashboard")
    header.config(text=f"Centre de contrôle · {settings['club_name']}")
    refresh_status()
    save_settings()

def on_theme_change(event=None):
    apply_theme(theme_var.get())

theme_box.bind("<<ComboboxSelected>>", on_theme_change)
sidebar_theme_box.bind("<<ComboboxSelected>>", on_theme_change)

# -----------------------------
# Fonctions PDF / nom du fichier / dossier
# -----------------------------
def select_folder():
    global pdf_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        pdf_folder = folder_selected
        refresh_status()
        logging.debug(f"Dossier PDF sélectionné : {pdf_folder}")

def set_filename():
    global pdf_filename
    name = simpledialog.askstring("Nom du PDF", "Entrez le nom du fichier PDF :")
    if name:
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        pdf_filename = name
        refresh_status()
        logging.debug(f"Nom PDF défini : {pdf_filename}")

apply_theme(settings["theme"])
refresh_status()

root.mainloop()
