import streamlit as st
import pandas as pd
import os
import sqlite3
from ..config import THEME_COLORS, APP_NAME, APP_VERSION, DB_PATH
from ..utils.db_utils import get_db_connection

def show_home_view():
    """Affiche la page d'accueil moderne de l'application"""
    
    # Suppression de la sidebar pour cette vue
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # En-tête de la page
    st.markdown(
        f"""
        <div style="background-color: {THEME_COLORS['primary']}; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="color: white; margin: 0;">{APP_NAME}</h1>
                    <p style="color: white; margin: 0;">Version {APP_VERSION}</p>
                </div>
                <div>
                    <img src="https://img.icons8.com/officel/40/000000/user.png" style="border-radius: 50%; background-color: white; padding: 5px;">
                </div>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Navigation principale
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            """
            <a href="/" style="text-decoration: none;">
                <div style="background-color: #3498db; color: white; padding: 10px; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="margin: 0;">Accueil</p>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <a href="/?menu=Module+Semestre+1" style="text-decoration: none;">
                <div style="background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="margin: 0;">Semestre 1</p>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <a href="/?menu=Module+Semestre+2" style="text-decoration: none;">
                <div style="background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="margin: 0;">Semestre 2</p>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            """
            <a href="/?menu=Module+Général" style="text-decoration: none;">
                <div style="background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="margin: 0;">Module Général</p>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            """
            <a href="/?menu=Paramètres" style="text-decoration: none;">
                <div style="background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="margin: 0;">Paramètres</p>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    
    # Section Hero
    st.markdown(
        """
        <div style="background: linear-gradient(to right, #3498db, #2c3e50); padding: 3rem; border-radius: 5px; margin: 2rem 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h1 style="color: white; margin-bottom: 1rem;">Bienvenue dans LCAMS</h1>
            <p style="color: white; font-size: 1.2rem; margin-bottom: 1.5rem;">Logiciel de Calcul et Analyse des Moyennes Semestrielles pour les établissements scolaires sénégalais</p>
            <a href="/?menu=Module+Semestre+1" style="background-color: white; color: #3498db; padding: 0.8rem 1.5rem; border-radius: 30px; text-decoration: none; font-weight: bold; display: inline-block;">
                Commencer l'analyse
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Vérifier si des données existent pour afficher les statistiques
    if os.path.exists(DB_PATH):
        # Connexion à la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Statistiques clés à récupérer
        cursor.execute("SELECT COUNT(*) FROM Eleves")
        nb_eleves = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Classes WHERE etat = 'actif'")
        nb_classes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Disciplines")
        nb_disciplines = cursor.fetchone()[0]
        
        cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif'")
        row = cursor.fetchone()
        annee_scolaire = row[0] if row else "Non définie"
        
        # Calculer le taux de réussite global si des données existent
        taux_reussite = "N/A"
        cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S1 WHERE moyenne >= 10")
        eleves_reussite = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Moyennes_Generales_S1")
        total_moyennes = cursor.fetchone()[0]
        if total_moyennes > 0:
            taux_reussite = f"{round((eleves_reussite / total_moyennes) * 100, 1)}%"
        
        conn.close()
        
        # Affichage des cartes statistiques
        st.markdown("<h2 style='text-align: center; margin: 2rem 0 1rem;'>Statistiques générales</h2>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                    <div style="font-size: 3rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                        <i class="fas fa-user-graduate"></i>
                        {nb_eleves}
                    </div>
                    <p style="font-size: 1.2rem; color: #2c3e50; margin: 0;">Élèves</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                    <div style="font-size: 3rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                        <i class="fas fa-chalkboard"></i>
                        {nb_classes}
                    </div>
                    <p style="font-size: 1.2rem; color: #2c3e50; margin: 0;">Classes</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                    <div style="font-size: 3rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                        <i class="fas fa-chart-line"></i>
                        {taux_reussite}
                    </div>
                    <p style="font-size: 1.2rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                    <div style="font-size: 2rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                        <i class="fas fa-calendar"></i>
                        {annee_scolaire}
                    </div>
                    <p style="font-size: 1.2rem; color: #2c3e50; margin: 0;">Année scolaire</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Section des fonctionnalités principales
    st.markdown("<h2 style='text-align: center; margin: 3rem 0 1rem;'>Modules principaux</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                <div style="font-size: 3rem; color: #3498db; margin-bottom: 1rem;">
                    <i class="fas fa-clipboard-list"></i>
                </div>
                <h3 style="color: #2c3e50; margin-bottom: 1rem;">Module Semestre 1</h3>
                <p style="color: #7f8c8d; margin-bottom: 1.5rem;">
                    Importez et analysez les résultats du premier semestre. Visualisez les performances et générez des rapports détaillés.
                </p>
                <a href="/?menu=Module+Semestre+1" style="background-color: #3498db; color: white; padding: 0.5rem 1rem; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Accéder
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                <div style="font-size: 3rem; color: #2ecc71; margin-bottom: 1rem;">
                    <i class="fas fa-clipboard-check"></i>
                </div>
                <h3 style="color: #2c3e50; margin-bottom: 1rem;">Module Semestre 2</h3>
                <p style="color: #7f8c8d; margin-bottom: 1.5rem;">
                    Gérez les résultats du second semestre. Comparez les performances avec le premier semestre et suivez les progrès.
                </p>
                <a href="/?menu=Module+Semestre+2" style="background-color: #2ecc71; color: white; padding: 0.5rem 1rem; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Accéder
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
                <div style="font-size: 3rem; color: #e74c3c; margin-bottom: 1rem;">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <h3 style="color: #2c3e50; margin-bottom: 1rem;">Module Général</h3>
                <p style="color: #7f8c8d; margin-bottom: 1.5rem;">
                    Analysez les tendances annuelles, comparez les semestres et prenez des décisions éclairées sur la base de statistiques complètes.
                </p>
                <a href="/?menu=Module+Général" style="background-color: #e74c3c; color: white; padding: 0.5rem 1rem; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Accéder
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Section d'information sur l'établissement
    if os.path.exists(DB_PATH):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        conn.close()
        
        if config:
            st.markdown("<h2 style='text-align: center; margin: 3rem 0 1rem;'>Informations de l'établissement</h2>", unsafe_allow_html=True)
            
            st.markdown(
                f"""
                <div style="background-color: white; padding: 2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                    <div style="display: flex; align-items: flex-start;">
                        <div style="font-size: 3rem; color: #34495e; margin-right: 1.5rem;">
                            <i class="fas fa-school"></i>
                        </div>
                        <div>
                            <h3 style="color: #2c3e50; margin-top: 0;">{config['nom_etablissement'] or 'Nom non défini'}</h3>
                            <p style="color: #7f8c8d; margin: 0.5rem 0;">
                                <strong>Adresse:</strong> {config['adresse'] or 'Non définie'}<br>
                                <strong>Téléphone:</strong> {config['telephone'] or 'Non défini'}<br>
                                <strong>Inspection d'académie:</strong> {config['inspection_academique'] or 'Non définie'}<br>
                                <strong>Inspection de l'éducation:</strong> {config['inspection_education'] or 'Non définie'}
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Pied de page
    st.markdown(
        f"""
        <div style="background-color: #2c3e50; padding: 1.5rem; border-radius: 5px; text-align: center; margin-top: 3rem;">
            <p style="color: white; margin: 0;">© 2025 LCAMS - Logiciel de Calcul et Analyse des Moyennes Semestrielles | Version {APP_VERSION}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Ajouter le CSS pour les icônes Font Awesome
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """,
        unsafe_allow_html=True
    )