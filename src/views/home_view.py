import streamlit as st
import pandas as pd
import os
import sqlite3
from ..config import THEME_COLORS, APP_NAME, DB_PATH
from ..utils.db_utils import get_db_connection

def show_home_view():
    """Affiche la page d'accueil de l'application"""
    
    # Titre principal
    st.title("📊 Bienvenue dans LCAMS")
    st.subheader("Logiciel de Calcul et Analyse des Moyennes Semestrielles")
    
    # Présentation de l'application
    st.markdown("""
    LCAMS est une application conçue pour les établissements scolaires sénégalais permettant d'importer, 
    d'analyser et d'interpréter les données d'évaluation générées par la plateforme nationale PLANETE.
    
    ### Fonctionnalités principales:
    - Importation des fichiers Excel standardisés de PLANETE
    - Analyses détaillées par niveau, classe, sexe et discipline
    - Tableaux de bord dynamiques et rapports personnalisés
    - Analyse comparative entre semestres
    - Visualisation des décisions finales
    
    Pour commencer, utilisez le menu de navigation à gauche pour accéder aux différents modules.
    """)
    
    # Affichage des stats générales si des données existent
    if os.path.exists(DB_PATH):
        st.subheader("📈 Tableau de bord")
        
        # Créer un layout avec 4 colonnes pour les stats
        col1, col2, col3, col4 = st.columns(4)
        
        # Connexion à la base de données
        conn = get_db_connection()
        
        # Nombre d'élèves
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Eleves")
        nb_eleves = cursor.fetchone()[0]
        
        # Nombre de classes
        cursor.execute("SELECT COUNT(*) FROM Classes WHERE etat = 'actif'")
        nb_classes = cursor.fetchone()[0]
        
        # Nombre de disciplines
        cursor.execute("SELECT COUNT(*) FROM Disciplines")
        nb_disciplines = cursor.fetchone()[0]
        
        # Année scolaire active
        cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif'")
        row = cursor.fetchone()
        annee_scolaire = row[0] if row else "Non définie"
        
        conn.close()
        
        # Affichage des métriques
        col1.metric("Élèves enregistrés", nb_eleves)
        col2.metric("Classes actives", nb_classes)
        col3.metric("Disciplines", nb_disciplines)
        col4.metric("Année scolaire", annee_scolaire)
        
        # Informations sur l'établissement
        st.subheader("📍 Informations de l'établissement")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        conn.close()
        
        if config:
            col1, col2 = st.columns(2)
            col1.info(f"""
            **Nom**: {config['nom_etablissement'] or 'Non défini'}  
            **Adresse**: {config['adresse'] or 'Non définie'}  
            **Téléphone**: {config['telephone'] or 'Non défini'}
            """)
            
            col2.info(f"""
            **Inspection d'académie**: {config['inspection_academique'] or 'Non définie'}  
            **Inspection de l'éducation**: {config['inspection_education'] or 'Non définie'}
            """)
        else:
            st.warning("Les informations de l'établissement ne sont pas encore configurées. Veuillez vous rendre dans le module Paramètres.")
    
    else:
        # Message pour l'utilisateur si aucune donnée n'existe
        st.info("Aucune donnée n'est encore disponible. Commencez par configurer l'application dans le module Paramètres.")
    
    # Pied de page avec des liens d'aide
    st.divider()
    st.markdown("""
    ### Besoin d'aide?
    - Consultez la documentation complète pour apprendre à utiliser LCAMS
    - Importez des données dans le Module Semestre 1 ou Semestre 2
    - Configurez les paramètres de votre établissement
    """)