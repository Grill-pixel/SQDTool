# SQDTool – Tableau de gestion d’effectif

SQDTool est une application de bureau (Tkinter) qui permet de gérer un effectif, de modifier facilement les données, puis de générer un PDF propre et structuré. L’interface est organisée en cartes modernes et propose un **sélecteur de thèmes** avec plusieurs palettes de couleurs.

Langues : [English](README.en.md) | [العربية](README.ar.md) | [Licence](LICENSE)

## Points clés

- **Nom du club et saison éditables** (plus de texte figé).
- **Édition complète de l’effectif** (ajout, modification, suppression).
- **Export PDF** par postes.
- **Interface modernisée** avec 12 thèmes.
- **Paramètres sauvegardés automatiquement**.

## Prérequis

- Python 3.9+
- Accès internet (uniquement pour l’installation auto de `fpdf2` au premier lancement)

## Installation

```bash
git clone <votre-repo>
cd SQDTool
python marseille.pyw
```

> Lors du premier lancement, l’application installe `fpdf2` si nécessaire.

## Fonctionnalités principales

### 1) Paramètres du club
Dans la carte **« Paramètres du club »**, vous pouvez définir :

- **Nom du club**
- **Saison**
- **Thème**

Cliquez sur **Appliquer** pour enregistrer et mettre à jour le titre, le panneau de statut et l’en‑tête du PDF.

### 2) Sélecteur de thèmes
Le menu déroulant propose 12 palettes (ex. « Azur & Or », « Océan Profond », « Lavande Moderne »). Le thème s’applique immédiatement et est mémorisé.

### 3) Éditeur d’effectif
Cliquez sur **« Éditer la composition »** :

- Ajoutez, modifiez ou supprimez des joueurs.
- Les données sont sauvegardées dans `composition.json`.
- L’éditeur fonctionne comme un mini tableur.

### 4) Export PDF
Cliquez sur **« Générer le PDF »** :

- Regroupement automatique par poste.
- Utilisation du nom du club et de la saison actuels.
- Le PDF est enregistré dans le dossier sélectionné (par défaut `PDFs/`).

## Fichiers et persistance

- `composition.json` : données de l’effectif.
- `settings.json` : nom du club, saison, thème.
- `om_program_logs.txt` : journaux de debug.
- `PDFs/` : dossier des exports.

## Personnalisation

Pour ajouter un thème, modifiez le dictionnaire `themes` dans `marseille.pyw` :

```python
"Mon Thème": {
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

## Dépannage

- **Installation FPDF** : lancez `pip install fpdf2` manuellement si besoin.
- **PDF introuvable** : vérifiez le dossier de sortie et les permissions.
- **Polices sur macOS/Linux** : ajustez les chemins de polices dans `generate_pdf_file()`.

## Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus d’informations.
