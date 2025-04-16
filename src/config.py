# Configuration globale de l'application LCAMS
import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "src", "data")
STATIC_DIR = os.path.join(BASE_DIR, "src", "static")

# Nom des fichiers de base de données
DB_NAME = "lcams.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

# Nom du fichier Excel centralisé
FICHIER_CENTRAL = os.path.join(DATA_DIR, "fichier_central.xlsx")

# Configurations système
APP_NAME = "LCAMS - Logiciel de Calcul et Analyse des Moyennes Semestrielles"
APP_VERSION = "1.0.0"

# Configuration de l'interface
THEME_COLORS = {
    "primary": "#3498db",
    "secondary": "#2c3e50",
    "success": "#2ecc71",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "info": "#1abc9c",
    "light": "#ecf0f1",
    "dark": "#2c3e50",
}

# Niveaux d'enseignement disponibles
NIVEAUX = [
    "6ème", "5ème", "4ème", "3ème",  # Collège
    "Seconde", "Première", "Terminale"  # Lycée
]

# Configuration par défaut de l'établissement
DEFAULT_ETABLISSEMENT = {
    "nom": "",
    "adresse": "",
    "telephone": "",
    "inspection_academique": "",
    "inspection_education": "",
}