# SQDTool — Tableau moderne de gestion d’effectif

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-0F172A)
![Licence](https://img.shields.io/badge/Licence-MIT-10B981)

**SQDTool** est une application de bureau (Tkinter) pour piloter un effectif, organiser une disposition tactique et générer des PDF propres, prêts à être partagés. Elle combine un éditeur de roster flexible, une vue terrain interactive et un système de thèmes pour moderniser l’interface.

**Langues :** [English](README.en.md) · [العربية](README.ar.md) · [Licence](LICENSE)

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Aperçu rapide](#aperçu-rapide)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Paramètres du club](#paramètres-du-club)
  - [Éditeur d’effectif](#éditeur-deffectif)
  - [Disposition (terrain)](#disposition-terrain)
  - [Exports PDF](#exports-pdf)
- [Fichiers et persistance](#fichiers-et-persistance)
- [Personnalisation](#personnalisation)
- [Dépannage](#dépannage)
- [Licence](#licence)

---

## Fonctionnalités

- **Gestion complète de l’effectif** : ajout, édition, suppression en un clic.
- **Disposition tactique interactive** : placement des joueurs et repositionnement manuel des postes.
- **PDF “Effectif”** : export structuré par postes.
- **PDF “Disposition”** : export fidèle de la vue terrain (copie conforme de l’écran).
- **Thèmes modernes** : 12 palettes intégrées, sauvegarde automatique.
- **Paramètres persistants** : nom du club, saison, thème.

---

## Aperçu rapide

1. Lancez l’application : `python marseille.pyw`.
2. Modifiez votre effectif dans **Éditer la composition**.
3. Organisez votre équipe via **Disposition**.
4. Exportez des PDF : effectif et disposition.

---

## Installation

```bash
git clone <votre-repo>
cd SQDTool
python marseille.pyw
```

> Au premier lancement, **fpdf2** est installé automatiquement si nécessaire. L’export de la disposition installe **Pillow** si besoin.

---

## Utilisation

### Paramètres du club
Dans **Paramètres du club**, vous pouvez éditer :

- **Nom du club**
- **Saison**
- **Thème**

Cliquez sur **Appliquer** pour mettre à jour l’interface et les exports.

### Éditeur d’effectif
Ouvrez **Éditer la composition** pour :

- Ajouter un joueur (nom, poste, âge, nationalité, statut, option d’achat).
- Modifier une ligne existante.
- Supprimer une sélection.
- Sauvegarder la composition au format JSON.

### Disposition (terrain)
La vue **Disposition** permet de construire un schéma tactique sur demi-terrain :

- **Mode Placement joueurs** : sélectionnez un joueur puis cliquez un poste pour l’assigner.
- **Mode Déplacement postes** : faites glisser les postes pour ajuster la structure.
- **Rafraîchir l’effectif** : recharge la liste des joueurs si elle a changé.
- **Réinitialiser** : remise à zéro des placements ou des positions.

### Exports PDF

- **PDF Effectif** : bouton **Générer le PDF** (regroupé par poste).
- **PDF Disposition** : bouton **Exporter en PDF** dans la fenêtre disposition.

Le PDF de disposition est une **copie conforme** de la vue terrain et conserve la mise en page actuelle (postes, joueurs, positions).

---

## Fichiers et persistance

- `composition.json` (ou `effectifOM.json`) : données d’effectif.
- `settings.json` : nom du club, saison, thème.
- `om_program_logs.txt` : logs d’exécution.
- `PDFs/` : exports PDF.

---

## Personnalisation

Vous pouvez ajouter un thème dans `marseille.pyw` via le dictionnaire `themes` :

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

---

## Dépannage

- **Erreur d’export PDF** : assurez-vous d’avoir une connexion pour l’installation initiale de `fpdf2` et `pillow`.
- **PDF introuvable** : vérifiez le dossier choisi lors de l’export.
- **Texte tronqué dans la disposition** : élargissez la fenêtre avant d’exporter.

---

## Licence

Ce projet est sous licence MIT. Voir `LICENSE`.
