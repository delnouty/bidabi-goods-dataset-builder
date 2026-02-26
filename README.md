# bidabi-goods-dataset-builder
## 🥂 Objectif du projet
Ce dépôt contient un outil de collecte automatisée de données destiné à construire des jeux de données d’images de produits alimentaires. La première catégorie traitée est les champagnes, récupérés depuis l’API publique OpenFoodFacts. Le projet sert de base à la création de datasets pour des tâches de machine learning (classification, vision par ordinateur, reconnaissance de produits, etc.).

## 📦 Fonctionnalités principales
- Téléchargement robuste de produits via l’API OpenFoodFacts (gestion des erreurs, retries).
- Filtrage des produits pour garantir la qualité des données.
- Téléchargement automatique des images associées.
- Export des métadonnées dans un fichier CSV structuré.
- Organisation claire des données dans un dossier data/.
- Préparation pour l’intégration avec :
- DVC (versionnement des données),
- GitHub Actions (exécution planifiée du scraper),
- pipelines MLOps futurs.

## Structure du dépôt
```
bidabi-goods-dataset-builder/
│
├── src/
│   └── scraper.py          # Script principal de scraping
│
├── data/
│   ├── images/             # Images téléchargées
│   └── metadata.csv        # Métadonnées exportées
│
├── requirements.txt
└── README.md
```
## 🚀 Utilisation
1. Installer les dépendances
```bash
pip install -r requirements.txt
```
2. Lancer le scraper
```bash
python src/scraper.py
```
Les images seront enregistrées dans **data/images/**  
Les métadonnées seront exportées dans **data/metadata.csv**

## 🧠 Description du fonctionnement
Le scraper :

- Interroge l’API OpenFoodFacts pour une catégorie donnée (par défaut : champagnes).
- Applique un filtrage strict pour ne conserver que les produits exploitables.
- Télécharge la meilleure image disponible pour chaque produit.

Construit un fichier CSV contenant :

- l’identifiant du produit,
- le nom,
- les catégories,
- la liste des ingrédients,
- l’URL de l’image.

🔧 Configuration
Les paramètres principaux se trouvent en haut du fichier scraper.py :
```python
TARGET_COUNT = 180
PAGE_SIZE = 100
MAX_PAGES = 50
CATEGORY = "champagnes"
```
Ils peuvent être modifiés selon les besoins.
