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
    initial_sidebar_state="collapsed",
)

# Hide the default Streamlit sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {display: none;}
    a {
        text-decoration: none;
        color: inherit;
    }
    a:visited {
        color: inherit;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Initialiser la base de données
    init_database()
    
    # Récupérer le paramètre de menu de l'URL (si présent)
    menu = st.query_params.get("menu", "Accueil")
    
    # Barre latérale cachée par défaut sur la page d'accueil
    if menu == "Accueil":
        show_home_view()
        return
    
    # Barre latérale avec navigation
    st.sidebar.title(f"{APP_NAME}")
    st.sidebar.caption(f"Version {APP_VERSION}")
    
    # Menu de navigation
    selected_menu = st.sidebar.radio(
        "Navigation",
        ["Accueil", "Module Semestre 1", "Module Semestre 2", "Module Général", "Paramètres"],
        captions=["Page principale", "Données du 1er semestre", "Données du 2ème semestre", "Analyses annuelles", "Configuration"],
        index=["Accueil", "Module Semestre 1", "Module Semestre 2", "Module Général", "Paramètres"].index(menu)
    )
    
    # Mettre à jour l'URL
    st.query_params["menu"] = selected_menu
    
    # Afficher la vue correspondante
    if selected_menu == "Accueil":
        show_home_view()
    elif selected_menu == "Module Semestre 1":
        show_semestre1_view()
    elif selected_menu == "Module Semestre 2":
        show_semestre2_view()
    elif selected_menu == "Module Général":
        show_general_view()
    elif selected_menu == "Paramètres":
        show_parametres_view()
    
    # Pied de page
    st.sidebar.divider()
    st.sidebar.caption("© 2025 LCAMS")

if __name__ == "__main__":
    main()