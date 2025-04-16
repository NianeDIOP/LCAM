import streamlit as st
import pandas as pd
import os
import sqlite3
import shutil
from datetime import datetime
from ..config import DB_PATH, DATA_DIR, DEFAULT_ETABLISSEMENT, NIVEAUX
from ..utils.db_utils import get_db_connection, execute_query, insert_data, update_data

def show_parametres_view():
    """Affiche la page des paramètres de l'application"""
    
    st.title("⚙️ Paramètres")
    
    # Créer des onglets pour les différentes sections de paramètres
    tab1, tab2, tab3, tab4 = st.tabs(["Informations de base", "Configuration académique", "Année scolaire", "Sauvegarde/Restauration"])
    
    # Onglet 1: Informations de base
    with tab1:
        show_info_base_settings()
    
    # Onglet 2: Configuration académique
    with tab2:
        show_academic_settings()
    
    # Onglet 3: Année scolaire
    with tab3:
        show_school_year_settings()
    
    # Onglet 4: Sauvegarde/Restauration
    with tab4:
        show_backup_restore_settings()

def show_info_base_settings():
    """Affiche et gère les paramètres d'informations de base"""
    
    st.subheader("Informations de l'établissement")
    
    # Récupérer les informations actuelles si elles existent
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Configuration LIMIT 1")
    config = cursor.fetchone()
    conn.close()
    
    # Utiliser des valeurs par défaut
    nom_etablissement = ""
    adresse = ""
    telephone = ""
    inspection_academique = ""
    inspection_education = ""
    
    # Si des configurations existent, les récupérer
    if config:
        try:
            # Tenter de récupérer les valeurs de la configuration
            nom_etablissement = config.get('nom_etablissement', "")
            adresse = config.get('adresse', "")
            telephone = config.get('telephone', "")
            inspection_academique = config.get('inspection_academique', "")
            inspection_education = config.get('inspection_education', "")
        except:
            # En cas d'erreur, afficher un message
            st.warning("Impossible de récupérer les configurations existantes.")
    
    # Formulaire pour les informations
    with st.form("form_etablissement"):
        nom_etablissement_input = st.text_input("Nom de l'établissement", value=nom_etablissement)
        adresse_input = st.text_input("Adresse", value=adresse)
        telephone_input = st.text_input("Téléphone", value=telephone)
        inspection_academique_input = st.text_input("Inspection d'académie", value=inspection_academique)
        inspection_education_input = st.text_input("Inspection de l'éducation et de la formation", value=inspection_education)
        
        submitted = st.form_submit_button("Enregistrer")
        
        if submitted:
            # Préparer les données
            data = {
                'nom_etablissement': nom_etablissement_input,
                'adresse': adresse_input,
                'telephone': telephone_input,
                'inspection_academique': inspection_academique_input,
                'inspection_education': inspection_education_input
            }
            
            # Mettre à jour ou insérer dans la base de données
            try:
                if config and 'id' in config:
                    update_data('Configuration', data, f"id = {config['id']}")
                    st.success("✅ Informations de l'établissement mises à jour avec succès")
                else:
                    insert_data('Configuration', data)
                    st.success("✅ Informations de l'établissement enregistrées avec succès")
                
                # Recharger la page pour afficher les nouvelles informations
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement des informations: {str(e)}")

def show_academic_settings():
    """Affiche et gère les paramètres académiques (niveaux et classes)"""
    
    # Séparation en deux colonnes
    col1, col2 = st.columns(2)
    
    # Colonne 1: Gestion des niveaux
    with col1:
        st.subheader("Gestion des niveaux")
        
        # Récupérer les niveaux existants
        conn = get_db_connection()
        niveaux_db = pd.read_sql_query("SELECT * FROM Niveaux ORDER BY id", conn)
        conn.close()
        
        # Afficher le tableau des niveaux avec possibilité d'édition
        edited_niveaux = st.data_editor(
            niveaux_db,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "libelle": st.column_config.TextColumn("Libellé"),
                "etat": st.column_config.SelectboxColumn(
                    "État",
                    options=["actif", "inactif"],
                    required=True
                )
            },
            hide_index=True,
            num_rows="dynamic"
        )
        
        # Bouton pour sauvegarder les modifications
        if st.button("Enregistrer les niveaux"):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Pour chaque niveau modifié
            for _, row in edited_niveaux.iterrows():
                if row['id'] in niveaux_db['id'].values:
                    # Mise à jour
                    cursor.execute(
                        "UPDATE Niveaux SET libelle = ?, etat = ? WHERE id = ?",
                        (row['libelle'], row['etat'], row['id'])
                    )
                else:
                    # Insertion nouveau niveau
                    cursor.execute(
                        "INSERT INTO Niveaux (libelle, etat) VALUES (?, ?)",
                        (row['libelle'], row['etat'])
                    )
            
            conn.commit()
            conn.close()
            st.success("✅ Niveaux enregistrés avec succès")
            st.experimental_rerun()
    
    # Colonne 2: Gestion des classes
    with col2:
        st.subheader("Gestion des classes")
        
        # Récupérer les niveaux actifs pour le sélecteur
        conn = get_db_connection()
        niveaux_actifs = pd.read_sql_query("SELECT id, libelle FROM Niveaux WHERE etat = 'actif' ORDER BY libelle", conn)
        
        # Sélection du niveau pour afficher ses classes
        niveau_id = st.selectbox(
            "Sélectionner un niveau",
            options=niveaux_actifs['id'].tolist(),
            format_func=lambda x: niveaux_actifs[niveaux_actifs['id'] == x]['libelle'].iloc[0]
        )
        
        # Récupérer les classes du niveau sélectionné
        classes_db = pd.read_sql_query(
            "SELECT * FROM Classes WHERE id_niveau = ? ORDER BY libelle",
            conn,
            params=(niveau_id,)
        )
        conn.close()
        
        # Ajouter une colonne id_niveau pour les nouvelles classes
        if 'id_niveau' not in classes_db.columns:
            classes_db['id_niveau'] = niveau_id
        
        # Afficher le tableau des classes avec possibilité d'édition
        edited_classes = st.data_editor(
            classes_db,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "id_niveau": st.column_config.NumberColumn("ID Niveau", disabled=True),
                "libelle": st.column_config.TextColumn("Libellé"),
                "effectif": st.column_config.NumberColumn("Effectif"),
                "etat": st.column_config.SelectboxColumn(
                    "État",
                    options=["actif", "inactif"],
                    required=True
                )
            },
            hide_index=True,
            num_rows="dynamic"
        )
        
        # Bouton pour sauvegarder les modifications
        if st.button("Enregistrer les classes"):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Pour chaque classe modifiée
            for _, row in edited_classes.iterrows():
                # S'assurer que id_niveau est défini
                row_id_niveau = row.get('id_niveau', niveau_id)
                
                if 'id' in row and not pd.isna(row['id']) and row['id'] in classes_db['id'].values:
                    # Mise à jour
                    cursor.execute(
                        "UPDATE Classes SET libelle = ?, effectif = ?, etat = ? WHERE id = ?",
                        (row['libelle'], row['effectif'], row['etat'], row['id'])
                    )
                else:
                    # Insertion nouvelle classe
                    cursor.execute(
                        "INSERT INTO Classes (id_niveau, libelle, effectif, etat) VALUES (?, ?, ?, ?)",
                        (row_id_niveau, row['libelle'], row['effectif'], row['etat'])
                    )
            
            conn.commit()
            conn.close()
            st.success("✅ Classes enregistrées avec succès")
            st.experimental_rerun()

def show_school_year_settings():
    """Affiche et gère les paramètres d'année scolaire"""
    
    st.subheader("Gestion des années scolaires")
    
    # Récupérer les années scolaires existantes
    conn = get_db_connection()
    annees_db = pd.read_sql_query("SELECT * FROM Annee_Scolaire ORDER BY id DESC", conn)
    conn.close()
    
    # Afficher le tableau des années scolaires avec possibilité d'édition
    edited_annees = st.data_editor(
        annees_db,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "libelle": st.column_config.TextColumn("Libellé"),
            "etat": st.column_config.SelectboxColumn(
                "État",
                options=["actif", "inactif"],
                required=True
            ),
            "date_debut": st.column_config.DateColumn("Date début"),
            "date_fin": st.column_config.DateColumn("Date fin")
        },
        hide_index=True,
        num_rows="dynamic"
    )
    
    # Bouton pour sauvegarder les modifications
    if st.button("Enregistrer les années scolaires"):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Si une année est marquée comme active, désactiver les autres
        active_years = edited_annees[edited_annees['etat'] == 'actif']
        if not active_years.empty:
            active_id = active_years.iloc[0]['id']
            cursor.execute("UPDATE Annee_Scolaire SET etat = 'inactif' WHERE id != ?", (active_id,))
        
        # Pour chaque année modifiée
        for _, row in edited_annees.iterrows():
            if row['id'] in annees_db['id'].values:
                # Mise à jour
                cursor.execute(
                    "UPDATE Annee_Scolaire SET libelle = ?, etat = ?, date_debut = ?, date_fin = ? WHERE id = ?",
                    (row['libelle'], row['etat'], row['date_debut'], row['date_fin'], row['id'])
                )
            else:
                # Insertion nouvelle année
                cursor.execute(
                    "INSERT INTO Annee_Scolaire (libelle, etat, date_debut, date_fin) VALUES (?, ?, ?, ?)",
                    (row['libelle'], row['etat'], row['date_debut'], row['date_fin'])
                )
        
        conn.commit()
        conn.close()
        st.success("✅ Années scolaires enregistrées avec succès")
        st.experimental_rerun()

def show_backup_restore_settings():
    """Affiche et gère les paramètres de sauvegarde et restauration"""
    
    st.subheader("Sauvegarde et restauration des données")
    
    col1, col2 = st.columns(2)
    
    # Colonne 1: Sauvegarde
    with col1:
        st.write("#### Sauvegarde de la base de données")
        
        if st.button("Créer une sauvegarde"):
            # Créer un dossier pour les sauvegardes s'il n'existe pas
            backup_dir = os.path.join(DATA_DIR, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Nom du fichier de sauvegarde avec date et heure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"lcams_backup_{timestamp}.db")
            
            # Copier la base de données
            try:
                shutil.copy2(DB_PATH, backup_file)
                st.success(f"✅ Sauvegarde créée avec succès: {os.path.basename(backup_file)}")
            except Exception as e:
                st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
    
    # Colonne 2: Restauration
    with col2:
        st.write("#### Restauration de la base de données")
        
        # Liste des fichiers de sauvegarde disponibles
        backup_dir = os.path.join(DATA_DIR, "backups")
        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith("lcams_backup_") and f.endswith(".db")]
            backup_files.sort(reverse=True)  # Les plus récents en premier
            
            if backup_files:
                selected_backup = st.selectbox(
                    "Sélectionner une sauvegarde à restaurer",
                    options=backup_files,
                    format_func=lambda x: f"{x.replace('lcams_backup_', '').replace('.db', '').replace('_', ' à ')}"
                )
                
                if st.button("Restaurer la sauvegarde"):
                    backup_path = os.path.join(backup_dir, selected_backup)
                    
                    # Fermer toutes les connexions à la base de données
                    try:
                        # Créer une sauvegarde de la base actuelle avant restauration
                        current_backup = os.path.join(backup_dir, f"lcams_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
                        shutil.copy2(DB_PATH, current_backup)
                        
                        # Restaurer la sauvegarde
                        shutil.copy2(backup_path, DB_PATH)
                        st.success("✅ Base de données restaurée avec succès")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la restauration: {str(e)}")
            else:
                st.info("Aucune sauvegarde disponible")
        else:
            st.info("Aucune sauvegarde disponible")
    
    # Section de purge des données
    st.divider()
    st.write("#### Purge des données")
    
    with st.expander("Options de purge (ATTENTION: Actions irréversibles)"):
        purge_option = st.radio(
            "Sélectionner une option de purge",
            ["Purger les données d'un semestre", "Purger toute la base de données"],
            captions=["Supprime uniquement les données d'un semestre spécifique", "Réinitialise complètement la base de données"]
        )
        
        if purge_option == "Purger les données d'un semestre":
            semestre = st.selectbox("Sélectionner le semestre à purger", [1, 2])
            annee_scolaire = st.text_input("Confirmer l'année scolaire (ex: 2023-2024)")
            
            if st.button("Purger les données du semestre"):
                if annee_scolaire:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Supprimer les données du semestre spécifié
                    cursor.execute(f"DELETE FROM Notes_S{semestre} WHERE annee_scolaire = ?", (annee_scolaire,))
                    cursor.execute(f"DELETE FROM Moyennes_Generales_S{semestre} WHERE annee_scolaire = ?", (annee_scolaire,))
                    
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Données du semestre {semestre} pour l'année {annee_scolaire} supprimées avec succès")
                else:
                    st.warning("⚠️ Veuillez confirmer l'année scolaire")
        
        elif purge_option == "Purger toute la base de données":
            confirmation = st.text_input("Tapez 'CONFIRMER' pour réinitialiser la base de données")
            
            if st.button("Réinitialiser la base de données"):
                if confirmation == "CONFIRMER":
                    # Créer une sauvegarde avant réinitialisation
                    backup_dir = os.path.join(DATA_DIR, "backups")
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_file = os.path.join(backup_dir, f"lcams_pre_reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
                    
                    try:
                        # Créer sauvegarde
                        shutil.copy2(DB_PATH, backup_file)
                        
                        # Supprimer la base actuelle
                        if os.path.exists(DB_PATH):
                            os.remove(DB_PATH)
                        
                        # Réinitialiser la base (sera recréée au prochain démarrage)
                        st.success("✅ Base de données réinitialisée avec succès. Veuillez redémarrer l'application.")
                        st.info(f"Une sauvegarde a été créée: {os.path.basename(backup_file)}")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la réinitialisation: {str(e)}")
                else:
                    st.warning("⚠️ Confirmation incorrecte")