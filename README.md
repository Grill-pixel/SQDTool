# SQDTool — Tableau moderne de gestion d’effectif

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-0F172A)
![Licence](https://img.shields.io/badge/Licence-MIT-10B981)

**SQDTool** est une application de bureau Tkinter conçue pour gérer un effectif, créer une disposition tactique visuelle et générer des PDF prêts à être partagés. L’application combine un éditeur de roster, une vue terrain interactive et un système de thèmes pour une expérience moderne et claire.

**Langues :** [English](README.en.md) · [العربية](README.ar.md) · [Licence](LICENSE)

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Pré-requis](#pré-requis)
- [Installation rapide](#installation-rapide)
- [Guide d’utilisation](#guide-dutilisation)
  - [1) Paramètres du club](#1-paramètres-du-club)
  - [2) Gestion de l’effectif](#2-gestion-de-leffectif)
  - [3) Disposition tactique](#3-disposition-tactique)
  - [4) Exports PDF](#4-exports-pdf)
- [Fichiers, persistance et formats](#fichiers-persistance-et-formats)
- [Personnalisation des thèmes](#personnalisation-des-thèmes)
- [Dépannage](#dépannage)
- [Licence](#licence)

---

## Fonctionnalités

- **Gestion complète de l’effectif** : ajout, édition, suppression en un clic.
- **Éditeur riche** : recherche instantanée, formulaire de fiche joueur, sauvegarde JSON.
- **Disposition tactique interactive** : placement par rôle et repositionnement manuel des postes.
- **Exports PDF** :
  - **Effectif** (tableau structuré par colonnes) ;
  - **Disposition** (export fidèle de la vue terrain).
- **Thèmes modernes** : 12 palettes intégrées, sauvegarde automatique.
- **Persistance** : club, saison, thème, composition, disposition sauvegardés.

---

## Pré-requis

- **Python 3.9+**
- Accès **pip** (pour la première installation des dépendances si elles ne sont pas déjà présentes)

> Dépendances utilisées : `fpdf2` (export PDF) et `Pillow` (capture de la disposition). Elles sont installées automatiquement si manquantes.

---

## Installation rapide

```bash
git clone <votre-repo>
cd SQDTool
python marseille.pyw
```

---

## Guide d’utilisation

### 1) Paramètres du club
Dans l’onglet **Paramètres**, vous pouvez modifier :

- **Nom du club**
- **Saison**
- **Thème**

Cliquez sur **Appliquer** pour mettre à jour l’interface et les exports.

### 2) Gestion de l’effectif
Ouvrez **Éditer l’effectif** pour :

- Ajouter un joueur (nom, poste, âge, nationalité, statut, option d’achat).
- Mettre à jour une ligne existante.
- Supprimer une sélection.
- Charger/Sauvegarder votre effectif au format JSON.

### 3) Disposition tactique
La vue **Disposition terrain** permet de construire un schéma tactique sur demi-terrain :

- **Mode Placement joueurs** : sélectionnez un joueur puis cliquez un poste pour l’assigner.
- **Mode Déplacement postes** : faites glisser les postes pour ajuster la structure.
- **Sauvegarder / Charger** : enregistre l’état des placements et positions.
- **Réinitialiser** : remise à zéro des affectations ou des positions.

### 4) Exports PDF

- **PDF Effectif** : bouton **PDF composition** (colonne “Actions” ou barre latérale).
- **PDF Disposition** : bouton **Exporter en PDF** depuis la fenêtre de disposition.

Les exports sont **fidèles à l’interface actuelle** (titres, thème, placements).

---

## Fichiers, persistance et formats

| Fichier / dossier | Rôle |
| --- | --- |
| `effectifOM.json` | Composition par défaut si `composition.json` n’existe pas |
| `composition.json` | Composition enregistrée (format tableau ou dictionnaire) |
| `settings.json` | Nom du club, saison, thème |
| `disposition_layout.json` | Positions et placements par formation |
| `PDFs/` | Exports PDF |
| `om_program_logs.txt` | Logs d’exécution |

### Format de composition accepté
Le fichier peut être :
- une liste de lignes `[[joueur, poste, âge, nationalité, statut, option], ...]`,
- ou un dictionnaire par catégories, qui sera normalisé automatiquement.

---

## Personnalisation des thèmes

Les thèmes sont définis dans `marseille.pyw` via le dictionnaire `themes` :

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

- **Export PDF impossible** : vérifiez que `fpdf2` est installé (connexion nécessaire au premier lancement).
- **Export disposition en erreur** : `Pillow` doit être disponible ; l’installation peut échouer hors connexion.
- **Texte tronqué** : agrandissez la fenêtre avant l’export de disposition.
- **Police non trouvée** : sur certains systèmes, l’export PDF peut utiliser une police de secours.

---

## Licence

Ce projet est sous licence MIT. Voir `LICENSE`.
