import streamlit as st
import pandas as pd
import os
import sqlite3
from ..config import FICHIER_CENTRAL, DB_PATH
from ..utils.db_utils import get_db_connection
from ..utils.excel_utils import charger_et_nettoyer, sauvegarder_dans_fichier_central, to_excel
from ..utils.viz_utils import plot_distribution_moyennes, plot_repartition_par_sexe, plot_comparaison_disciplines

def show_semestre1_view():
    """Affiche le module Semestre 1"""
    
    st.title("📝 Module Semestre 1")
    
    # Barre latérale pour la navigation interne
    page = st.sidebar.radio(
        "Navigation Semestre 1",
        ["Vue d'ensemble", "Analyse Moyennes", "Analyse Disciplines", "Rapports", "Base d'importation"],
        captions=["Tableau de bord", "Analyse des moyennes générales", "Analyse par discipline", "Génération de rapports", "Importation de données"]
    )
    
    # Afficher la page correspondante
    if page == "Vue d'ensemble":
        show_overview()
    elif page == "Analyse Moyennes":
        show_moyennes_analysis()
    elif page == "Analyse Disciplines":
        show_disciplines_analysis()
    elif page == "Rapports":
        show_reports()
    elif page == "Base d'importation":
        show_import_interface()

def show_overview():
    """Affiche la vue d'ensemble du semestre 1"""
    
    st.subheader("Vue d'ensemble - Semestre 1")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via la page 'Base d'importation'.")
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
    
    # Afficher l'année scolaire active
    st.info(f"Année scolaire active: {annee_scolaire}")
    
    # Récupérer les statistiques clés
    stats = {}
    
    # Nombre total d'élèves évalués au S1
    cursor.execute("""
        SELECT COUNT(DISTINCT ien) FROM Moyennes_Generales_S1 
        WHERE annee_scolaire = ?
    """, (annee_scolaire,))
    stats['total_eleves'] = cursor.fetchone()[0] or 0
    
    # Calculer la moyenne générale à partir du fichier Excel centralisé
    moyenne_generale = 0
    try:
        if os.path.exists(FICHIER_CENTRAL):
            df_excel = pd.read_excel(FICHIER_CENTRAL, sheet_name="Moyennes eleves")
            # Filtrer sur l'année scolaire si la colonne existe
            if 'semestre' in df_excel.columns and 'Moy' in df_excel.columns:
                df_excel = df_excel[df_excel['semestre'] == 1]
                if not df_excel.empty:
                    moyenne_generale = round(df_excel['Moy'].sum() / len(df_excel), 2)
    except Exception:
        moyenne_generale = 0

    stats['moyenne_generale'] = moyenne_generale
    
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
    
    # Afficher les statistiques clés
    st.subheader("Statistiques générales")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Élèves évalués", stats['total_eleves'])
    col2.metric("Moyenne générale", stats['moyenne_generale'])
    col3.metric("Élèves ≥ 10", stats['eleves_avec_moyenne'])
    col4.metric("Taux de réussite", f"{stats['taux_reussite']}%")
    
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
        # Convertir en DataFrame pour faciliter l'affichage
        df_niveaux = pd.DataFrame(niveaux_data, columns=['niveau', 'nb_eleves', 'moyenne', 'nb_moyenne'])
        df_niveaux['taux'] = (df_niveaux['nb_moyenne'] / df_niveaux['nb_eleves'] * 100).round(2)
        df_niveaux['moyenne'] = df_niveaux['moyenne'].round(2)
        
        # Afficher un tableau des statistiques par niveau
        st.subheader("Performance par niveau")
        st.dataframe(
            df_niveaux,
            column_config={
                "niveau": "Niveau",
                "nb_eleves": "Nombre d'élèves",
                "moyenne": "Moyenne générale",
                "nb_moyenne": "Élèves ≥ 10",
                "taux": "Taux de réussite (%)"
            },
            hide_index=True
        )
        
        # Visualisation des moyennes par niveau
        st.subheader("Moyennes par niveau")
        
        # Récupérer les moyennes de tous les élèves
        conn = get_db_connection()
        query = """
            SELECT n.libelle as niveau, mg.moyenne
            FROM Moyennes_Generales_S1 mg
            JOIN Eleves e ON mg.ien = e.ien
            JOIN Classes c ON e.id_classe = c.id
            JOIN Niveaux n ON c.id_niveau = n.id
            WHERE mg.annee_scolaire = ?
        """
        df_moyennes = pd.read_sql_query(query, conn, params=(annee_scolaire,))
        conn.close()
        
        if not df_moyennes.empty:
            # Créer un graphique en barres des moyennes par niveau
            import plotly.express as px
            
            fig = px.box(
                df_moyennes, 
                x="niveau", 
                y="moyenne",
                color="niveau",
                title="Distribution des moyennes par niveau"
            )
            
            fig.update_layout(
                xaxis_title="Niveau",
                yaxis_title="Moyenne",
                yaxis=dict(range=[0, 20])  # Échelle de 0 à 20
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour l'année scolaire actuelle.")

def show_moyennes_analysis():
    """Affiche l'analyse des moyennes générales du semestre 1"""
    
    st.subheader("Analyse des moyennes - Semestre 1")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via la page 'Base d'importation'.")
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
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    selected_niveau = st.selectbox("Sélectionner un niveau", options=list(niveau_options.keys()))
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
        st.info(f"Aucune classe avec des données pour le niveau {selected_niveau}.")
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    selected_classe = st.selectbox("Sélectionner une classe", options=list(classe_options.keys()))
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
    
    # Statistiques de la classe
    st.subheader(f"Statistiques de la classe {selected_niveau} {selected_classe}")
    
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
    
    # Afficher les statistiques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Effectif", stats['effectif'])
    col2.metric("Moyenne de classe", stats['moyenne_classe'])
    col3.metric("Élèves ≥ 10", stats['nb_moyenne'])
    col4.metric("Taux de réussite", f"{stats['taux_reussite']}%")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Médiane", stats['mediane'])
    col2.metric("Écart-type", stats['ecart_type'])
    col3.metric("Min", stats['min'])
    col4.metric("Max", stats['max'])
    
    # Tableau des élèves
    st.subheader("Liste des élèves")
    
    # Ajouter une colonne pour la mention
    df_classe['mention'] = df_classe['moyenne'].apply(lambda x: 
        "Excellent" if x >= 16 else
        "Très Bien" if x >= 14 else
        "Bien" if x >= 12 else
        "Assez Bien" if x >= 10 else
        "Insuffisant"
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
            "appreciation": "Appréciation"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Visualisations
    st.subheader("Visualisations")
    
    col1, col2 = st.columns(2)
    
    # Distribution des moyennes
    with col1:
        fig = plot_distribution_moyennes(df_classe, f"Distribution des moyennes - {selected_classe}", column="moyenne")
        st.plotly_chart(fig, use_container_width=True)
    
    # Répartition par sexe
    with col2:
        if 'sexe' in df_classe.columns:
            fig = plot_repartition_par_sexe(df_classe, "moyenne", f"Moyennes par sexe - {selected_classe}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de sexe non disponibles pour cette analyse.")
    
    # Analyse des élèves en difficulté
    st.subheader("Élèves en difficulté")
    
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
    else:
        st.success("Aucun élève en difficulté (tous les élèves ont une moyenne ≥ 10).")

def show_disciplines_analysis():
    """Affiche l'analyse par discipline du semestre 1"""
    
    st.subheader("Analyse par discipline - Semestre 1")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via la page 'Base d'importation'.")
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
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    selected_niveau = st.selectbox("Sélectionner un niveau", options=list(niveau_options.keys()))
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
        st.info(f"Aucune classe avec des données pour le niveau {selected_niveau}.")
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    selected_classe = st.selectbox("Sélectionner une classe", options=list(classe_options.keys()))
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
        st.info(f"Aucune donnée de discipline disponible pour la classe {selected_classe}.")
        return
    
    # Sélecteur de discipline
    discipline_options = {discipline['libelle']: discipline['id'] for discipline in disciplines}
    selected_discipline = st.selectbox("Sélectionner une discipline", options=list(discipline_options.keys()))
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
    
    # Statistiques de la discipline
    st.subheader(f"Statistiques de {selected_discipline} - {selected_niveau} {selected_classe}")
    
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
    
    # Afficher les statistiques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Effectif", stats['effectif'])
    col2.metric("Moyenne de discipline", stats['moyenne_discipline'])
    col3.metric("Élèves ≥ 10", stats['nb_moyenne'])
    col4.metric("Taux de réussite", f"{stats['taux_reussite']}%")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Médiane", stats['mediane'])
    col2.metric("Écart-type", stats['ecart_type'])
    col3.metric("Min", stats['min'])
    col4.metric("Max", stats['max'])
    
    # Tableau des notes
    st.subheader("Notes des élèves")
    
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
            "rang_general": "Rang Général"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Visualisations
    st.subheader("Visualisations")
    
    col1, col2 = st.columns(2)
    
    # Distribution des notes
    with col1:
        import plotly.express as px
        
        fig = px.histogram(
            df_discipline, 
            x="moy_d", 
            nbins=20,
            color_discrete_sequence=['#2ecc71'],
            title=f"Distribution des notes - {selected_discipline}"
        )
        
        fig.update_layout(
            xaxis_title="Note",
            yaxis_title="Nombre d'élèves",
            bargap=0.1
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Répartition par sexe
    with col2:
        if 'sexe' in df_discipline.columns:
            fig = plot_repartition_par_sexe(df_discipline, "moy_d", f"Notes par sexe - {selected_discipline}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de sexe non disponibles pour cette analyse.")
    
    # Analyse comparative avec la moyenne générale
    st.subheader("Comparaison avec la moyenne générale")
    
    # Créer un graphique comparatif
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Créer une liste d'indices pour représenter les élèves
    indices = list(range(len(df_discipline)))
    
    # Trier par rang général pour une meilleure visualisation
    df_tri = df_discipline.sort_values('rang_general')
    
    # Ajouter les deux courbes
    fig.add_trace(go.Scatter(
        x=indices,
        y=df_tri['moy_d'],
        mode='lines+markers',
        name=f'{selected_discipline}',
        line=dict(color='#2ecc71', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=indices,
        y=df_tri['moyenne_generale'],
        mode='lines+markers',
        name='Moyenne générale',
        line=dict(color='#3498db', width=2)
    ))
    
    # Personnaliser le graphique
    fig.update_layout(
        title=f"Comparaison entre {selected_discipline} et la moyenne générale",
        xaxis_title="Élèves",
        yaxis_title="Note",
        yaxis=dict(range=[0, 20]),
        xaxis=dict(
            tickmode='array',
            tickvals=indices,
            ticktext=[f"{prenom} {nom}" for prenom, nom in zip(df_tri['prenom'], df_tri['nom'])]
        )
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)

def show_reports():
    """Affiche la page de génération de rapports du semestre 1"""
    
    st.subheader("Rapports - Semestre 1")
    
    # Vérifier si des données existent
    if not os.path.exists(DB_PATH):
        st.info("Aucune donnée disponible. Veuillez importer des données via la page 'Base d'importation'.")
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
    
    # Types de rapports disponibles
    report_types = [
        "Rapport de classe",
        "Rapport par discipline",
        "Tableau d'honneur",
        "Rapport statistique global"
    ]
    
    selected_report = st.selectbox("Sélectionner un type de rapport", options=report_types)
    
    if selected_report == "Rapport de classe":
        generate_class_report(conn, annee_scolaire)
    elif selected_report == "Rapport par discipline":
        generate_discipline_report(conn, annee_scolaire)
    elif selected_report == "Tableau d'honneur":
        generate_honor_roll(conn, annee_scolaire)
    elif selected_report == "Rapport statistique global":
        generate_global_stats(conn, annee_scolaire)
    
    conn.close()

def generate_class_report(conn, annee_scolaire):
    """Génère un rapport de classe"""
    
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
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    selected_niveau = st.selectbox("Sélectionner un niveau", options=list(niveau_options.keys()))
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
        st.info(f"Aucune classe avec des données pour le niveau {selected_niveau}.")
        return
    
    # Sélecteur de classe
    classe_options = {classe['libelle']: classe['id'] for classe in classes}
    selected_classe = st.selectbox("Sélectionner une classe", options=list(classe_options.keys()))
    classe_id = classe_options[selected_classe]
    
    # Options supplémentaires
    include_disciplines = st.checkbox("Inclure les détails par discipline", value=True)
    include_charts = st.checkbox("Inclure les graphiques", value=True)
    
    if st.button("Générer le rapport"):
        st.subheader(f"Rapport de classe - {selected_niveau} {selected_classe} - Semestre 1")
        
        # Récupérer les informations de l'établissement
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            st.markdown(f"""
            **Établissement**: {config['nom_etablissement']}  
            **Année scolaire**: {annee_scolaire}  
            **Semestre**: 1
            """)
        
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
        
        # Afficher les statistiques
        st.markdown("### Statistiques générales")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Effectif", stats['effectif'])
        col2.metric("Moyenne de classe", stats['moyenne_classe'])
        col3.metric("Élèves ≥ 10", stats['nb_moyenne'])
        col4.metric("Taux de réussite", f"{stats['taux_reussite']}%")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Médiane", stats['mediane'])
        col2.metric("Écart-type", stats['ecart_type'])
        col3.metric("Min", stats['min'])
        col4.metric("Max", stats['max'])
        
        # Ajouter une colonne pour la mention
        df_classe['mention'] = df_classe['moyenne'].apply(lambda x: 
            "Excellent" if x >= 16 else
            "Très Bien" if x >= 14 else
            "Bien" if x >= 12 else
            "Assez Bien" if x >= 10 else
            "Insuffisant"
        )
        
        # Tableau des élèves
        st.markdown("### Liste des élèves")
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
            st.markdown("### Détails par discipline")
            
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
                st.markdown(f"#### {discipline['libelle']}")
                
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
            st.markdown("### Visualisations")
            
            col1, col2 = st.columns(2)
            
            # Distribution des moyennes
            with col1:
                fig = plot_distribution_moyennes(df_classe, f"Distribution des moyennes - {selected_classe}", column="moyenne")
                st.plotly_chart(fig, use_container_width=True)
            
            # Répartition par sexe
            with col2:
                if 'sexe' in df_classe.columns:
                    fig = plot_repartition_par_sexe(df_classe, "moyenne", f"Moyennes par sexe - {selected_classe}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Données de sexe non disponibles pour cette analyse.")
        
        # Bouton pour télécharger le rapport en Excel
        st.markdown("### Télécharger le rapport")
        
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def generate_discipline_report(conn, annee_scolaire):
    """Génère un rapport par discipline"""
    
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
    
    # Sélecteur de discipline
    discipline_options = {discipline['libelle']: discipline['id'] for discipline in disciplines}
    selected_discipline = st.selectbox("Sélectionner une discipline", options=list(discipline_options.keys()))
    discipline_id = discipline_options[selected_discipline]
    
    # Options supplémentaires
    analyze_by_level = st.checkbox("Analyser par niveau", value=True)
    analyze_by_gender = st.checkbox("Analyser par sexe", value=True)
    include_charts = st.checkbox("Inclure les graphiques", value=True)
    
    if st.button("Générer le rapport"):
        st.subheader(f"Rapport de discipline - {selected_discipline} - Semestre 1")
        
        # Récupérer les informations de l'établissement
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            st.markdown(f"""
            **Établissement**: {config['nom_etablissement']}  
            **Année scolaire**: {annee_scolaire}  
            **Semestre**: 1
            """)
        
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
        
        # Afficher les statistiques globales
        st.markdown("### Statistiques globales")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre d'élèves", stats_global['nb_eleves'])
        col2.metric("Moyenne générale", round(stats_global['moyenne'], 2))
        col3.metric("Taux de réussite", f"{round(taux_reussite, 2)}%")
        
        # Analyse par niveau si demandée
        if analyze_by_level:
            st.markdown("### Analyse par niveau")
            
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
                    "nb_eleves": "Nombre d'élèves",
                    "moyenne": "Moyenne",
                    "nb_moyenne": "Élèves ≥ 10",
                    "taux_reussite": "Taux de réussite (%)"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Graphique si demandé
            if include_charts:
                import plotly.express as px
                
                fig = px.bar(
                    df_niveaux,
                    x="niveau",
                    y="moyenne",
                    color="niveau",
                    title=f"Moyenne par niveau - {selected_discipline}"
                )
                
                fig.update_layout(
                    xaxis_title="Niveau",
                    yaxis_title="Moyenne",
                    yaxis=dict(range=[0, 20])
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Analyse par sexe si demandée
        if analyze_by_gender:
            st.markdown("### Analyse par sexe")
            
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
                    "nb_eleves": "Nombre d'élèves",
                    "moyenne": "Moyenne",
                    "nb_moyenne": "Élèves ≥ 10",
                    "taux_reussite": "Taux de réussite (%)"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Graphique si demandé
            if include_charts and not df_sexe.empty:
                import plotly.graph_objects as go
                
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
                    xaxis_title="Sexe",
                    yaxis_title="Moyenne",
                    yaxis=dict(range=[0, 20])
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Bouton pour télécharger le rapport en Excel
        st.markdown("### Télécharger le rapport")
        
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def generate_honor_roll(conn, annee_scolaire):
    """Génère un tableau d'honneur"""
    
    # Options du tableau d'honneur
    top_n = st.number_input("Nombre d'élèves à inclure", min_value=1, max_value=100, value=10)
    
    # Options de filtrage
    filter_type = st.radio(
        "Type de filtrage",
        ["Global", "Par niveau", "Par classe"],
        captions=["Meilleurs élèves de l'établissement", "Meilleurs élèves par niveau", "Meilleurs élèves par classe"]
    )
    
    if st.button("Générer le tableau d'honneur"):
        st.subheader(f"Tableau d'honneur - Semestre 1")
        
        # Récupérer les informations de l'établissement
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Configuration LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            st.markdown(f"""
            **Établissement**: {config['nom_etablissement']}  
            **Année scolaire**: {annee_scolaire}  
            **Semestre**: 1
            """)
        
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
    """Génère un tableau d'honneur global"""
    
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
    
    # Ajouter le rang dans le tableau d'honneur
    df_honor.insert(0, 'rang_honneur', range(1, len(df_honor) + 1))
    
    # Afficher le tableau
    st.markdown("### Meilleurs élèves de l'établissement")
    
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
            "rang": "Rang en classe"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Bouton pour télécharger le tableau d'honneur
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_honor.to_excel(writer, sheet_name='Tableau_Honneur', index=False)
    
    # Proposer le téléchargement
    st.download_button(
        label="📥 Télécharger le tableau d'honneur",
        data=output.getvalue(),
        file_name=f"Tableau_Honneur_Global_S1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def generate_level_honor_roll(conn, annee_scolaire, top_n):
    """Génère un tableau d'honneur par niveau"""
    
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
        st.markdown(f"### Meilleurs élèves de {niveau['libelle']}")
        
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
                "rang": "Rang en classe"
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Bouton pour télécharger tous les tableaux d'honneur
    st.markdown("### Télécharger les tableaux d'honneur")
    
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
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def generate_class_honor_roll(conn, annee_scolaire, top_n):
    """Génère un tableau d'honneur par classe"""
    
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
        st.markdown(f"### Meilleurs élèves de {classe['niveau']} {classe['libelle']}")
        
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
                "rang": "Rang en classe"
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Bouton pour télécharger tous les tableaux d'honneur
    st.markdown("### Télécharger les tableaux d'honneur")
    
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
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def generate_global_stats(conn, annee_scolaire):
    """Génère un rapport statistique global"""
    
    st.markdown("### Rapport statistique global - Semestre 1")
    
    # Récupérer les informations de l'établissement
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Configuration LIMIT 1")
    config = cursor.fetchone()
    
    if config:
        st.markdown(f"""
        **Établissement**: {config['nom_etablissement']}  
        **Année scolaire**: {annee_scolaire}  
        **Semestre**: 1
        """)
    
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
    st.markdown("#### Statistiques générales")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre d'élèves", stats_global['nb_eleves'])
    col2.metric("Moyenne générale", round(stats_global['moyenne_generale'], 2))
    col3.metric("Taux de réussite", f"{round(taux_reussite, 2)}%")
    
    # Statistiques par niveau
    st.markdown("#### Statistiques par niveau")
    
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
                "nb_eleves": "Nombre d'élèves",
                "moyenne": "Moyenne",
                "nb_moyenne": "Élèves ≥ 10",
                "taux_reussite": "Taux de réussite (%)"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Graphique des moyennes par niveau
        import plotly.express as px
        
        fig = px.bar(
            df_niveaux,
            x="niveau",
            y="moyenne",
            color="niveau",
            title="Moyenne par niveau"
        )
        
        fig.update_layout(
            xaxis_title="Niveau",
            yaxis_title="Moyenne",
            yaxis=dict(range=[0, 20])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques par classe
    st.markdown("#### Statistiques par classe")
    
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
                "nb_eleves": "Nombre d'élèves",
                "moyenne": "Moyenne",
                "nb_moyenne": "Élèves ≥ 10",
                "taux_reussite": "Taux de réussite (%)"
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Statistiques par discipline
    st.markdown("#### Statistiques par discipline")
    
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
                "nb_eleves": "Nombre d'élèves",
                "moyenne": "Moyenne",
                "nb_moyenne": "Élèves ≥ 10",
                "taux_reussite": "Taux de réussite (%)"
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
            title="Moyenne par discipline"
        )
        
        fig.update_layout(
            xaxis_title="Discipline",
            yaxis_title="Moyenne",
            yaxis=dict(range=[0, 20])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Bouton pour télécharger le rapport statistique
    st.markdown("### Télécharger le rapport statistique")
    
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
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def show_import_interface():
    """Affiche l'interface d'importation des données"""
    
    st.subheader("Base d'importation - Semestre 1")
    
    # Vérifier si une année scolaire est active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
    annee_result = cursor.fetchone()
    
    if not annee_result:
        st.warning("Aucune année scolaire active. Veuillez configurer l'année scolaire dans les paramètres.")
        return
    
    annee_scolaire = annee_result[0]
    
    # Afficher l'année scolaire active
    st.info(f"Importation pour l'année scolaire: {annee_scolaire}")
    
    # Récupérer les niveaux disponibles
    cursor.execute("SELECT id, libelle FROM Niveaux WHERE etat = 'actif' ORDER BY libelle")
    niveaux = cursor.fetchall()
    
    if not niveaux:
        st.warning("Aucun niveau actif trouvé. Veuillez configurer les niveaux dans les paramètres.")
        return
    
    # Sélecteur de niveau
    niveau_options = {niveau['libelle']: niveau['id'] for niveau in niveaux}
    selected_niveau = st.selectbox("📚 Sélectionner le niveau", options=list(niveau_options.keys()))
    niveau_id = niveau_options[selected_niveau]
    
    # Récupérer les classes du niveau sélectionné
    cursor.execute(
        "SELECT id, libelle FROM Classes WHERE id_niveau = ? AND etat = 'actif' ORDER BY libelle",
        (niveau_id,)
    )
    classes = cursor.fetchall()
    
    # Si aucune classe n'existe pour ce niveau, proposer d'en créer une
    if not classes:
        st.warning(f"Aucune classe active trouvée pour le niveau {selected_niveau}.")
        
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
    selected_classe = st.selectbox("🏷️ Sélectionner la classe", options=list(classe_options.keys()))
    classe_id = classe_options[selected_classe]
    
    conn.close()
    
    # Uploader le fichier Excel
    fichier = st.file_uploader("📂 Importer un fichier Excel PLANETE", type=["xlsx"])
    
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
                
                st.subheader("📋 Aperçu des moyennes générales")
                st.dataframe(df_moyennes)
                
                # Bouton pour confirmer l'importation
                if st.button("✅ Confirmer et importer les données"):
                    with st.spinner("Importation des données..."):
                        # Sécuriser à nouveau juste avant l'import
                        df_moyennes["Prenom"] = df_moyennes["Prenom"].fillna("Non défini").replace("", "Non défini")
                        df_moyennes["Nom"] = df_moyennes["Nom"].fillna("Non défini").replace("", "Non défini")
                        df_moyennes["IEN"] = df_moyennes["IEN"].fillna("").replace("", "")
                        sauvegarder_dans_fichier_central(df_moyennes, df_final, selected_niveau, selected_classe, 1)  # 1 pour semestre 1
                        
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
    else:
        # Instructions pour l'importation
        st.info("""
        ### Instructions pour l'importation:
        1. Exportez les données de PLANETE au format Excel
        2. Assurez-vous que le fichier contient les feuilles "Moyennes eleves" et "Données détaillées"
        3. Sélectionnez le niveau et la classe correspondants
        4. Importez le fichier en cliquant sur le bouton ci-dessus
        5. Vérifiez les données avant de confirmer l'importation
        """)
    
    # --- Suppression massive (niveau ou classe) en haut de page ---
    st.markdown("### Suppression massive")
    colA, colB = st.columns(2)
    with colA:
        if st.button("❌ Supprimer tout le niveau"):
            from ..utils.excel_utils import synchroniser_suppression_niveau
            try:
                synchroniser_suppression_niveau(selected_niveau, 1)
                st.success("Toutes les données du niveau ont été supprimées (base + fichier central)")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erreur lors de la suppression du niveau : {e}")
    with colB:
        if st.button("❌ Supprimer toute la classe"):
            from ..utils.excel_utils import synchroniser_suppression_classe
            try:
                synchroniser_suppression_classe(selected_niveau, selected_classe, 1)
                st.success("Toutes les données de la classe ont été supprimées (base + fichier central)")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erreur lors de la suppression de la classe : {e}")

    # --- Historique des imports ---
    st.markdown("### Historique des imports")
    import os
    import pandas as pd
    from datetime import datetime
    from ..config import FICHIER_CENTRAL
    if os.path.exists(FICHIER_CENTRAL):
        try:
            df_moy = pd.read_excel(FICHIER_CENTRAL, sheet_name="Moyennes eleves")
            # Correction: utiliser les bons noms de colonnes (insensible à la casse)
            col_niveau = next((c for c in df_moy.columns if c.lower() == 'niveau'), None)
            col_classe = next((c for c in df_moy.columns if c.lower() == 'classe'), None)
            col_semestre = next((c for c in df_moy.columns if c.lower() == 'semestre'), None)
            col_ien = next((c for c in df_moy.columns if c.lower() == 'ien'), None)
            if not (col_niveau and col_classe and col_semestre and col_ien):
                st.warning("Colonnes manquantes dans le fichier centralisé. Impossible d'afficher l'historique.")
            else:
                historique = df_moy.groupby([col_niveau, col_classe, col_semestre]).agg(
                    nb_eleves=(col_ien, "count")
                ).reset_index()
                # Utiliser les vrais noms de colonnes pour l'accès
                for idx, row in historique.iterrows():
                    niveau_val = row[col_niveau] if col_niveau in historique.columns else row[0]
                    classe_val = row[col_classe] if col_classe in historique.columns else row[1]
                    semestre_val = row[col_semestre] if col_semestre in historique.columns else row[2]
                    nb_eleves = row['nb_eleves']
                    cols = st.columns([2,2,1,2,1])
                    cols[0].write(niveau_val)
                    cols[1].write(classe_val)
                    cols[2].write(f"S{semestre_val}")
                    cols[3].write(nb_eleves)
                    if cols[4].button("Supprimer", key=f"suppr_{idx}"):
                        from ..utils.excel_utils import synchroniser_suppression_classe
                        try:
                            synchroniser_suppression_classe(niveau_val, classe_val, semestre_val)
                            st.success(f"Import {niveau_val} {classe_val} S{semestre_val} supprimé (base + fichier central)")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la suppression : {e}")
                # Affichage du tableau historique
                historique_aff = historique.rename(columns={col_niveau: "Niveau", col_classe: "Classe", col_semestre: "Semestre"})
                st.dataframe(historique_aff, use_container_width=True)
        except Exception as e:
            st.info("Aucun historique d'import disponible ou erreur de lecture.")
    else:
        st.info("Aucun fichier centralisé trouvé.")

    # Onglets pour visualiser les données de la base
    st.subheader("Données existantes dans la base")
    onglet1, onglet2 = st.tabs(["Moyennes élèves (base)", "Données détaillées (base)"])

    # --- Moyennes élèves (base) ---
    with onglet1:
        conn = get_db_connection()
        query = '''
            SELECT e.ien, e.prenom, e.nom, e.sexe, e.date_naissance, e.lieu_naissance, c.libelle as classe, n.libelle as niveau, mg.moyenne, mg.rang, mg.retard, mg.absence, mg.conseil_discipline, mg.appreciation, mg.observation, mg.annee_scolaire
            FROM Eleves e
            JOIN Classes c ON e.id_classe = c.id
            JOIN Niveaux n ON c.id_niveau = n.id
            JOIN Moyennes_Generales_S1 mg ON e.ien = mg.ien
            WHERE c.id_niveau = ? AND c.id = ?
            ORDER BY mg.rang
        '''
        df_moy_base = pd.read_sql_query(query, conn, params=(niveau_id, classe_id))
        conn.close()
        st.dataframe(df_moy_base, use_container_width=True)

    # --- Données détaillées (base) ---
    with onglet2:
        conn = get_db_connection()
        query = '''
            SELECT e.ien, e.prenom, e.nom, e.sexe, d.libelle as discipline, notes.moy_d
            FROM Eleves e
            JOIN Notes_S1 notes ON e.ien = notes.ien
            JOIN Disciplines d ON notes.id_discipline = d.id
            JOIN Classes c ON e.id_classe = c.id
            WHERE c.id_niveau = ? AND c.id = ?
        '''
        df_det_base = pd.read_sql_query(query, conn, params=(niveau_id, classe_id))
        conn.close()
        if not df_det_base.empty:
            df_pivot = df_det_base.pivot_table(
                index=["ien", "prenom", "nom", "sexe"],
                columns="discipline",
                values="moy_d"
            ).reset_index()
            df_pivot.columns.name = None
            st.dataframe(df_pivot, use_container_width=True)
        else:
            st.info("Aucune donnée détaillée disponible pour cette classe.")
# ...existing code...