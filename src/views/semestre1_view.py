import streamlit as st
import pandas as pd
import os
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from ..config import FICHIER_CENTRAL, DB_PATH, THEME_COLORS, APP_NAME, APP_VERSION
from ..utils.db_utils import get_db_connection
from ..utils.excel_utils import charger_et_nettoyer, sauvegarder_dans_fichier_central, to_excel
from ..utils.viz_utils import plot_distribution_moyennes, plot_repartition_par_sexe, plot_comparaison_disciplines

def show_semestre1_view():
    """Affiche le module Semestre 1 avec design amélioré"""
    
    # En-tête moderne avec navigation intégrée
    st.markdown(
        f"""
        <div style="background-color: {THEME_COLORS['primary']}; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="color: white; margin: 0;">📝 Module Semestre 1</h1>
                </div>
                <div>
                    <a href="/" target="_self" style="color: white; text-decoration: none; margin: 0 10px;">Accueil</a>
                    <a href="/?menu=Module+Semestre+2" target="_self" style="color: white; text-decoration: none; margin: 0 10px;">Semestre 2</a>
                    <a href="/?menu=Module+Général" target="_self" style="color: white; text-decoration: none; margin: 0 10px;">Module Général</a>
                    <a href="/?menu=Paramètres" target="_self" style="color: white; text-decoration: none; margin: 0 10px;">Paramètres</a>
                </div>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Navigation par onglets pour ce module
    tabs = st.tabs(["📊 Vue d'ensemble", "📈 Analyse Moyennes", "📋 Analyse Disciplines", "📑 Rapports", "📤 Importation"])
    
    # Contenu de chaque onglet
    with tabs[0]:
        show_overview()
    with tabs[1]:
        show_moyennes_analysis()
    with tabs[2]:
        show_disciplines_analysis()
    with tabs[3]:
        show_reports()
    with tabs[4]:
        show_import_interface()
    
    # Pied de page
    st.markdown(
        f"""
        <div style="background-color: #2c3e50; padding: 1rem; border-radius: 5px; text-align: center; margin-top: 2rem;">
            <p style="color: white; margin: 0;">© 2025 LCAMS - Semestre 1 | Version {APP_VERSION}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_overview():
    """Affiche la vue d'ensemble du semestre 1 avec design amélioré"""
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 1rem;'>Vue d'ensemble - Semestre 1</h2>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        h3 {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via l'onglet 'Importation'.")
        return
    
    # Récupérer l'année scolaire active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
    annee_result = cursor.fetchone()
    
    if not annee_result:
        st.warning("Aucune année scolaire active. Veuillez configurer l'année scolaire dans les paramètres.")
        return
    
    annee_scolaire = annee_result[0]
    
    # Afficher l'année scolaire active de manière élégante
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem; text-align: center;">
            <h3 style="margin: 0; color: {THEME_COLORS['primary']};">Année scolaire active: {annee_scolaire}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Récupérer les statistiques clés
    stats = {}
    
    # Nombre total d'élèves évalués au S1
    cursor.execute("""
        SELECT COUNT(DISTINCT ien) FROM Moyennes_Generales_S1 
        WHERE annee_scolaire = ?
    """, (annee_scolaire,))
    stats['total_eleves'] = cursor.fetchone()[0] or 0
    
    # Calculer la moyenne générale à partir de la base de données
    cursor.execute("""
        SELECT AVG(moyenne) FROM Moyennes_Generales_S1 
        WHERE annee_scolaire = ?
    """, (annee_scolaire,))
    stats['moyenne_generale'] = round(cursor.fetchone()[0] or 0, 2)
    
    # Nombre d'élèves ayant la moyenne
    cursor.execute("""
        SELECT COUNT(*) FROM Moyennes_Generales_S1 
        WHERE moyenne >= 10 AND annee_scolaire = ?
    """, (annee_scolaire,))
    stats['eleves_avec_moyenne'] = cursor.fetchone()[0] or 0
    
    # Taux de réussite
    if stats['total_eleves'] > 0:
        stats['taux_reussite'] = round((stats['eleves_avec_moyenne'] / stats['total_eleves']) * 100, 2)
    else:
        stats['taux_reussite'] = 0
    
    # Afficher les statistiques avec un design moderne
    st.markdown("<h3 style='margin-bottom: 1rem;'>Statistiques générales</h3>", unsafe_allow_html=True)
    
    # Utiliser des colonnes avec des cartes stylisées
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2.5rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                    <i class="fas fa-user-graduate"></i>
                    {stats['total_eleves']}
                </div>
                <p style="font-size: 1rem; color: #2c3e50; margin: 0;">Élèves évalués</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2.5rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                    <i class="fas fa-calculator"></i>
                    {stats['moyenne_generale']}
                </div>
                <p style="font-size: 1rem; color: #2c3e50; margin: 0;">Moyenne générale</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2.5rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                    <i class="fas fa-check-circle"></i>
                    {stats['eleves_avec_moyenne']}
                </div>
                <p style="font-size: 1rem; color: #2c3e50; margin: 0;">Élèves ≥ 10</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.5rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2.5rem; color: {THEME_COLORS['warning']}; margin-bottom: 0.5rem;">
                    <i class="fas fa-percentage"></i>
                    {stats['taux_reussite']}%
                </div>
                <p style="font-size: 1rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Récupérer les données par niveau
    cursor.execute("""
        SELECT n.libelle as niveau, COUNT(DISTINCT mg.ien) as nb_eleves, 
               AVG(mg.moyenne) as moyenne, 
               SUM(CASE WHEN mg.moyenne >= 10 THEN 1 ELSE 0 END) as nb_moyenne
        FROM Moyennes_Generales_S1 mg
        JOIN Eleves e ON mg.ien = e.ien
        JOIN Classes c ON e.id_classe = c.id
        JOIN Niveaux n ON c.id_niveau = n.id
        WHERE mg.annee_scolaire = ?
        GROUP BY n.libelle
        ORDER BY n.libelle
    """, (annee_scolaire,))
    
    niveaux_data = cursor.fetchall()
    conn.close()
    
    if niveaux_data:
        # Convertir en DataFrame pour faciliter l'affichage et les graphiques
        df_niveaux = pd.DataFrame(niveaux_data, columns=['niveau', 'nb_eleves', 'moyenne', 'nb_moyenne'])
        df_niveaux['taux'] = (df_niveaux['nb_moyenne'] / df_niveaux['nb_eleves'] * 100).round(2)
        df_niveaux['moyenne'] = df_niveaux['moyenne'].round(2)
        
        # Afficher un tableau moderne des statistiques par niveau
        st.markdown("<h3 style='margin: 1.5rem 0 1rem;'>Performance par niveau</h3>", unsafe_allow_html=True)
        
        st.markdown(
            """
            <style>
            .dataframe-container {
                background-color: white;
                padding: 1rem;
                border-radius: 5px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 1.5rem;
            }
            </style>
            <div class="dataframe-container">
            """,
            unsafe_allow_html=True
        )
        
        st.dataframe(
            df_niveaux,
            column_config={
                "niveau": "Niveau",
                "nb_eleves": st.column_config.NumberColumn("Nombre d'élèves", format="%d"),
                "moyenne": st.column_config.NumberColumn("Moyenne générale", format="%.2f"),
                "nb_moyenne": st.column_config.NumberColumn("Élèves ≥ 10", format="%d"),
                "taux": st.column_config.NumberColumn("Taux de réussite (%)", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Visualisation graphique modernisée des moyennes par niveau
        st.markdown("<h3 style='margin: 1.5rem 0 1rem;'>Moyennes par niveau</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique en barres des moyennes par niveau
            fig_moyennes = px.bar(
                df_niveaux, 
                x="niveau", 
                y="moyenne",
                color="niveau",
                labels={"niveau": "Niveau", "moyenne": "Moyenne générale"},
                title="Moyenne générale par niveau",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig_moyennes.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                legend_title_text="",
                xaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12),
                    range=[0, 20]
                )
            )
            
            st.plotly_chart(fig_moyennes, use_container_width=True)
        
        with col2:
            # Graphique en barres du taux de réussite par niveau
            fig_taux = px.bar(
                df_niveaux, 
                x="niveau", 
                y="taux",
                color="niveau",
                labels={"niveau": "Niveau", "taux": "Taux de réussite (%)"},
                title="Taux de réussite par niveau",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig_taux.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                legend_title_text="",
                xaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12),
                    range=[0, 100]
                )
            )
            
            st.plotly_chart(fig_taux, use_container_width=True)
        
        # Tableau d'honneur - Top 5 élèves
        st.markdown("<h3 style='margin: 1.5rem 0 1rem;'>Tableau d'honneur</h3>", unsafe_allow_html=True)
        
        conn = get_db_connection()
        query = """
            SELECT e.prenom, e.nom, n.libelle as niveau, c.libelle as classe, 
                   mg.moyenne, mg.rang
            FROM Moyennes_Generales_S1 mg
            JOIN Eleves e ON mg.ien = e.ien
            JOIN Classes c ON e.id_classe = c.id
            JOIN Niveaux n ON c.id_niveau = n.id
            WHERE mg.annee_scolaire = ?
            ORDER BY mg.moyenne DESC
            LIMIT 5
        """
        df_top = pd.read_sql_query(query, conn, params=(annee_scolaire,))
        conn.close()
        
        if not df_top.empty:
            st.markdown(
                """
                <style>
                .top-table {
                    background-color: white;
                    padding: 1rem;
                    border-radius: 5px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                </style>
                <div class="top-table">
                """,
                unsafe_allow_html=True
            )
            
            # Ajouter une colonne "rang honorifique"
            df_top.insert(0, 'rang_honor', range(1, len(df_top) + 1))
            
            st.dataframe(
                df_top,
                column_config={
                    "rang_honor": st.column_config.NumberColumn("№", format="%d"),
                    "prenom": "Prénom",
                    "nom": "Nom",
                    "niveau": "Niveau",
                    "classe": "Classe",
                    "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                    "rang": st.column_config.NumberColumn("Rang en classe", format="%d")
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Lien vers l'analyse détaillée
        st.markdown(
            """
            <div style="text-align: center; margin-top: 2rem;">
                <p>Pour des analyses plus approfondies, consultez les onglets d'analyse spécifiques.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Aucune donnée disponible pour l'année scolaire actuelle.")

    # Ajouter le CSS pour les icônes Font Awesome
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """,
        unsafe_allow_html=True
    )


def show_moyennes_analysis():
    """Affiche l'analyse des moyennes générales du semestre 1 avec un design amélioré"""
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Analyse des moyennes - Semestre 1</h2>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        h3 {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via l'onglet 'Importation'.")
        return
    
    # Récupérer l'année scolaire active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
    annee_result = cursor.fetchone()
    
    if not annee_result:
        st.warning("Aucune année scolaire active. Veuillez configurer l'année scolaire dans les paramètres.")
        return
    
    annee_scolaire = annee_result[0]
    
    # Récupérer les niveaux disponibles
    cursor.execute("""
        SELECT DISTINCT n.id, n.libelle
        FROM Niveaux n
        JOIN Classes c ON n.id = c.id_niveau
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE mg.annee_scolaire = ? AND n.etat = 'actif'
        ORDER BY n.libelle
    """, (annee_scolaire,))
    
    niveaux = cursor.fetchall()
    
    if not niveaux:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Créer un conteneur pour les filtres avec style amélioré
    st.markdown(
        """
        <style>
        .filter-container {
            background-color: white;
            padding: 1.2rem;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        </style>
        <div class="filter-container">
        <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;">Filtrer les données</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    col1, col2 = st.columns(2)
    
    with col1:
        selected_niveau = st.selectbox(
            "Sélectionner un niveau",
            options=list(niveau_options.keys()),
            key="niveau_select_moyennes"
        )
    
    niveau_id = niveau_options[selected_niveau]
    
    # Récupérer les classes du niveau sélectionné
    cursor.execute("""
        SELECT DISTINCT c.id, c.libelle
        FROM Classes c
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE c.id_niveau = ? AND mg.annee_scolaire = ? AND c.etat = 'actif'
        ORDER BY c.libelle
    """, (niveau_id, annee_scolaire))
    
    classes = cursor.fetchall()
    
    if not classes:
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(f"Aucune classe avec des données pour le niveau {selected_niveau}.")
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    
    with col2:
        selected_classe = st.selectbox(
            "Sélectionner une classe",
            options=list(classe_options.keys()),
            key="classe_select_moyennes"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    classe_id = classe_options[selected_classe]
    
    # Récupérer les données de la classe sélectionnée
    query = """
        SELECT e.ien, e.prenom, e.nom, e.sexe, mg.moyenne, mg.rang, 
               mg.retard, mg.absence, mg.conseil_discipline, mg.appreciation
        FROM Eleves e
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE e.id_classe = ? AND mg.annee_scolaire = ?
        ORDER BY mg.rang
    """
    
    df_classe = pd.read_sql_query(query, conn, params=(classe_id, annee_scolaire))
    conn.close()
    
    if df_classe.empty:
        st.info(f"Aucune donnée disponible pour la classe {selected_classe}.")
        return
    
    # Statistiques de la classe dans un conteneur stylisé
    st.markdown(
        f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques de la classe {selected_niveau} {selected_classe}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Calcul des statistiques
    stats = {
        'effectif': len(df_classe),
        'moyenne_classe': round(df_classe['moyenne'].mean(), 2),
        'mediane': round(df_classe['moyenne'].median(), 2),
        'ecart_type': round(df_classe['moyenne'].std(), 2),
        'min': round(df_classe['moyenne'].min(), 2),
        'max': round(df_classe['moyenne'].max(), 2),
        'nb_moyenne': (df_classe['moyenne'] >= 10).sum(),
    }
    
    stats['taux_reussite'] = round((stats['nb_moyenne'] / stats['effectif']) * 100, 2) if stats['effectif'] > 0 else 0
    
    # Afficher les statistiques avec des cartes améliorées
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                    {stats['effectif']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Effectif</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                    {stats['moyenne_classe']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Moyenne de classe</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                    {stats['nb_moyenne']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Élèves ≥ 10</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['warning']}; margin-bottom: 0.5rem;">
                    {stats['taux_reussite']}%
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                    {stats['mediane']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Médiane</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                    {stats['ecart_type']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Écart-type</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['danger']}; margin-bottom: 0.5rem;">
                    {stats['min']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Min</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                    {stats['max']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Max</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Tableau des élèves avec style amélioré
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Liste des élèves</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Ajouter une colonne pour la mention
    df_classe['mention'] = df_classe['moyenne'].apply(lambda x: 
        "Excellent" if x >= 16 else
        "Très Bien" if x >= 14 else
        "Bien" if x >= 12 else
        "Assez Bien" if x >= 10 else
        "Insuffisant"
    )
    
    # Ajouter une colonne de couleur pour les mentions
    df_classe['color'] = df_classe['mention'].apply(lambda x: 
        "#28a745" if x == "Excellent" else
        "#17a2b8" if x == "Très Bien" else
        "#007bff" if x == "Bien" else
        "#6c757d" if x == "Assez Bien" else
        "#dc3545"
    )
    
    # Afficher le tableau
    st.dataframe(
        df_classe,
        column_config={
            "ien": st.column_config.TextColumn("IEN"),
            "prenom": "Prénom",
            "nom": "Nom",
            "sexe": "Sexe",
            "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
            "rang": "Rang",
            "mention": st.column_config.TextColumn("Mention"),
            "retard": "Retards",
            "absence": "Absences",
            "conseil_discipline": "Conseil de discipline",
            "appreciation": "Appréciation",
            "color": None  # Cacher la colonne de couleur
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Visualisations avec un design amélioré
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Visualisations</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    # Distribution des moyennes
    with col1:
        fig = plot_distribution_moyennes(df_classe, f"Distribution des moyennes - {selected_classe}", column="moyenne")
        
        # Améliorer le design du graphique
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                title=dict(font=dict(size=14)),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title=dict(font=dict(size=14)),
                tickfont=dict(size=12)
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Répartition par sexe
    with col2:
        if 'sexe' in df_classe.columns:
            fig = plot_repartition_par_sexe(df_classe, "moyenne", f"Moyennes par sexe - {selected_classe}")
            
            # Améliorer le design du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de sexe non disponibles pour cette analyse.")
    
    # Analyse des élèves en difficulté
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Élèves en difficulté</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    difficulte = df_classe[df_classe['moyenne'] < 10].sort_values('moyenne')
    
    if not difficulte.empty:
        st.dataframe(
            difficulte[['prenom', 'nom', 'sexe', 'moyenne', 'rang']],
            column_config={
                "prenom": "Prénom",
                "nom": "Nom",
                "sexe": "Sexe",
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "rang": "Rang"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Ajouter un graphique pour les élèves en difficulté
        if len(difficulte) > 1:
            st.markdown("<h4 style='margin: 1.5rem 0 1rem;'>Graphique des élèves en difficulté</h4>", unsafe_allow_html=True)
            
            fig = px.bar(
                difficulte,
                x=difficulte['prenom'] + " " + difficulte['nom'],
                y="moyenne",
                labels={"x": "Élève", "moyenne": "Moyenne"},
                title="Moyennes des élèves en difficulté",
                color_discrete_sequence=[THEME_COLORS['danger']]
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title="Élève",
                    titlefont=dict(size=14),
                    tickfont=dict(size=10)
                ),
                yaxis=dict(
                    title="Moyenne",
                    titlefont=dict(size=14),
                    tickfont=dict(size=12),
                    range=[0, 10]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Aucun élève en difficulté (tous les élèves ont une moyenne ≥ 10).")
    
    # Options d'export
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Exporter les données</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Exporter en Excel
        excel_data = to_excel(df_classe, pd.DataFrame())
        st.download_button(
            label="📥 Télécharger en Excel",
            data=excel_data,
            file_name=f"{selected_niveau}_{selected_classe}_moyennes_S1.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # Exporter en CSV
        csv_data = df_classe.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv_data,
            file_name=f"{selected_niveau}_{selected_classe}_moyennes_S1.csv",
            mime="text/csv"
        )


def show_disciplines_analysis():
    """Affiche l'analyse par discipline du semestre 1 avec design amélioré"""
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Analyse par discipline - Semestre 1</h2>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        h3 {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via l'onglet 'Importation'.")
        return
    
    # Récupérer l'année scolaire active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
    annee_result = cursor.fetchone()
    
    if not annee_result:
        st.warning("Aucune année scolaire active. Veuillez configurer l'année scolaire dans les paramètres.")
        return
    
    annee_scolaire = annee_result[0]
    
    # Récupérer les niveaux disponibles
    cursor.execute("""
        SELECT DISTINCT n.id, n.libelle
        FROM Niveaux n
        JOIN Classes c ON n.id = c.id_niveau
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Notes_S1 notes ON e.ien = notes.ien
        WHERE notes.annee_scolaire = ? AND n.etat = 'actif'
        ORDER BY n.libelle
    """, (annee_scolaire,))
    
    niveaux = cursor.fetchall()
    
    if not niveaux:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Créer un conteneur pour les filtres avec style amélioré
    st.markdown(
        """
        <style>
        .filter-container {
            background-color: white;
            padding: 1.2rem;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        </style>
        <div class="filter-container">
        <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;">Filtrer les données</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_niveau = st.selectbox(
            "Sélectionner un niveau",
            options=list(niveau_options.keys()),
            key="niveau_select_disciplines"
        )
    
    niveau_id = niveau_options[selected_niveau]
    
    # Récupérer les classes du niveau sélectionné
    cursor.execute("""
        SELECT DISTINCT c.id, c.libelle
        FROM Classes c
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Notes_S1 notes ON e.ien = notes.ien
        WHERE c.id_niveau = ? AND notes.annee_scolaire = ? AND c.etat = 'actif'
        ORDER BY c.libelle
    """, (niveau_id, annee_scolaire))
    
    classes = cursor.fetchall()
    
    if not classes:
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(f"Aucune classe avec des données pour le niveau {selected_niveau}.")
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    
    with col2:
        selected_classe = st.selectbox(
            "Sélectionner une classe",
            options=list(classe_options.keys()),
            key="classe_select_disciplines"
        )
    
    classe_id = classe_options[selected_classe]
    
    # Récupérer les disciplines disponibles pour cette classe
    cursor.execute("""
        SELECT DISTINCT d.id, d.libelle
        FROM Disciplines d
        JOIN Notes_S1 notes ON d.id = notes.id_discipline
        JOIN Eleves e ON notes.ien = e.ien
        WHERE e.id_classe = ? AND notes.annee_scolaire = ?
        ORDER BY d.libelle
    """, (classe_id, annee_scolaire))
    
    disciplines = cursor.fetchall()
    
    if not disciplines:
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(f"Aucune donnée de discipline disponible pour la classe {selected_classe}.")
        return
    
    # Sélecteur de discipline
    discipline_options = {discipline['libelle']: discipline['id'] for discipline in disciplines}
    
    with col3:
        selected_discipline = st.selectbox(
            "Sélectionner une discipline",
            options=list(discipline_options.keys()),
            key="discipline_select"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    discipline_id = discipline_options[selected_discipline]
    
    # Récupérer les notes de la discipline sélectionnée
    query = """
        SELECT e.ien, e.prenom, e.nom, e.sexe, 
               notes.moy_dd, notes.comp_d, notes.moy_d, notes.rang_d
        FROM Eleves e
        JOIN Notes_S1 notes ON e.ien = notes.ien
        WHERE e.id_classe = ? AND notes.id_discipline = ? AND notes.annee_scolaire = ?
        ORDER BY notes.rang_d
    """
    
    df_notes = pd.read_sql_query(query, conn, params=(classe_id, discipline_id, annee_scolaire))
    
    # Récupérer les moyennes générales pour avoir une vue complète
    query_moy = """
        SELECT e.ien, mg.moyenne as moyenne_generale, mg.rang as rang_general
        FROM Eleves e
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE e.id_classe = ? AND mg.annee_scolaire = ?
    """
    
    df_moy = pd.read_sql_query(query_moy, conn, params=(classe_id, annee_scolaire))
    
    conn.close()
    
    # Fusionner les données
    df_discipline = pd.merge(df_notes, df_moy, on='ien')
    
    if df_discipline.empty:
        st.info(f"Aucune donnée disponible pour la discipline {selected_discipline}.")
        return
    
    # Statistiques de la discipline dans un conteneur stylisé
    st.markdown(
        f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques de {selected_discipline} - {selected_niveau} {selected_classe}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Calcul des statistiques
    stats = {
        'effectif': len(df_discipline),
        'moyenne_discipline': round(df_discipline['moy_d'].mean(), 2),
        'mediane': round(df_discipline['moy_d'].median(), 2),
        'ecart_type': round(df_discipline['moy_d'].std(), 2),
        'min': round(df_discipline['moy_d'].min(), 2),
        'max': round(df_discipline['moy_d'].max(), 2),
        'nb_moyenne': (df_discipline['moy_d'] >= 10).sum(),
    }
    
    stats['taux_reussite'] = round((stats['nb_moyenne'] / stats['effectif']) * 100, 2) if stats['effectif'] > 0 else 0
    
    # Afficher les statistiques avec des cartes améliorées
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                    {stats['effectif']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Effectif</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                    {stats['moyenne_discipline']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Moyenne de discipline</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                    {stats['nb_moyenne']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Élèves ≥ 10</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['warning']}; margin-bottom: 0.5rem;">
                    {stats['taux_reussite']}%
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                    {stats['mediane']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Médiane</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                    {stats['ecart_type']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Écart-type</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['danger']}; margin-bottom: 0.5rem;">
                    {stats['min']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Min</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                    {stats['max']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Max</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Tableau des notes avec style amélioré
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Notes des élèves</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Ajouter une colonne pour la mention
    df_discipline['mention'] = df_discipline['moy_d'].apply(lambda x: 
        "Excellent" if x >= 16 else
        "Très Bien" if x >= 14 else
        "Bien" if x >= 12 else
        "Assez Bien" if x >= 10 else
        "Insuffisant"
    )
    
    # Afficher le tableau
    st.dataframe(
        df_discipline,
        column_config={
            "ien": st.column_config.TextColumn("IEN"),
            "prenom": "Prénom",
            "nom": "Nom",
            "sexe": "Sexe",
            "moy_dd": st.column_config.NumberColumn("Moy. Devoirs", format="%.2f"),
            "comp_d": st.column_config.NumberColumn("Composition", format="%.2f"),
            "moy_d": st.column_config.NumberColumn("Moyenne", format="%.2f"),
            "rang_d": "Rang Discipline",
            "moyenne_generale": st.column_config.NumberColumn("Moyenne Générale", format="%.2f"),
            "rang_general": "Rang Général",
            "mention": "Mention"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Visualisations avec un design amélioré
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Visualisations</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    # Distribution des notes
    with col1:
        fig = px.histogram(
            df_discipline, 
            x="moy_d", 
            nbins=20,
            color_discrete_sequence=[THEME_COLORS['success']],
            title=f"Distribution des notes - {selected_discipline}"
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                title="Note",
                titlefont=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title="Nombre d'élèves",
                titlefont=dict(size=14),
                tickfont=dict(size=12)
            ),
            bargap=0.1
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Répartition par sexe
    with col2:
        if 'sexe' in df_discipline.columns:
            fig = plot_repartition_par_sexe(df_discipline, "moy_d", f"Notes par sexe - {selected_discipline}")
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de sexe non disponibles pour cette analyse.")
    
    # Analyse comparative avec la moyenne générale
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Comparaison avec la moyenne générale</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Créer un graphique comparatif
    fig = go.Figure()
    
    # Trier par rang général pour une meilleure visualisation
    df_tri = df_discipline.sort_values('rang_general')
    
    # Ajouter les deux courbes
    fig.add_trace(go.Scatter(
        x=[f"{prenom} {nom}" for prenom, nom in zip(df_tri['prenom'], df_tri['nom'])],
        y=df_tri['moy_d'],
        mode='lines+markers',
        name=f'{selected_discipline}',
        line=dict(color=THEME_COLORS['success'], width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=[f"{prenom} {nom}" for prenom, nom in zip(df_tri['prenom'], df_tri['nom'])],
        y=df_tri['moyenne_generale'],
        mode='lines+markers',
        name='Moyenne générale',
        line=dict(color=THEME_COLORS['primary'], width=2)
    ))
    
    # Personnaliser le graphique
    fig.update_layout(
        title=f"Comparaison entre {selected_discipline} et la moyenne générale",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            title="Élèves",
            titlefont=dict(size=14),
            tickfont=dict(size=10),
            tickangle=45
        ),
        yaxis=dict(
            title="Note",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            range=[0, 20]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)
    
    # Options d'export
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Exporter les données</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Exporter en Excel
        excel_data = to_excel(df_discipline, pd.DataFrame())
        st.download_button(
            label="📥 Télécharger en Excel",
            data=excel_data,
            file_name=f"{selected_niveau}_{selected_classe}_{selected_discipline}_S1.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # Exporter en CSV
        csv_data = df_discipline.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv_data,
            file_name=f"{selected_niveau}_{selected_classe}_{selected_discipline}_S1.csv",
            mime="text/csv"
        )


def show_reports():
    """Affiche la page de génération de rapports du semestre 1 avec design amélioré"""
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Rapports - Semestre 1</h2>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        h3 {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via l'onglet 'Importation'.")
        return
    
    # Récupérer l'année scolaire active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
    annee_result = cursor.fetchone()
    
    if not annee_result:
        st.warning("Aucune année scolaire active. Veuillez configurer l'année scolaire dans les paramètres.")
        return
    
    annee_scolaire = annee_result[0]
    
    # Afficher l'année scolaire active de manière élégante
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem; text-align: center;">
            <h3 style="margin: 0; color: {THEME_COLORS['primary']};">Année scolaire: {annee_scolaire}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Types de rapports disponibles avec interface moderne
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Sélectionner un type de rapport</h3>
        """,
        unsafe_allow_html=True
    )
    
    report_types = {
        "Rapport de classe": {
            "icon": "fas fa-chalkboard-teacher",
            "description": "Statistiques complètes pour une classe spécifique"
        },
        "Rapport par discipline": {
            "icon": "fas fa-book",
            "description": "Analyse détaillée d'une discipline particulière"
        },
        "Tableau d'honneur": {
            "icon": "fas fa-trophy",
            "description": "Liste des meilleurs élèves par classe ou niveau"
        },
        "Rapport statistique global": {
            "icon": "fas fa-chart-pie",
            "description": "Statistiques générales pour l'ensemble de l'établissement"
        }
    }
    
    # Afficher les options de rapport sous forme de cartes
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            f"""
            📊 Rapport de classe
            """,
            help="Statistiques complètes pour une classe spécifique",
            use_container_width=True
        ):
            selected_report = "Rapport de classe"
        
        if st.button(
            f"""
            🏆 Tableau d'honneur
            """,
            help="Liste des meilleurs élèves par classe ou niveau",
            use_container_width=True
        ):
            selected_report = "Tableau d'honneur"
    
    with col2:
        if st.button(
            f"""
            📚 Rapport par discipline
            """,
            help="Analyse détaillée d'une discipline particulière",
            use_container_width=True
        ):
            selected_report = "Rapport par discipline"
        
        if st.button(
            f"""
            📈 Rapport statistique global
            """,
            help="Statistiques générales pour l'ensemble de l'établissement",
            use_container_width=True
        ):
            selected_report = "Rapport statistique global"
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sélection de rapport avec radio plus visuel
    selected_report = st.radio(
        "Type de rapport",
        list(report_types.keys()),
        format_func=lambda x: f"{x}",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown(
        f"""
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 0.5rem;">{selected_report}</h3>
            <p style="margin-bottom: 0;">{report_types[selected_report]["description"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Générer le rapport correspondant
    if selected_report == "Rapport de classe":
        generate_class_report(conn, annee_scolaire)
    elif selected_report == "Rapport par discipline":
        generate_discipline_report(conn, annee_scolaire)
    elif selected_report == "Tableau d'honneur":
        generate_honor_roll(conn, annee_scolaire)
    elif selected_report == "Rapport statistique global":
        generate_global_stats(conn, annee_scolaire)
    
    conn.close()
    
    # Ajouter le CSS pour les icônes Font Awesome
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """,
        unsafe_allow_html=True
    )


def generate_class_report(conn, annee_scolaire):
    """Génère un rapport de classe avec design amélioré"""
    
    # Récupérer les niveaux disponibles
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT n.id, n.libelle
        FROM Niveaux n
        JOIN Classes c ON n.id = c.id_niveau
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE mg.annee_scolaire = ? AND n.etat = 'actif'
        ORDER BY n.libelle
    """, (annee_scolaire,))
    
    niveaux = cursor.fetchall()
    
    if not niveaux:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Créer un conteneur pour les filtres
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;">Sélectionner une classe</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    col1, col2 = st.columns(2)
    
    with col1:
        selected_niveau = st.selectbox(
            "Niveau",
            options=list(niveau_options.keys()),
            key="niveau_select_report"
        )
    
    niveau_id = niveau_options[selected_niveau]
    
    # Récupérer les classes du niveau sélectionné
    cursor.execute("""
        SELECT DISTINCT c.id, c.libelle
        FROM Classes c
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE c.id_niveau = ? AND mg.annee_scolaire = ? AND c.etat = 'actif'
        ORDER BY c.libelle
    """, (niveau_id, annee_scolaire))
    
    classes = cursor.fetchall()
    
    if not classes:
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(f"Aucune classe avec des données pour le niveau {selected_niveau}.")
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    
    with col2:
        selected_classe = st.selectbox(
            "Classe",
            options=list(classe_options.keys()),
            key="classe_select_report"
        )
    
    classe_id = classe_options[selected_classe]
    
    # Options supplémentaires
    col1, col2 = st.columns(2)
    
    with col1:
        include_disciplines = st.checkbox("Inclure les détails par discipline", value=True)
    
    with col2:
        include_charts = st.checkbox("Inclure les graphiques", value=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton pour générer le rapport
    if st.button("Générer le rapport", use_container_width=True, type="primary"):
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Rapport de classe - {selected_niveau} {selected_classe} - Semestre 1</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Récupérer les informations de l'établissement
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem;">
                    <p style="margin: 0.3rem 0;"><strong>Établissement:</strong> {config['nom_etablissement'] or 'Non défini'}</p>
                    <p style="margin: 0.3rem 0;"><strong>Année scolaire:</strong> {annee_scolaire}</p>
                    <p style="margin: 0.3rem 0;"><strong>Semestre:</strong> 1</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Récupérer les données de la classe
        query = """
            SELECT e.ien, e.prenom, e.nom, e.sexe, mg.moyenne, mg.rang, 
                mg.retard, mg.absence, mg.conseil_discipline, mg.appreciation
            FROM Eleves e
            JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
            WHERE e.id_classe = ? AND mg.annee_scolaire = ?
            ORDER BY mg.rang
        """
        
        df_classe = pd.read_sql_query(query, conn, params=(classe_id, annee_scolaire))
        
        if df_classe.empty:
            st.info(f"Aucune donnée disponible pour la classe {selected_classe}.")
            return
        
        # Statistiques de la classe
        stats = {
            'effectif': len(df_classe),
            'moyenne_classe': round(df_classe['moyenne'].mean(), 2),
            'mediane': round(df_classe['moyenne'].median(), 2),
            'ecart_type': round(df_classe['moyenne'].std(), 2),
            'min': round(df_classe['moyenne'].min(), 2),
            'max': round(df_classe['moyenne'].max(), 2),
            'nb_moyenne': (df_classe['moyenne'] >= 10).sum(),
        }
        
        stats['taux_reussite'] = round((stats['nb_moyenne'] / stats['effectif']) * 100, 2) if stats['effectif'] > 0 else 0
        
        # Afficher les statistiques avec un design amélioré
        st.markdown(
            """
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques générales</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                        {stats['effectif']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Effectif</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                        {stats['moyenne_classe']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Moyenne de classe</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                        {stats['nb_moyenne']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Élèves ≥ 10</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['warning']}; margin-bottom: 0.5rem;">
                        {stats['taux_reussite']}%
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                        {stats['mediane']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Médiane</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['secondary']}; margin-bottom: 0.5rem;">
                        {stats['ecart_type']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Écart-type</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['danger']}; margin-bottom: 0.5rem;">
                        {stats['min']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Min</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                        {stats['max']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Max</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Ajouter une colonne pour la mention
        df_classe['mention'] = df_classe['moyenne'].apply(lambda x: 
            "Excellent" if x >= 16 else
            "Très Bien" if x >= 14 else
            "Bien" if x >= 12 else
            "Assez Bien" if x >= 10 else
            "Insuffisant"
        )
        
        # Tableau des élèves
        st.markdown(
            """
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Liste des élèves</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.dataframe(
            df_classe,
            column_config={
                "ien": st.column_config.TextColumn("IEN"),
                "prenom": "Prénom",
                "nom": "Nom",
                "sexe": "Sexe",
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "rang": "Rang",
                "mention": st.column_config.TextColumn("Mention"),
                "retard": "Retards",
                "absence": "Absences",
                "conseil_discipline": "Conseil de discipline",
                "appreciation": "Appréciation"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Inclure les détails par discipline si demandé
        if include_disciplines:
            st.markdown(
                """
                <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                    <h3 style="margin-top: 0; margin-bottom: 1rem;">Détails par discipline</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Récupérer les disciplines disponibles
            cursor.execute("""
                SELECT DISTINCT d.id, d.libelle
                FROM Disciplines d
                JOIN Notes_S1 notes ON d.id = notes.id_discipline
                JOIN Eleves e ON notes.ien = e.ien
                WHERE e.id_classe = ? AND notes.annee_scolaire = ?
                ORDER BY d.libelle
            """, (classe_id, annee_scolaire))
            
            disciplines = cursor.fetchall()
            
            for discipline in disciplines:
                st.markdown(f"<h4 style='margin: 1.5rem 0 1rem;'>{discipline['libelle']}</h4>", unsafe_allow_html=True)
                
                # Récupérer les notes de cette discipline
                query = """
                    SELECT e.prenom, e.nom, notes.moy_dd, notes.comp_d, notes.moy_d, notes.rang_d
                    FROM Eleves e
                    JOIN Notes_S1 notes ON e.ien = notes.ien
                    WHERE e.id_classe = ? AND notes.id_discipline = ? AND notes.annee_scolaire = ?
                    ORDER BY notes.rang_d
                """
                
                df_disc = pd.read_sql_query(query, conn, params=(classe_id, discipline['id'], annee_scolaire))
                
                if not df_disc.empty:
                    moyenne_disc = round(df_disc['moy_d'].mean(), 2)
                    taux_reussite_disc = round((df_disc[df_disc['moy_d'] >= 10].shape[0] / df_disc.shape[0]) * 100, 2)
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Moyenne", moyenne_disc)
                    col2.metric("Taux de réussite", f"{taux_reussite_disc}%")
                    
                    st.dataframe(
                        df_disc,
                        column_config={
                            "prenom": "Prénom",
                            "nom": "Nom",
                            "moy_dd": st.column_config.NumberColumn("Moy. Devoirs", format="%.2f"),
                            "comp_d": st.column_config.NumberColumn("Composition", format="%.2f"),
                            "moy_d": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                            "rang_d": "Rang"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
        
        # Inclure les graphiques si demandé
        if include_charts:
            st.markdown(
                """
                <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                    <h3 style="margin-top: 0; margin-bottom: 1rem;">Visualisations</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2)
            
            # Distribution des moyennes
            with col1:
                fig = plot_distribution_moyennes(df_classe, f"Distribution des moyennes - {selected_classe}", column="moyenne")
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Arial", size=12),
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis=dict(
                        title=dict(font=dict(size=14)),
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        title=dict(font=dict(size=14)),
                        tickfont=dict(size=12)
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Répartition par sexe
            with col2:
                if 'sexe' in df_classe.columns:
                    fig = plot_repartition_par_sexe(df_classe, "moyenne", f"Moyennes par sexe - {selected_classe}")
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Arial", size=12),
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis=dict(
                            title=dict(font=dict(size=14)),
                            tickfont=dict(size=12)
                        ),
                        yaxis=dict(
                            title=dict(font=dict(size=14)),
                            tickfont=dict(size=12)
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Données de sexe non disponibles pour cette analyse.")
               # Bouton pour télécharger le rapport en Excel
        st.markdown(
            """
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Télécharger le rapport</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Préparer les données pour le fichier Excel
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Feuille des moyennes générales
            df_classe.to_excel(writer, sheet_name='Moyennes_Generales', index=False)
            
            # Feuille des statistiques
            stats_df = pd.DataFrame({
                'Métrique': ['Effectif', 'Moyenne de classe', 'Élèves ≥ 10', 'Taux de réussite', 
                             'Médiane', 'Écart-type', 'Min', 'Max'],
                'Valeur': [stats['effectif'], stats['moyenne_classe'], stats['nb_moyenne'], f"{stats['taux_reussite']}%",
                          stats['mediane'], stats['ecart_type'], stats['min'], stats['max']]
            })
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
            
            # Feuilles des disciplines
            if include_disciplines:
                for discipline in disciplines:
                    query = """
                        SELECT e.prenom, e.nom, notes.moy_dd, notes.comp_d, notes.moy_d, notes.rang_d
                        FROM Eleves e
                        JOIN Notes_S1 notes ON e.ien = notes.ien
                        WHERE e.id_classe = ? AND notes.id_discipline = ? AND notes.annee_scolaire = ?
                        ORDER BY notes.rang_d
                    """
                    
                    df_disc = pd.read_sql_query(query, conn, params=(classe_id, discipline['id'], annee_scolaire))
                    
                    if not df_disc.empty:
                        # Limiter le nom de la feuille à 31 caractères (limite Excel)
                        sheet_name = discipline['libelle']
                        if len(sheet_name) > 31:
                            sheet_name = sheet_name[:28] + "..."
                        
                        df_disc.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Proposer le téléchargement
        st.download_button(
            label="📥 Télécharger le rapport Excel",
            data=output.getvalue(),
            file_name=f"Rapport_{selected_niveau}_{selected_classe}_S1.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def generate_discipline_report(conn, annee_scolaire):
    """Génère un rapport par discipline avec design amélioré"""
    
    # Récupérer les disciplines disponibles
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT d.id, d.libelle
        FROM Disciplines d
        JOIN Notes_S1 notes ON d.id = notes.id_discipline
        WHERE notes.annee_scolaire = ?
        ORDER BY d.libelle
    """, (annee_scolaire,))
    
    disciplines = cursor.fetchall()
    
    if not disciplines:
        st.info(f"Aucune discipline avec des données pour l'année scolaire {annee_scolaire}.")
        return
    
    # Créer un conteneur pour la sélection de discipline
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;">Sélectionner une discipline</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Sélecteur de discipline
    discipline_options = {discipline['libelle']: discipline['id'] for discipline in disciplines}
    
    selected_discipline = st.selectbox(
        "Discipline",
        options=list(discipline_options.keys()),
        key="discipline_select_report"
    )
    
    discipline_id = discipline_options[selected_discipline]
    
    # Options supplémentaires
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analyze_by_level = st.checkbox("Analyser par niveau", value=True)
    
    with col2:
        analyze_by_gender = st.checkbox("Analyser par sexe", value=True)
    
    with col3:
        include_charts = st.checkbox("Inclure les graphiques", value=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton pour générer le rapport
    if st.button("Générer le rapport", use_container_width=True, type="primary"):
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Rapport de discipline - {selected_discipline} - Semestre 1</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Récupérer les informations de l'établissement
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem;">
                    <p style="margin: 0.3rem 0;"><strong>Établissement:</strong> {config['nom_etablissement'] or 'Non défini'}</p>
                    <p style="margin: 0.3rem 0;"><strong>Année scolaire:</strong> {annee_scolaire}</p>
                    <p style="margin: 0.3rem 0;"><strong>Semestre:</strong> 1</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Récupérer les statistiques globales de la discipline
        cursor.execute("""
            SELECT COUNT(DISTINCT notes.ien) as nb_eleves,
                   AVG(notes.moy_d) as moyenne,
                   COUNT(CASE WHEN notes.moy_d >= 10 THEN 1 END) as nb_moyenne
            FROM Notes_S1 notes
            WHERE notes.id_discipline = ? AND notes.annee_scolaire = ?
        """, (discipline_id, annee_scolaire))
        
        stats_global = cursor.fetchone()
        
        if not stats_global or stats_global['nb_eleves'] == 0:
            st.info(f"Aucune donnée disponible pour la discipline {selected_discipline}.")
            return
        
        # Calculer le taux de réussite
        taux_reussite = (stats_global['nb_moyenne'] / stats_global['nb_eleves']) * 100
        
        # Afficher les statistiques globales avec un design amélioré
        st.markdown(
            """
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques globales</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                        {stats_global['nb_eleves']}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Nombre d'élèves</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                        {round(stats_global['moyenne'], 2)}
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Moyenne générale</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                        {round(taux_reussite, 2)}%
                    </div>
                    <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Analyse par niveau si demandée
        if analyze_by_level:
            st.markdown(
                """
                <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                    <h3 style="margin-top: 0; margin-bottom: 1rem;">Analyse par niveau</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Récupérer les données par niveau
            query = """
                SELECT n.libelle as niveau, COUNT(DISTINCT notes.ien) as nb_eleves,
                       AVG(notes.moy_d) as moyenne,
                       COUNT(CASE WHEN notes.moy_d >= 10 THEN 1 END) as nb_moyenne
                FROM Notes_S1 notes
                JOIN Eleves e ON notes.ien = e.ien
                JOIN Classes c ON e.id_classe = c.id
                JOIN Niveaux n ON c.id_niveau = n.id
                WHERE notes.id_discipline = ? AND notes.annee_scolaire = ?
                GROUP BY n.libelle
                ORDER BY n.libelle
            """
            
            df_niveaux = pd.read_sql_query(query, conn, params=(discipline_id, annee_scolaire))
            
            # Calculer le taux de réussite
            df_niveaux['taux_reussite'] = (df_niveaux['nb_moyenne'] / df_niveaux['nb_eleves'] * 100).round(2)
            df_niveaux['moyenne'] = df_niveaux['moyenne'].round(2)
            
            # Afficher le tableau
            st.dataframe(
                df_niveaux,
                column_config={
                    "niveau": "Niveau",
                    "nb_eleves": st.column_config.NumberColumn("Nombre d'élèves", format="%d"),
                    "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                    "nb_moyenne": st.column_config.NumberColumn("Élèves ≥ 10", format="%d"),
                    "taux_reussite": st.column_config.NumberColumn("Taux de réussite (%)", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Graphique si demandé
            if include_charts:
                fig = px.bar(
                    df_niveaux,
                    x="niveau",
                    y="moyenne",
                    color="niveau",
                    title=f"Moyenne par niveau - {selected_discipline}",
                    labels={"niveau": "Niveau", "moyenne": "Moyenne"},
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Arial", size=12),
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend_title_text="",
                    xaxis=dict(
                        title=dict(font=dict(size=14)),
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        title=dict(font=dict(size=14)),
                        tickfont=dict(size=12),
                        range=[0, 20]
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Analyse par sexe si demandée
        if analyze_by_gender:
            st.markdown(
                """
                <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                    <h3 style="margin-top: 0; margin-bottom: 1rem;">Analyse par sexe</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Récupérer les données par sexe
            query = """
                SELECT e.sexe, COUNT(DISTINCT notes.ien) as nb_eleves,
                       AVG(notes.moy_d) as moyenne,
                       COUNT(CASE WHEN notes.moy_d >= 10 THEN 1 END) as nb_moyenne
                FROM Notes_S1 notes
                JOIN Eleves e ON notes.ien = e.ien
                WHERE notes.id_discipline = ? AND notes.annee_scolaire = ?
                GROUP BY e.sexe
                ORDER BY e.sexe
            """
            
            df_sexe = pd.read_sql_query(query, conn, params=(discipline_id, annee_scolaire))
            
            # Calculer le taux de réussite
            df_sexe['taux_reussite'] = (df_sexe['nb_moyenne'] / df_sexe['nb_eleves'] * 100).round(2)
            df_sexe['moyenne'] = df_sexe['moyenne'].round(2)
            
            # Remplacer les codes de sexe pour plus de clarté
            df_sexe['sexe'] = df_sexe['sexe'].replace({'M': 'Garçons', 'F': 'Filles'})
            
            # Afficher le tableau
            st.dataframe(
                df_sexe,
                column_config={
                    "sexe": "Sexe",
                    "nb_eleves": st.column_config.NumberColumn("Nombre d'élèves", format="%d"),
                    "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                    "nb_moyenne": st.column_config.NumberColumn("Élèves ≥ 10", format="%d"),
                    "taux_reussite": st.column_config.NumberColumn("Taux de réussite (%)", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Graphique si demandé
            if include_charts and not df_sexe.empty:
                fig = go.Figure()
                
                for sexe in df_sexe['sexe'].unique():
                    row = df_sexe[df_sexe['sexe'] == sexe].iloc[0]
                    
                    fig.add_trace(go.Bar(
                        x=[sexe],
                        y=[row['moyenne']],
                        name=sexe,
                        text=[f"{row['moyenne']}"],
                        textposition='auto',
                        marker_color='#3498db' if sexe == 'Garçons' else '#e74c3c'
                    ))
                
                fig.update_layout(
                    title=f"Moyenne par sexe - {selected_discipline}",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Arial", size=12),
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis=dict(
                        title="Sexe",
                        titlefont=dict(size=14),
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        title="Moyenne",
                        titlefont=dict(size=14),
                        tickfont=dict(size=12),
                        range=[0, 20]
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Bouton pour télécharger le rapport en Excel
        st.markdown(
            """
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Télécharger le rapport</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Préparer les données pour le fichier Excel
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Feuille des statistiques globales
            stats_global_df = pd.DataFrame({
                'Métrique': ['Nombre d\'élèves', 'Moyenne générale', 'Taux de réussite'],
                'Valeur': [stats_global['nb_eleves'], round(stats_global['moyenne'], 2), f"{round(taux_reussite, 2)}%"]
            })
            stats_global_df.to_excel(writer, sheet_name='Stats_Globales', index=False)
            
            # Feuille par niveau si demandée
            if analyze_by_level:
                df_niveaux.to_excel(writer, sheet_name='Stats_Par_Niveau', index=False)
            
            # Feuille par sexe si demandée
            if analyze_by_gender:
                df_sexe.to_excel(writer, sheet_name='Stats_Par_Sexe', index=False)
            
            # Récupérer les données détaillées de tous les élèves
            query = """
                SELECT n.libelle as niveau, c.libelle as classe,
                       e.ien, e.prenom, e.nom, e.sexe,
                       notes.moy_dd, notes.comp_d, notes.moy_d, notes.rang_d
                FROM Notes_S1 notes
                JOIN Eleves e ON notes.ien = e.ien
                JOIN Classes c ON e.id_classe = c.id
                JOIN Niveaux n ON c.id_niveau = n.id
                WHERE notes.id_discipline = ? AND notes.annee_scolaire = ?
                ORDER BY n.libelle, c.libelle, notes.rang_d
            """
            
            df_details = pd.read_sql_query(query, conn, params=(discipline_id, annee_scolaire))
            df_details.to_excel(writer, sheet_name='Détails_Élèves', index=False)
        
        # Proposer le téléchargement
        st.download_button(
            label="📥 Télécharger le rapport Excel",
            data=output.getvalue(),
            file_name=f"Rapport_{selected_discipline}_S1.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def generate_honor_roll(conn, annee_scolaire):
    """Génère un tableau d'honneur avec design amélioré"""
    
    # Créer un conteneur pour les options
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;">Options du tableau d'honneur</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Options du tableau d'honneur
    top_n = st.number_input("Nombre d'élèves à inclure", min_value=1, max_value=100, value=10)
    
    # Options de filtrage
    filter_type = st.radio(
        "Type de filtrage",
        ["Global", "Par niveau", "Par classe"],
        captions=["Meilleurs élèves de l'établissement", "Meilleurs élèves par niveau", "Meilleurs élèves par classe"],
        horizontal=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton pour générer le tableau d'honneur
    if st.button("Générer le tableau d'honneur", use_container_width=True, type="primary"):
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Tableau d'honneur - Semestre 1</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Récupérer les informations de l'établissement
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem;">
                    <p style="margin: 0.3rem 0;"><strong>Établissement:</strong> {config['nom_etablissement'] or 'Non défini'}</p>
                    <p style="margin: 0.3rem 0;"><strong>Année scolaire:</strong> {annee_scolaire}</p>
                    <p style="margin: 0.3rem 0;"><strong>Semestre:</strong> 1</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        if filter_type == "Global":
            # Tableau d'honneur global
            generate_global_honor_roll(conn, annee_scolaire, top_n)
        elif filter_type == "Par niveau":
            # Tableau d'honneur par niveau
            generate_level_honor_roll(conn, annee_scolaire, top_n)
        elif filter_type == "Par classe":
            # Tableau d'honneur par classe
            generate_class_honor_roll(conn, annee_scolaire, top_n)


def generate_global_honor_roll(conn, annee_scolaire, top_n):
    """Génère un tableau d'honneur global avec design amélioré"""
    
    # Récupérer les meilleurs élèves
    query = """
        SELECT e.ien, e.prenom, e.nom, e.sexe, n.libelle as niveau, c.libelle as classe,
               mg.moyenne, mg.rang
        FROM Moyennes_Generales_S1 mg
        JOIN Eleves e ON mg.ien = e.ien
        JOIN Classes c ON e.id_classe = c.id
        JOIN Niveaux n ON c.id_niveau = n.id
        WHERE mg.annee_scolaire = ?
        ORDER BY mg.moyenne DESC
        LIMIT ?
    """
    
    df_honor = pd.read_sql_query(query, conn, params=(annee_scolaire, top_n))
    
    if df_honor.empty:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Ajouter une colonne pour la mention
    df_honor['mention'] = df_honor['moyenne'].apply(lambda x: 
        "Excellent" if x >= 16 else
        "Très Bien" if x >= 14 else
        "Bien" if x >= 12 else
        "Assez Bien" if x >= 10 else
        "Insuffisant"
    )
    
    # Ajouter le rang dans le tableau d'honneur
    df_honor.insert(0, 'rang_honneur', range(1, len(df_honor) + 1))
    
    # Afficher le tableau
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Meilleurs élèves de l'établissement</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.dataframe(
        df_honor,
        column_config={
            "rang_honneur": st.column_config.NumberColumn("Rang"),
            "prenom": "Prénom",
            "nom": "Nom",
            "sexe": "Sexe",
            "niveau": "Niveau",
            "classe": "Classe",
            "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
            "rang": "Rang en classe",
            "mention": "Mention"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Visualisation graphique du top 10
    if len(df_honor) > 1:
        st.markdown("<h4 style='margin: 1.5rem 0 1rem;'>Visualisation des meilleurs élèves</h4>", unsafe_allow_html=True)
        
        # Préparer les données pour le graphique
        df_plot = df_honor.copy()
        df_plot['eleve'] = df_plot['prenom'] + " " + df_plot['nom']
        
        # Créer le graphique
        fig = px.bar(
            df_plot,
            x='eleve',
            y='moyenne',
            color='niveau',
            text='moyenne',
            labels={"eleve": "Élève", "moyenne": "Moyenne"},
            title="Top élèves - Établissement",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                title="Élève",
                titlefont=dict(size=14),
                tickfont=dict(size=10),
                tickangle=45
            ),
            yaxis=dict(
                title="Moyenne",
                titlefont=dict(size=14),
                tickfont=dict(size=12),
                range=[df_plot['moyenne'].min() - 1, 20]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Bouton pour télécharger le tableau d'honneur
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Télécharger le tableau d'honneur</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_honor.to_excel(writer, sheet_name='Tableau_Honneur', index=False)
    
    # Proposer le téléchargement
    st.download_button(
        label="📥 Télécharger le tableau d'honneur",
        data=output.getvalue(),
        file_name=f"Tableau_Honneur_Global_S1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
def generate_level_honor_roll(conn, annee_scolaire, top_n):
    """Génère un tableau d'honneur par niveau avec design amélioré"""
    
    # Récupérer les niveaux disponibles
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT n.id, n.libelle
        FROM Niveaux n
        JOIN Classes c ON n.id = c.id_niveau
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE mg.annee_scolaire = ? AND n.etat = 'actif'
        ORDER BY n.libelle
    """, (annee_scolaire,))
    
    niveaux = cursor.fetchall()
    
    if not niveaux:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Pour chaque niveau
    for niveau in niveaux:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Meilleurs élèves de {niveau['libelle']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Récupérer les meilleurs élèves du niveau
        query = """
            SELECT e.ien, e.prenom, e.nom, e.sexe, c.libelle as classe,
                mg.moyenne, mg.rang
            FROM Moyennes_Generales_S1 mg
            JOIN Eleves e ON mg.ien = e.ien
            JOIN Classes c ON e.id_classe = c.id
            WHERE c.id_niveau = ? AND mg.annee_scolaire = ?
            ORDER BY mg.moyenne DESC
            LIMIT ?
        """
        
        df_honor = pd.read_sql_query(query, conn, params=(niveau['id'], annee_scolaire, top_n))
        
        if df_honor.empty:
            st.info(f"Aucune donnée disponible pour le niveau {niveau['libelle']}.")
            continue
        
        # Ajouter une colonne pour la mention
        df_honor['mention'] = df_honor['moyenne'].apply(lambda x: 
            "Excellent" if x >= 16 else
            "Très Bien" if x >= 14 else
            "Bien" if x >= 12 else
            "Assez Bien" if x >= 10 else
            "Insuffisant"
        )
        
        # Ajouter le rang dans le tableau d'honneur
        df_honor.insert(0, 'rang_honneur', range(1, len(df_honor) + 1))
        
        # Afficher le tableau
        st.dataframe(
            df_honor,
            column_config={
                "rang_honneur": st.column_config.NumberColumn("Rang"),
                "prenom": "Prénom",
                "nom": "Nom",
                "sexe": "Sexe",
                "classe": "Classe",
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "rang": "Rang en classe",
                "mention": "Mention"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Visualisation graphique
        if len(df_honor) > 1:
            # Préparer les données pour le graphique
            df_plot = df_honor.copy()
            df_plot['eleve'] = df_plot['prenom'] + " " + df_plot['nom']
            
            # Créer le graphique
            fig = px.bar(
                df_plot,
                x='eleve',
                y='moyenne',
                color='classe',
                text='moyenne',
                labels={"eleve": "Élève", "moyenne": "Moyenne"},
                title=f"Top élèves - {niveau['libelle']}",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title="Élève",
                    titlefont=dict(size=14),
                    tickfont=dict(size=10),
                    tickangle=45
                ),
                yaxis=dict(
                    title="Moyenne",
                    titlefont=dict(size=14),
                    tickfont=dict(size=12),
                    range=[df_plot['moyenne'].min() - 1, 20]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Bouton pour télécharger tous les tableaux d'honneur
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Télécharger les tableaux d'honneur</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for niveau in niveaux:
            # Récupérer les meilleurs élèves du niveau
            query = """
                SELECT e.ien, e.prenom, e.nom, e.sexe, c.libelle as classe,
                    mg.moyenne, mg.rang
                FROM Moyennes_Generales_S1 mg
                JOIN Eleves e ON mg.ien = e.ien
                JOIN Classes c ON e.id_classe = c.id
                WHERE c.id_niveau = ? AND mg.annee_scolaire = ?
                ORDER BY mg.moyenne DESC
                LIMIT ?
            """
            
            df_honor = pd.read_sql_query(query, conn, params=(niveau['id'], annee_scolaire, top_n))
            
            if not df_honor.empty:
                # Ajouter le rang dans le tableau d'honneur
                df_honor.insert(0, 'rang_honneur', range(1, len(df_honor) + 1))
                
                # Limiter le nom de la feuille à 31 caractères (limite Excel)
                sheet_name = f"Niveau_{niveau['libelle']}"
                if len(sheet_name) > 31:
                    sheet_name = sheet_name[:28] + "..."
                
                df_honor.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Proposer le téléchargement
    st.download_button(
        label="📥 Télécharger tous les tableaux d'honneur",
        data=output.getvalue(),
        file_name=f"Tableaux_Honneur_Par_Niveau_S1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def generate_class_honor_roll(conn, annee_scolaire, top_n):
    """Génère un tableau d'honneur par classe avec design amélioré"""
    
    # Récupérer les classes disponibles
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT c.id, c.libelle, n.libelle as niveau
        FROM Classes c
        JOIN Niveaux n ON c.id_niveau = n.id
        JOIN Eleves e ON c.id = e.id_classe
        JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
        WHERE mg.annee_scolaire = ? AND c.etat = 'actif'
        ORDER BY n.libelle, c.libelle
    """, (annee_scolaire,))
    
    classes = cursor.fetchall()
    
    if not classes:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Pour chaque classe
    for classe in classes:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Meilleurs élèves de {classe['niveau']} {classe['libelle']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Récupérer les meilleurs élèves de la classe
        query = """
            SELECT e.ien, e.prenom, e.nom, e.sexe, mg.moyenne, mg.rang
            FROM Moyennes_Generales_S1 mg
            JOIN Eleves e ON mg.ien = e.ien
            WHERE e.id_classe = ? AND mg.annee_scolaire = ?
            ORDER BY mg.moyenne DESC
            LIMIT ?
        """
        
        df_honor = pd.read_sql_query(query, conn, params=(classe['id'], annee_scolaire, top_n))
        
        if df_honor.empty:
            st.info(f"Aucune donnée disponible pour la classe {classe['niveau']} {classe['libelle']}.")
            continue
        
        # Ajouter une colonne pour la mention
        df_honor['mention'] = df_honor['moyenne'].apply(lambda x: 
            "Excellent" if x >= 16 else
            "Très Bien" if x >= 14 else
            "Bien" if x >= 12 else
            "Assez Bien" if x >= 10 else
            "Insuffisant"
        )
        
        # Ajouter le rang dans le tableau d'honneur
        df_honor.insert(0, 'rang_honneur', range(1, len(df_honor) + 1))
        
        # Afficher le tableau
        st.dataframe(
            df_honor,
            column_config={
                "rang_honneur": st.column_config.NumberColumn("Rang"),
                "prenom": "Prénom",
                "nom": "Nom",
                "sexe": "Sexe",
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "rang": "Rang en classe",
                "mention": "Mention"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Visualisation graphique
        if len(df_honor) > 1:
            # Préparer les données pour le graphique
            df_plot = df_honor.copy()
            df_plot['eleve'] = df_plot['prenom'] + " " + df_plot['nom']
            
            # Créer le graphique
            fig = px.bar(
                df_plot,
                x='eleve',
                y='moyenne',
                text='moyenne',
                labels={"eleve": "Élève", "moyenne": "Moyenne"},
                title=f"Top élèves - {classe['niveau']} {classe['libelle']}",
                color_discrete_sequence=[THEME_COLORS['primary']]
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title="Élève",
                    titlefont=dict(size=14),
                    tickfont=dict(size=10),
                    tickangle=45
                ),
                yaxis=dict(
                    title="Moyenne",
                    titlefont=dict(size=14),
                    tickfont=dict(size=12),
                    range=[df_plot['moyenne'].min() - 1, 20]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Bouton pour télécharger tous les tableaux d'honneur
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Télécharger les tableaux d'honneur</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for classe in classes:
            # Récupérer les meilleurs élèves de la classe
            query = """
                SELECT e.ien, e.prenom, e.nom, e.sexe, mg.moyenne, mg.rang
                FROM Moyennes_Generales_S1 mg
                JOIN Eleves e ON mg.ien = e.ien
                WHERE e.id_classe = ? AND mg.annee_scolaire = ?
                ORDER BY mg.moyenne DESC
                LIMIT ?
            """
            
            df_honor = pd.read_sql_query(query, conn, params=(classe['id'], annee_scolaire, top_n))
            
            if not df_honor.empty:
                # Ajouter le rang dans le tableau d'honneur
                df_honor.insert(0, 'rang_honneur', range(1, len(df_honor) + 1))
                
                # Limiter le nom de la feuille à 31 caractères (limite Excel)
                sheet_name = f"{classe['niveau']}_{classe['libelle']}"
                if len(sheet_name) > 31:
                    sheet_name = sheet_name[:28] + "..."
                
                df_honor.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Proposer le téléchargement
    st.download_button(
        label="📥 Télécharger tous les tableaux d'honneur",
        data=output.getvalue(),
        file_name=f"Tableaux_Honneur_Par_Classe_S1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def generate_global_stats(conn, annee_scolaire):
    """Génère un rapport statistique global avec design amélioré"""
    
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Rapport statistique global - Semestre 1</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Récupérer les informations de l'établissement
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Configuration LIMIT 1")
    config = cursor.fetchone()
    
    if config:
        st.markdown(
            f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem;">
                <p style="margin: 0.3rem 0;"><strong>Établissement:</strong> {config['nom_etablissement'] or 'Non défini'}</p>
                <p style="margin: 0.3rem 0;"><strong>Année scolaire:</strong> {annee_scolaire}</p>
                <p style="margin: 0.3rem 0;"><strong>Semestre:</strong> 1</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Statistiques générales
    cursor.execute("""
        SELECT COUNT(DISTINCT mg.ien) as nb_eleves,
               AVG(mg.moyenne) as moyenne_generale,
               COUNT(CASE WHEN mg.moyenne >= 10 THEN 1 END) as nb_moyenne
        FROM Moyennes_Generales_S1 mg
        WHERE mg.annee_scolaire = ?
    """, (annee_scolaire,))
    
    stats_global = cursor.fetchone()
    
    if not stats_global or stats_global['nb_eleves'] == 0:
        st.info(f"Aucune donnée disponible pour l'année scolaire {annee_scolaire}.")
        return
    
    # Calculer le taux de réussite
    taux_reussite = (stats_global['nb_moyenne'] / stats_global['nb_eleves']) * 100
    
    # Afficher les statistiques globales
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques générales</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['primary']}; margin-bottom: 0.5rem;">
                    {stats_global['nb_eleves']}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Nombre d'élèves</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['info']}; margin-bottom: 0.5rem;">
                    {round(stats_global['moyenne_generale'], 2)}
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Moyenne générale</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 1rem; border-radius: 5px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem; color: {THEME_COLORS['success']}; margin-bottom: 0.5rem;">
                    {round(taux_reussite, 2)}%
                </div>
                <p style="font-size: 0.9rem; color: #2c3e50; margin: 0;">Taux de réussite</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Statistiques par niveau
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques par niveau</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    query = """
        SELECT n.libelle as niveau, COUNT(DISTINCT mg.ien) as nb_eleves,
               AVG(mg.moyenne) as moyenne,
               COUNT(CASE WHEN mg.moyenne >= 10 THEN 1 END) as nb_moyenne
        FROM Moyennes_Generales_S1 mg
        JOIN Eleves e ON mg.ien = e.ien
        JOIN Classes c ON e.id_classe = c.id
        JOIN Niveaux n ON c.id_niveau = n.id
        WHERE mg.annee_scolaire = ?
        GROUP BY n.libelle
        ORDER BY n.libelle
    """
    
    df_niveaux = pd.read_sql_query(query, conn, params=(annee_scolaire,))
    
    if not df_niveaux.empty:
        # Calculer le taux de réussite
        df_niveaux['taux_reussite'] = (df_niveaux['nb_moyenne'] / df_niveaux['nb_eleves'] * 100).round(2)
        df_niveaux['moyenne'] = df_niveaux['moyenne'].round(2)
        
        # Afficher le tableau des niveaux
        st.dataframe(
            df_niveaux,
            column_config={
                "niveau": "Niveau",
                "nb_eleves": st.column_config.NumberColumn("Nombre d'élèves", format="%d"),
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "nb_moyenne": st.column_config.NumberColumn("Élèves ≥ 10", format="%d"),
                "taux_reussite": st.column_config.NumberColumn("Taux de réussite (%)", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Graphique des moyennes par niveau
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_niveaux,
                x="niveau",
                y="moyenne",
                color="niveau",
                title="Moyenne par niveau",
                labels={"niveau": "Niveau", "moyenne": "Moyenne"},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12),
                    range=[0, 20]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df_niveaux,
                x="niveau",
                y="taux_reussite",
                color="niveau",
                title="Taux de réussite par niveau",
                labels={"niveau": "Niveau", "taux_reussite": "Taux de réussite (%)"},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title=dict(font=dict(size=14)),
                    tickfont=dict(size=12),
                    range=[0, 100]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques par classe
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques par classe</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    query = """
        SELECT n.libelle as niveau, c.libelle as classe, 
               COUNT(DISTINCT mg.ien) as nb_eleves,
               AVG(mg.moyenne) as moyenne,
               COUNT(CASE WHEN mg.moyenne >= 10 THEN 1 END) as nb_moyenne
        FROM Moyennes_Generales_S1 mg
        JOIN Eleves e ON mg.ien = e.ien
        JOIN Classes c ON e.id_classe = c.id
        JOIN Niveaux n ON c.id_niveau = n.id
        WHERE mg.annee_scolaire = ?
        GROUP BY n.libelle, c.libelle
        ORDER BY n.libelle, c.libelle
    """
    
    df_classes = pd.read_sql_query(query, conn, params=(annee_scolaire,))
    
    if not df_classes.empty:
        # Calculer le taux de réussite
        df_classes['taux_reussite'] = (df_classes['nb_moyenne'] / df_classes['nb_eleves'] * 100).round(2)
        df_classes['moyenne'] = df_classes['moyenne'].round(2)
        
        # Afficher le tableau des classes
        st.dataframe(
            df_classes,
            column_config={
                "niveau": "Niveau",
                "classe": "Classe",
                "nb_eleves": st.column_config.NumberColumn("Nombre d'élèves", format="%d"),
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "nb_moyenne": st.column_config.NumberColumn("Élèves ≥ 10", format="%d"),
                "taux_reussite": st.column_config.NumberColumn("Taux de réussite (%)", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Statistiques par discipline
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Statistiques par discipline</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    query = """
        SELECT d.libelle as discipline, COUNT(DISTINCT notes.ien) as nb_eleves,
               AVG(notes.moy_d) as moyenne,
               COUNT(CASE WHEN notes.moy_d >= 10 THEN 1 END) as nb_moyenne
        FROM Notes_S1 notes
        JOIN Disciplines d ON notes.id_discipline = d.id
        WHERE notes.annee_scolaire = ?
        GROUP BY d.libelle
        ORDER BY d.libelle
    """
    
    df_disciplines = pd.read_sql_query(query, conn, params=(annee_scolaire,))
    
    if not df_disciplines.empty:
        # Calculer le taux de réussite
        df_disciplines['taux_reussite'] = (df_disciplines['nb_moyenne'] / df_disciplines['nb_eleves'] * 100).round(2)
        df_disciplines['moyenne'] = df_disciplines['moyenne'].round(2)
        
        # Afficher le tableau des disciplines
        st.dataframe(
            df_disciplines,
            column_config={
                "discipline": "Discipline",
                "nb_eleves": st.column_config.NumberColumn("Nombre d'élèves", format="%d"),
                "moyenne": st.column_config.NumberColumn("Moyenne", format="%.2f"),
                "nb_moyenne": st.column_config.NumberColumn("Élèves ≥ 10", format="%d"),
                "taux_reussite": st.column_config.NumberColumn("Taux de réussite (%)", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Graphique des moyennes par discipline
        fig = px.bar(
            df_disciplines,
            x="discipline",
            y="moyenne",
            color="discipline",
            title="Moyenne par discipline",
            labels={"discipline": "Discipline", "moyenne": "Moyenne"},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                title="Discipline",
                titlefont=dict(size=14),
                tickfont=dict(size=10),
                tickangle=45
            ),
            yaxis=dict(
                title="Moyenne",
                titlefont=dict(size=14),
                tickfont=dict(size=12),
                range=[0, 20]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
   # Bouton pour télécharger le rapport statistique
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0 0.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">Télécharger le rapport statistique</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Feuille des statistiques globales
        stats_global_df = pd.DataFrame({
            'Métrique': ['Nombre d\'élèves', 'Moyenne générale', 'Élèves ≥ 10', 'Taux de réussite'],
            'Valeur': [
                stats_global['nb_eleves'], 
                round(stats_global['moyenne_generale'], 2), 
                stats_global['nb_moyenne'],
                f"{round(taux_reussite, 2)}%"
            ]
        })
        stats_global_df.to_excel(writer, sheet_name='Stats_Globales', index=False)
        
        # Feuille des statistiques par niveau
        if not df_niveaux.empty:
            df_niveaux.to_excel(writer, sheet_name='Stats_Par_Niveau', index=False)
        
        # Feuille des statistiques par classe
        if not df_classes.empty:
            df_classes.to_excel(writer, sheet_name='Stats_Par_Classe', index=False)
        
        # Feuille des statistiques par discipline
        if not df_disciplines.empty:
            df_disciplines.to_excel(writer, sheet_name='Stats_Par_Discipline', index=False)
    
    # Proposer le téléchargement
    st.download_button(
        label="📥 Télécharger le rapport statistique",
        data=output.getvalue(),
        file_name=f"Rapport_Statistique_Global_S1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def show_import_interface():
    """Affiche l'interface d'importation des données avec design amélioré"""
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Importation de données - Semestre 1</h2>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        h3 {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Vérifier si une année scolaire est active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
    annee_result = cursor.fetchone()
    
    if not annee_result:
        st.warning("Aucune année scolaire active. Veuillez configurer l'année scolaire dans le module Paramètres.")
        return
    
    annee_scolaire = annee_result[0]
    
    # Afficher l'année scolaire active de manière élégante
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem; text-align: center;">
            <h3 style="margin: 0; color: {THEME_COLORS['primary']};">Importation pour l'année scolaire: {annee_scolaire}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Sélection du niveau et de la classe
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;'>Étape 1: Sélectionner le niveau et la classe</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Récupérer les niveaux disponibles
    cursor.execute("SELECT id, libelle FROM Niveaux WHERE etat = 'actif' ORDER BY libelle")
    niveaux = cursor.fetchall()
    
    if not niveaux:
        st.markdown("</div>", unsafe_allow_html=True)
        st.warning("Aucun niveau actif trouvé. Veuillez configurer les niveaux dans le module Paramètres.")
        return
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    col1, col2 = st.columns(2)
    
    with col1:
        selected_niveau = st.selectbox(
            "📚 Niveau",
            options=list(niveau_options.keys()),
            key="niveau_select_import"
        )
    
    niveau_id = niveau_options[selected_niveau]
    
    # Récupérer les classes du niveau sélectionné
    cursor.execute(
        "SELECT id, libelle FROM Classes WHERE id_niveau = ? AND etat = 'actif' ORDER BY libelle",
        (niveau_id,)
    )
    classes = cursor.fetchall()
    
    # Si aucune classe n'existe pour ce niveau, proposer d'en créer une
    if not classes:
        st.markdown("</div>", unsafe_allow_html=True)
        st.warning(f"Aucune classe active trouvée pour le niveau {selected_niveau}.")
        
        st.markdown(
            """
            <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
                <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;'>Créer une nouvelle classe</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.form("create_class_form"):
            nouvelle_classe = st.text_input("🏷️ Nom de la nouvelle classe")
            effectif = st.number_input("👥 Effectif estimé", min_value=1, value=30)
            
            submitted = st.form_submit_button("Créer la classe")
            
            if submitted and nouvelle_classe:
                cursor.execute(
                    "INSERT INTO Classes (id_niveau, libelle, effectif) VALUES (?, ?, ?)",
                    (niveau_id, nouvelle_classe, effectif)
                )
                conn.commit()
                st.success(f"✅ Classe {nouvelle_classe} créée avec succès")
                st.experimental_rerun()
        
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    
    with col2:
        selected_classe = st.selectbox(
            "🏷️ Classe",
            options=list(classe_options.keys()),
            key="classe_select_import"
        )
    
    classe_id = classe_options[selected_classe]
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Uploader le fichier Excel
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;'>Étape 2: Importer le fichier Excel</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Section d'aide
    with st.expander("ℹ️ Instructions pour l'importation"):
        st.markdown("""
        ### Format du fichier à importer
        
        Votre fichier doit être au format Excel (XLSX) et contenir les feuilles suivantes:
        
        1. **Moyennes eleves** - Contenant les moyennes générales et informations sur les élèves.
           - Doit inclure les colonnes: IEN, Prénom, Nom, Moy, Rang
           
        2. **Données détaillées** - Contenant les notes détaillées par discipline.
           - Structure avec des colonnes par discipline
        
        ### Procédure d'importation
        
        1. Exportez les données depuis la plateforme PLANETE au format Excel
        2. Vérifiez que le fichier contient toutes les données requises
        3. Sélectionnez le niveau et la classe correspondants
        4. Importez le fichier en utilisant le bouton ci-dessous
        5. Vérifiez l'aperçu des données avant de confirmer l'importation
        
        ### Remarques importantes
        
        - Les données existantes pour la même classe et le même semestre seront écrasées
        - Assurez-vous que tous les élèves ont un identifiant IEN valide
        - Les données importées seront associées à l'année scolaire active
        """)
    
    fichier = st.file_uploader("📂 Importer un fichier Excel PLANETE", type=["xlsx"])
    
    conn.close()
    
    if fichier:
        try:
            # Afficher message de traitement
            with st.spinner("Traitement du fichier en cours..."):
                # Charger et nettoyer le fichier
                df_moyennes, df_final, _ = charger_et_nettoyer(fichier)

                # Forcer la présence des colonnes obligatoires et remplir les vides
                for col in ["Prenom", "Nom", "IEN"]:
                    if col not in df_moyennes.columns:
                        df_moyennes[col] = "Non défini"
                df_moyennes["Prenom"] = df_moyennes["Prenom"].fillna("Non défini").replace("", "Non défini")
                df_moyennes["Nom"] = df_moyennes["Nom"].fillna("Non défini").replace("", "Non défini")
                df_moyennes["IEN"] = df_moyennes["IEN"].fillna("").replace("", "")

                # Valider le fichier
                if 'IEN' not in df_moyennes.columns or 'Moy' not in df_moyennes.columns:
                    st.error("❌ Format de fichier incorrect. Vérifiez que le fichier provient bien de PLANETE.")
                    return

                # Afficher un aperçu des données
                st.success("✅ Fichier chargé avec succès")
                
                st.markdown(
                    """
                    <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                        <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;'>Étape 3: Vérifier les données</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("<h4 style='margin: 1rem 0;'>📋 Aperçu des moyennes générales</h4>", unsafe_allow_html=True)
                st.dataframe(df_moyennes, use_container_width=True)
                
                # Afficher des statistiques de base
                nb_eleves = len(df_moyennes)
                moyenne_generale = round(df_moyennes['Moy'].mean(), 2) if 'Moy' in df_moyennes.columns else 0
                nb_disciplines = len(df_final.columns) - 3  # Soustraire les colonnes d'information (IEN, Prénom, Nom)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Nombre d'élèves", nb_eleves)
                col2.metric("Moyenne générale", moyenne_generale)
                col3.metric("Nombre de disciplines", nb_disciplines)
                
                # Bouton pour confirmer l'importation
                st.markdown(
                    """
                    <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                        <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem;'>Étape 4: Confirmer l'importation</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button("✅ Confirmer et importer les données", use_container_width=True, type="primary"):
                    with st.spinner("Importation des données..."):
                        # Sécuriser à nouveau juste avant l'import
                        df_moyennes["Prenom"] = df_moyennes["Prenom"].fillna("Non défini").replace("", "Non défini")
                        df_moyennes["Nom"] = df_moyennes["Nom"].fillna("Non défini").replace("", "Non défini")
                        df_moyennes["IEN"] = df_moyennes["IEN"].fillna("").replace("", "")
                        try:
                            sauvegarder_dans_fichier_central(df_moyennes, df_final, selected_niveau, selected_classe, 1)  # 1 pour semestre 1
                        except PermissionError:
                            st.error("Impossible d'écrire dans le fichier central. Veuillez fermer 'fichier_central.xlsx' et réessayer.")
                            return
                        
                        st.success(f"✅ Données importées avec succès pour la classe {selected_niveau} {selected_classe}")
                        
                        # Proposer de télécharger le fichier traité
                        excel_data = to_excel(df_moyennes, df_final)
                        st.download_button(
                            label="⬇️ Télécharger le fichier traité",
                            data=excel_data,
                            file_name=f"{selected_niveau}_{selected_classe}_S1.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        except Exception as e:
            st.error(f"❌ Erreur lors du traitement du fichier: {str(e)}")
    
    # Section de suppression
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem; color: #e74c3c;'>Zone de suppression</h3>
            <p style="margin-bottom: 1rem; color: #7f8c8d;'>Cette zone permet de supprimer des données. Attention, ces opérations sont irréversibles.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Supprimer les données de la classe", use_container_width=True):
            # Confirmation
            if st.checkbox(f"Je confirme vouloir supprimer toutes les données de la classe {selected_classe}"):
                from ..utils.excel_utils import synchroniser_suppression_classe
                try:
                    synchroniser_suppression_classe(selected_niveau, selected_classe, 1)
                    st.success(f"Toutes les données de la classe {selected_classe} ont été supprimées (base + fichier central)")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la suppression de la classe : {e}")
    
    with col2:
        if st.button("❌ Supprimer les données du niveau", use_container_width=True):
            # Confirmation
            if st.checkbox(f"Je confirme vouloir supprimer toutes les données du niveau {selected_niveau}"):
                from ..utils.excel_utils import synchroniser_suppression_niveau
                try:
                    synchroniser_suppression_niveau(selected_niveau, 1)
                    st.success(f"Toutes les données du niveau {selected_niveau} ont été supprimées (base + fichier central)")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la suppression du niveau : {e}")
    
    # Historique des imports
    st.markdown(
        """
        <div style="background-color: white; padding: 1.2rem; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1.5rem 0;">
            <h3 style="margin-top: 0; margin-bottom: 1rem;'>Historique des imports</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    from ..utils.excel_utils import synchroniser_suppression_classe
    if os.path.exists(FICHIER_CENTRAL):
        try:
            df_hist = pd.read_excel(FICHIER_CENTRAL, sheet_name="Moyennes eleves")
            # normalize column names
            cols = {c.lower(): c for c in df_hist.columns}
            lvl_col = cols.get('niveau')
            cls_col = cols.get('classe')
            sem_col = cols.get('semestre')
            if lvl_col and cls_col and sem_col:
                df_hist = df_hist[df_hist[sem_col] == 1]
                entries = df_hist[[lvl_col, cls_col]].drop_duplicates().values.tolist()
                options = [f"{lvl}-{cls}" for lvl, cls in entries]
                if options:
                    sel = st.selectbox("Supprimer import: Niveau-Classe", options)
                    if st.button("Supprimer cet import", use_container_width=True):
                        lvl, cls = sel.split("-")
                        synchroniser_suppression_classe(lvl, cls, 1)
                        st.success(f"Import {sel} supprimé")
                        st.experimental_rerun()
            else:
                st.warning("Colonnes 'Niveau', 'Classe' ou 'Semestre' manquantes pour historique.")
        except Exception:
            st.warning("Impossible de lire l'historique des imports.")
    else:
        st.info("Aucun fichier centralisé trouvé.")
