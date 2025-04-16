import streamlit as st
import pandas as pd
import os
import sqlite3
from ..config import DB_PATH
from ..utils.db_utils import get_db_connection
from ..utils.viz_utils import plot_evolution_semestres

def show_general_view():
    """Affiche le module Général"""
    
    st.title("📊 Module Général")
    
    # Barre latérale pour la navigation interne
    page = st.sidebar.radio(
        "Navigation Module Général",
        ["Analyse Moyennes", "Analyse Disciplines", "Comparaison des semestres", "Décision finale", "Rapports annuels"],
        captions=["Moyennes annuelles", "Performance par discipline", "Évolution S1 vs S2", "Résultats finaux", "Rapports de synthèse"]
    )
    
    # Afficher la page correspondante
    if page == "Analyse Moyennes":
        show_moyennes_analysis()
    elif page == "Analyse Disciplines":
        show_disciplines_analysis()
    elif page == "Comparaison des semestres":
        show_semestres_comparison()
    elif page == "Décision finale":
        show_decisions_finales()
    elif page == "Rapports annuels":
        show_rapports_annuels()

def show_moyennes_analysis():
    """Affiche l'analyse des moyennes annuelles"""
    
    st.subheader("Analyse des moyennes annuelles")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via les modules Semestre 1 et Semestre 2.")
        return
    
    # Vérifier si les données des deux semestres existent
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Notes_S1")
    count_s1 = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Notes_S2")
    count_s2 = cursor.fetchone()[0]
    
    if count_s1 == 0 or count_s2 == 0:
        st.warning("Les données des deux semestres sont nécessaires pour l'analyse annuelle. Veuillez importer les données manquantes.")
        conn.close()
        return
    
    st.info("Module en cours de développement. Veuillez commencer par utiliser les modules Semestre 1 et Semestre 2.")
    conn.close()

def show_disciplines_analysis():
    """Affiche l'analyse par discipline sur l'année"""
    
    st.subheader("Analyse des disciplines sur l'année")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via les modules Semestre 1 et Semestre 2.")
        return
    
    # Vérifier si les données des deux semestres existent
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Notes_S1")
    count_s1 = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Notes_S2")
    count_s2 = cursor.fetchone()[0]
    
    if count_s1 == 0 or count_s2 == 0:
        st.warning("Les données des deux semestres sont nécessaires pour l'analyse annuelle. Veuillez importer les données manquantes.")
        conn.close()
        return
    
    st.info("Module en cours de développement. Veuillez commencer par utiliser les modules Semestre 1 et Semestre 2.")
    conn.close()

def show_semestres_comparison():
    """Affiche la comparaison entre les deux semestres"""
    
    st.subheader("Comparaison entre les deux semestres")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via les modules Semestre 1 et Semestre 2.")
        return
    
    # Vérifier si les données des deux semestres existent
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S1")
    count_s1 = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S2")
    count_s2 = cursor.fetchone()[0]
    
    if count_s1 == 0 or count_s2 == 0:
        st.warning("Les données des deux semestres sont nécessaires pour la comparaison. Veuillez importer les données manquantes.")
        conn.close()
        return
    
    st.info("Module en cours de développement. Veuillez commencer par utiliser les modules Semestre 1 et Semestre 2.")
    conn.close()

def show_decisions_finales():
    """Affiche les décisions finales"""
    
    st.subheader("Décisions finales")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via les modules Semestre 1 et Semestre 2.")
        return
    
    # Vérifier si les données des deux semestres existent
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S1")
    count_s1 = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S2")
    count_s2 = cursor.fetchone()[0]
    
    if count_s1 == 0 or count_s2 == 0:
        st.warning("Les données des deux semestres sont nécessaires pour les décisions finales. Veuillez importer les données manquantes.")
        conn.close()
        return
    
    st.info("Module en cours de développement. Veuillez commencer par utiliser les modules Semestre 1 et Semestre 2.")
    conn.close()

def show_rapports_annuels():
    """Affiche les rapports annuels"""
    
    st.subheader("Rapports annuels")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via les modules Semestre 1 et Semestre 2.")
        return
    
    # Vérifier si les données des deux semestres existent
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S1")
    count_s1 = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S2")
    count_s2 = cursor.fetchone()[0]
    
    if count_s1 == 0 or count_s2 == 0:
        st.warning("Les données des deux semestres sont nécessaires pour les rapports annuels. Veuillez importer les données manquantes.")
        conn.close()
        return
    
    st.info("Module en cours de développement. Veuillez commencer par utiliser les modules Semestre 1 et Semestre 2.")
    conn.close()