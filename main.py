import streamlit as st
import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import APP_NAME, APP_VERSION
from src.utils.db_utils import init_database
from src.views.home_view import show_home_view
from src.views.parametres_view import show_parametres_view
from src.views.semestre1_view import show_semestre1_view
from src.views.semestre2_view import show_semestre2_view
from src.views.general_view import show_general_view

# Configuration de la page Streamlit
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    # Initialiser la base de données
    init_database()
    
    # Barre latérale avec navigation
    st.sidebar.title(f"{APP_NAME}")
    st.sidebar.caption(f"Version {APP_VERSION}")
    
    # Menu de navigation
    menu = st.sidebar.radio(
        "Navigation",
        ["Accueil", "Module Semestre 1", "Module Semestre 2", "Module Général", "Paramètres"],
        captions=["Page principale", "Données du 1er semestre", "Données du 2ème semestre", "Analyses annuelles", "Configuration"]
    )
    
    # Afficher la vue correspondante
    if menu == "Accueil":
        show_home_view()
    elif menu == "Module Semestre 1":
        show_semestre1_view()
    elif menu == "Module Semestre 2":
        show_semestre2_view()
    elif menu == "Module Général":
        show_general_view()
    elif menu == "Paramètres":
        show_parametres_view()
    
    # Pied de page
    st.sidebar.divider()
    st.sidebar.caption("© 2025 LCAMS")

if __name__ == "__main__":
    main()