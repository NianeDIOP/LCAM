import pandas as pd
from io import BytesIO
import os
import sqlite3
from ..config import FICHIER_CENTRAL, DB_PATH

def charger_et_nettoyer(fichier_excel):
    """
    Charge et nettoie un fichier Excel de la plateforme PLANETE
    
    Args:
        fichier_excel: Le fichier Excel à traiter
        
    Returns:
        df_moyennes: DataFrame des moyennes générales des élèves
        df_final: DataFrame des données nettoyées avec les moyennes par matière
        df_detail_moy_d: DataFrame des moyennes par discipline uniquement
    """
    try:
        xls = pd.ExcelFile(fichier_excel)

        # Lecture de la feuille Moyennes eleves
        df_moyennes = pd.read_excel(xls, sheet_name="Moyennes eleves", skiprows=range(11), header=0)

        # Lecture de la feuille Données détaillées
        df_detail = pd.read_excel(xls, sheet_name="Données détaillées", skiprows=range(8), header=[0, 1])
        disciplines = df_detail.columns.get_level_values(0).tolist()
        sous_colonnes = df_detail.columns.get_level_values(1).tolist()

        # Remplissage des colonnes "Unnamed"
        for i in range(len(disciplines)):
            if "Unnamed" in disciplines[i]:
                disciplines[i] = disciplines[i - 1]

        # Extraction des colonnes infos (les 3 premières)
        info_colonnes = df_detail.iloc[:, :3]
        info_colonnes.columns = [col[0] for col in info_colonnes.columns]

        # Extraction des colonnes Moy D
        colonnes_moy_d = [i for i, col in enumerate(sous_colonnes) if col == "Moy D"]
        df_detail_moy_d = df_detail.iloc[:, colonnes_moy_d]
        noms_moy_d = [disciplines[i] for i in colonnes_moy_d]
        df_detail_moy_d.columns = noms_moy_d

        # Fusion info + moyennes
        df_final = pd.concat([info_colonnes, df_detail_moy_d], axis=1)

        # Ajout colonne Sexe si disponible
        if 'Sexe' in df_moyennes.columns:
            df_final.insert(3, 'Sexe', df_moyennes['Sexe'])
            
        return df_moyennes, df_final, df_detail_moy_d
        
    except Exception as e:
        raise Exception(f"Erreur lors du chargement du fichier Excel: {str(e)}")

def sauvegarder_dans_fichier_central(df_moyennes, df_detail, niveau, classe, semestre):
    """
    Sauvegarde les données dans le fichier Excel central et dans la base SQLite
    
    Args:
        df_moyennes: DataFrame des moyennes générales
        df_detail: DataFrame des données détaillées
        niveau: Niveau scolaire
        classe: Classe
        semestre: Semestre (1 ou 2)
    """
    try:
        df_moyennes = df_moyennes.copy()
        df_detail = df_detail.copy()
        
        # Normaliser les noms des colonnes pour éviter les problèmes d'accès aux données
        # Standardiser les noms de colonnes pour qu'ils correspondent à la base de données
        column_mapping_moyennes = {
            'IEN': 'IEN',
            'Prénom': 'prenom',
            'Nom': 'nom',
            'Sexe': 'sexe',
            'Date naissance': 'date_naissance',
            'Lieu naissance': 'lieu_naissance',
            'Retard': 'retard',
            'Absence': 'absence',
            'C.D.': 'conseil_discipline',
            'Moy': 'moyenne',
            'Rang': 'rang',
            'Décision conseil': 'decision_conseil',
            'Appréciation': 'appreciation',
            'Observation conseil': 'observation_conseil'
        }
        
        # Renommer les colonnes qui existent dans le DataFrame
        for old_col, new_col in column_mapping_moyennes.items():
            if old_col in df_moyennes.columns:
                df_moyennes.rename(columns={old_col: new_col}, inplace=True)
        
        # Ajout des colonnes de contexte
        df_moyennes['niveau'] = niveau
        df_moyennes['classe'] = classe
        df_moyennes['semestre'] = semestre
        df_detail['niveau'] = niveau
        df_detail['classe'] = classe
        df_detail['semestre'] = semestre
        
        # Réorganiser les colonnes pour mettre Niveau, Classe et Semestre en premier
        first_cols = ['niveau', 'classe', 'semestre']
        moyennes_cols = first_cols + [col for col in df_moyennes.columns if col not in first_cols]
        detail_cols = first_cols + [col for col in df_detail.columns if col not in first_cols]
        
        df_moyennes = df_moyennes[moyennes_cols]
        df_detail = df_detail[detail_cols]
        
        # Vérifier si le fichier central existe
        if os.path.exists(FICHIER_CENTRAL):
            try:
                xls = pd.ExcelFile(FICHIER_CENTRAL)
                df_moy_central = pd.read_excel(xls, sheet_name="Moyennes eleves")
                df_detail_central = pd.read_excel(xls, sheet_name="Données détaillées")
            except Exception:
                df_moy_central = pd.DataFrame()
                df_detail_central = pd.DataFrame()
                
            # Vérifier s'il y a déjà des données pour cette classe/niveau/semestre
            filter_condition = False
            if 'niveau' in df_moy_central.columns and 'classe' in df_moy_central.columns and 'semestre' in df_moy_central.columns:
                filter_condition = (df_moy_central['niveau'] == niveau) & (df_moy_central['classe'] == classe) & (df_moy_central['semestre'] == semestre)
            
            if isinstance(filter_condition, pd.Series) and filter_condition.any():
                # Supprimer les données existantes pour ce niveau/classe/semestre
                df_moy_central = df_moy_central[~filter_condition]
                
                detail_filter = False
                if 'niveau' in df_detail_central.columns and 'classe' in df_detail_central.columns and 'semestre' in df_detail_central.columns:
                    detail_filter = (df_detail_central['niveau'] == niveau) & (df_detail_central['classe'] == classe) & (df_detail_central['semestre'] == semestre)
                
                if isinstance(detail_filter, pd.Series):
                    df_detail_central = df_detail_central[~detail_filter]
                
            # Concaténer avec les nouvelles données
            df_moyennes = pd.concat([df_moy_central, df_moyennes], ignore_index=True)
            df_detail = pd.concat([df_detail_central, df_detail], ignore_index=True)
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(FICHIER_CENTRAL), exist_ok=True)
        
        # Écriture dans le fichier Excel central
        with pd.ExcelWriter(FICHIER_CENTRAL, engine='xlsxwriter') as writer:
            df_moyennes.to_excel(writer, sheet_name="Moyennes eleves", index=False)
            df_detail.to_excel(writer, sheet_name="Données détaillées", index=False)
        
        # Sauvegarde dans la base SQLite
        conn = sqlite3.connect(DB_PATH)
        try:
            # Déterminer quelle table doit être mise à jour selon le semestre
            table_moyennes = f"Moyennes_Generales_S{semestre}"
            table_notes = f"Notes_S{semestre}"
            
            # Récupérer l'année scolaire active
            cursor = conn.cursor()
            cursor.execute("SELECT libelle FROM Annee_Scolaire WHERE etat = 'actif' LIMIT 1")
            result = cursor.fetchone()
            annee_scolaire = result[0] if result else "Inconnue"
            
            # Récupérer l'ID de la classe
            cursor.execute("""
                SELECT c.id FROM Classes c
                JOIN Niveaux n ON c.id_niveau = n.id
                WHERE n.libelle = ? AND c.libelle = ?
            """, (niveau, classe))
            
            classe_id_result = cursor.fetchone()
            if not classe_id_result:
                # Créer la classe si elle n'existe pas
                cursor.execute("SELECT id FROM Niveaux WHERE libelle = ?", (niveau,))
                result = cursor.fetchone()
                niveau_id = result[0] if result else None
                
                if niveau_id:
                    cursor.execute("""
                        INSERT INTO Classes (id_niveau, libelle, effectif) 
                        VALUES (?, ?, ?)
                    """, (niveau_id, classe, len(df_moyennes)))
                    
                    classe_id = cursor.lastrowid
                else:
                    raise Exception(f"Niveau '{niveau}' non trouvé dans la base de données")
            else:
                classe_id = classe_id_result[0]
            
            # Pour chaque élève, insérer dans la table Eleves s'il n'existe pas déjà
            for _, eleve in df_moyennes.iterrows():
                ien = eleve.get('IEN')
                if not ien:
                    continue  # Ignorer les lignes sans IEN
                # Sécuriser les champs obligatoires
                prenom = eleve.get('prenom', eleve.get('Prenom', ''))
                nom = eleve.get('nom', eleve.get('Nom', ''))
                if not prenom or pd.isna(prenom) or str(prenom).strip() == '':
                    prenom = "Non défini"
                if not nom or pd.isna(nom) or str(nom).strip() == '':
                    nom = "Non défini"
                cursor.execute("SELECT COUNT(*) FROM Eleves WHERE ien = ?", (ien,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO Eleves (ien, prenom, nom, sexe, date_naissance, lieu_naissance, id_classe, annee_scolaire)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ien,
                        prenom,
                        nom,
                        eleve.get('sexe', eleve.get('Sexe', '')),
                        eleve.get('date_naissance', eleve.get('Date naissance', '')),
                        eleve.get('lieu_naissance', eleve.get('Lieu naissance', '')),
                        classe_id,
                        annee_scolaire
                    ))
                
                # Insérer les moyennes générales
                try:
                    # Convertir les valeurs numériques de manière sécurisée
                    moyenne = 0
                    if 'moyenne' in eleve:
                        moyenne = float(eleve['moyenne']) if isinstance(eleve['moyenne'], (int, float, str)) and str(eleve['moyenne']).replace('.', '', 1).isdigit() else 0
                    elif 'Moy' in eleve:
                        moyenne = float(eleve['Moy']) if isinstance(eleve['Moy'], (int, float, str)) and str(eleve['Moy']).replace('.', '', 1).isdigit() else 0
                    
                    rang = 0
                    if 'rang' in eleve:
                        rang = int(float(eleve['rang'])) if isinstance(eleve['rang'], (int, float, str)) and str(eleve['rang']).replace('.', '', 1).isdigit() else 0
                    elif 'Rang' in eleve:
                        rang = int(float(eleve['Rang'])) if isinstance(eleve['Rang'], (int, float, str)) and str(eleve['Rang']).replace('.', '', 1).isdigit() else 0
                    
                    retard = 0
                    if 'retard' in eleve:
                        retard = int(float(eleve['retard'])) if isinstance(eleve['retard'], (int, float, str)) and str(eleve['retard']).replace('.', '', 1).isdigit() else 0
                    elif 'Retard' in eleve:
                        retard = int(float(eleve['Retard'])) if isinstance(eleve['Retard'], (int, float, str)) and str(eleve['Retard']).replace('.', '', 1).isdigit() else 0
                    
                    absence = 0
                    if 'absence' in eleve:
                        absence = int(float(eleve['absence'])) if isinstance(eleve['absence'], (int, float, str)) and str(eleve['absence']).replace('.', '', 1).isdigit() else 0
                    elif 'Absence' in eleve:
                        absence = int(float(eleve['Absence'])) if isinstance(eleve['Absence'], (int, float, str)) and str(eleve['Absence']).replace('.', '', 1).isdigit() else 0
                    
                    conseil_discipline = eleve.get('conseil_discipline', eleve.get('C.D.', ''))
                    appreciation = eleve.get('appreciation', eleve.get('Appréciation', ''))
                    observation = eleve.get('observation_conseil', eleve.get('Observation conseil', ''))
                    
                    cursor.execute(f"""
                        INSERT INTO {table_moyennes} (ien, moyenne, rang, retard, absence, conseil_discipline, 
                                                    appreciation, observation, annee_scolaire)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ien,
                        moyenne,
                        rang,
                        retard,
                        absence,
                        conseil_discipline,
                        appreciation,
                        observation,
                        annee_scolaire
                    ))
                except Exception as e:
                    print(f"Erreur lors de l'insertion des moyennes pour l'élève {ien}: {str(e)}")
            
            # Pour chaque élève dans le détail, insérer les notes par discipline
            for _, eleve in df_detail.iterrows():
                # Récupérer l'IEN
                ien = eleve.get('IEN')
                if not ien:
                    continue  # Ignorer les lignes sans IEN
                
                # Pour chaque matière, récupérer ou créer la discipline
                for col in df_detail.columns:
                    if col not in ['IEN', 'Prénom', 'Nom', 'prenom', 'nom', 'sexe', 'Sexe', 'niveau', 'classe', 'semestre']:
                        cursor.execute("SELECT id FROM Disciplines WHERE libelle = ?", (col,))
                        result = cursor.fetchone()
                        
                        if result:
                            discipline_id = result[0]
                        else:
                            cursor.execute("INSERT INTO Disciplines (libelle) VALUES (?)", (col,))
                            discipline_id = cursor.lastrowid
                        
                        # Insérer la note si elle existe et est un nombre
                        try:
                            if col in eleve and not pd.isna(eleve[col]):
                                # Vérifier si la valeur est un nombre
                                if isinstance(eleve[col], (int, float)) or (isinstance(eleve[col], str) and str(eleve[col]).replace('.', '', 1).isdigit()):
                                    moy_d = float(eleve[col])
                                    cursor.execute(f"""
                                        INSERT INTO {table_notes} (ien, id_discipline, moy_d, annee_scolaire)
                                        VALUES (?, ?, ?, ?)
                                    """, (ien, discipline_id, moy_d, annee_scolaire))
                        except Exception as e:
                            print(f"Erreur lors de l'insertion de la note {col} pour l'élève {ien}: {str(e)}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la sauvegarde dans la base SQLite : {str(e)}")
        
        finally:
            conn.close()
            
    except Exception as e:
        raise Exception(f"Erreur lors du traitement : {str(e)}")

def to_excel(df1, df2):
    """
    Convertit deux DataFrames en un fichier Excel en mémoire
    
    Args:
        df1: Premier DataFrame (moyennes générales)
        df2: Deuxième DataFrame (données détaillées)
        
    Returns:
        bytes: Contenu du fichier Excel
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, index=False, sheet_name='Moyennes eleves')
        df2.to_excel(writer, index=False, sheet_name='Données détaillées')
    return output.getvalue()

def forcer_structure_moyennes_eleves(df):
    colonnes = [
        'Niveau', 'Classe', 'Semestre', 'IEN', 'Prenom', 'Nom', 'Sexe',
        'Date naissance', 'Lieu naissance', 'Retard', 'Absence', 'C. D.',
        'Moy', 'Rang', 'Décision conseil', 'Appréciation', 'Observation conseil'
    ]
    for col in colonnes:
        if col not in df.columns:
            df[col] = ''
    return df[colonnes]

def forcer_structure_donnees_detaillees(df, disciplines=None):
    base_cols = ['Niveau', 'Classe', 'Semestre', 'IEN', 'Prenom', 'Nom', 'Sexe']
    if disciplines is None:
        disciplines = [col for col in df.columns if col not in base_cols]
    for col in base_cols:
        if col not in df.columns:
            df[col] = ''
    # Ajouter les disciplines manquantes si besoin
    for col in disciplines:
        if col not in df.columns:
            df[col] = ''
    return df[base_cols + disciplines]

def synchroniser_suppression_eleve(ien, niveau, classe, semestre):
    """
    Supprime un élève de la base ET du fichier centralisé (toutes les feuilles)
    """
    import sqlite3
    from ..config import DB_PATH
    # Suppression dans la base
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Eleves WHERE ien = ?", (ien,))
    cursor.execute("DELETE FROM Moyennes_Generales_S1 WHERE ien = ?", (ien,))
    cursor.execute("DELETE FROM Moyennes_Generales_S2 WHERE ien = ?", (ien,))
    cursor.execute("DELETE FROM Notes_S1 WHERE ien = ?", (ien,))
    cursor.execute("DELETE FROM Notes_S2 WHERE ien = ?", (ien,))
    cursor.execute("DELETE FROM Decisions_Finales WHERE ien = ?", (ien,))
    conn.commit()
    conn.close()
    # Suppression dans le fichier centralisé
    if os.path.exists(FICHIER_CENTRAL):
        xls = pd.ExcelFile(FICHIER_CENTRAL)
        df_moy = pd.read_excel(xls, sheet_name="Moyennes eleves")
        df_det = pd.read_excel(xls, sheet_name="Données détaillées")
        # Filtrer
        cond_moy = ~((df_moy['IEN'] == ien) & (df_moy['Niveau'] == niveau) & (df_moy['Classe'] == classe) & (df_moy['Semestre'] == semestre))
        cond_det = ~((df_det['IEN'] == ien) & (df_det['Niveau'] == niveau) & (df_det['Classe'] == classe) & (df_det['Semestre'] == semestre))
        df_moy = df_moy[cond_moy]
        df_det = df_det[cond_det]
        # Réécrire le fichier central
        with pd.ExcelWriter(FICHIER_CENTRAL, engine='xlsxwriter') as writer:
            df_moy.to_excel(writer, sheet_name="Moyennes eleves", index=False)
            df_det.to_excel(writer, sheet_name="Données détaillées", index=False)

def synchroniser_suppression_classe(niveau, classe, semestre):
    """
    Supprime une classe (tous les élèves de cette classe) dans la base ET le fichier centralisé
    """
    import sqlite3
    from ..config import DB_PATH
    # Suppression dans la base
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Trouver tous les IEN des élèves de la classe
    cursor.execute("""
        SELECT ien FROM Eleves e
        JOIN Classes c ON e.id_classe = c.id
        JOIN Niveaux n ON c.id_niveau = n.id
        WHERE n.libelle = ? AND c.libelle = ?
    """, (niveau, classe))
    iens = [row[0] for row in cursor.fetchall()]
    for ien in iens:
        cursor.execute("DELETE FROM Eleves WHERE ien = ?", (ien,))
        cursor.execute("DELETE FROM Moyennes_Generales_S1 WHERE ien = ?", (ien,))
        cursor.execute("DELETE FROM Moyennes_Generales_S2 WHERE ien = ?", (ien,))
        cursor.execute("DELETE FROM Notes_S1 WHERE ien = ?", (ien,))
        cursor.execute("DELETE FROM Notes_S2 WHERE ien = ?", (ien,))
        cursor.execute("DELETE FROM Decisions_Finales WHERE ien = ?", (ien,))
    # Supprimer la classe elle-même
    cursor.execute("""
        DELETE FROM Classes WHERE id IN (
            SELECT c.id FROM Classes c
            JOIN Niveaux n ON c.id_niveau = n.id
            WHERE n.libelle = ? AND c.libelle = ?
        )
    """, (niveau, classe))
    conn.commit()
    conn.close()
    # Suppression dans le fichier centralisé
    if os.path.exists(FICHIER_CENTRAL):
        xls = pd.ExcelFile(FICHIER_CENTRAL)
        df_moy = pd.read_excel(xls, sheet_name="Moyennes eleves")
        df_det = pd.read_excel(xls, sheet_name="Données détaillées")
        cond_moy = ~((df_moy['Niveau'] == niveau) & (df_moy['Classe'] == classe) & (df_moy['Semestre'] == semestre))
        cond_det = ~((df_det['Niveau'] == niveau) & (df_det['Classe'] == classe) & (df_det['Semestre'] == semestre))
        df_moy = df_moy[cond_moy]
        df_det = df_det[cond_det]
        with pd.ExcelWriter(FICHIER_CENTRAL, engine='xlsxwriter') as writer:
            df_moy.to_excel(writer, sheet_name="Moyennes eleves", index=False)
            df_det.to_excel(writer, sheet_name="Données détaillées", index=False)

def synchroniser_suppression_niveau(niveau, semestre):
    """
    Supprime un niveau (toutes les classes et élèves de ce niveau) dans la base ET le fichier centralisé
    """
    import sqlite3
    from ..config import DB_PATH
    # Suppression dans la base
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Trouver toutes les classes du niveau
    cursor.execute("SELECT libelle FROM Classes c JOIN Niveaux n ON c.id_niveau = n.id WHERE n.libelle = ?", (niveau,))
    classes = [row[0] for row in cursor.fetchall()]
    for classe in classes:
        # Supprimer tous les élèves et la classe (réutilise la fonction classe)
        synchroniser_suppression_classe(niveau, classe, semestre)
    # Supprimer le niveau lui-même
    cursor.execute("DELETE FROM Niveaux WHERE libelle = ?", (niveau,))
    conn.commit()
    conn.close()
    # Suppression dans le fichier centralisé (toutes les lignes du niveau)
    if os.path.exists(FICHIER_CENTRAL):
        xls = pd.ExcelFile(FICHIER_CENTRAL)
        df_moy = pd.read_excel(xls, sheet_name="Moyennes eleves")
        df_det = pd.read_excel(xls, sheet_name="Données détaillées")
        cond_moy = ~( (df_moy['Niveau'] == niveau) & (df_moy['Semestre'] == semestre) )
        cond_det = ~( (df_det['Niveau'] == niveau) & (df_det['Semestre'] == semestre) )
        df_moy = df_moy[cond_moy]
        df_det = df_det[cond_det]
        with pd.ExcelWriter(FICHIER_CENTRAL, engine='xlsxwriter') as writer:
            df_moy.to_excel(writer, sheet_name="Moyennes eleves", index=False)
            df_det.to_excel(writer, sheet_name="Données détaillées", index=False)

def synchroniser_suppression_import(df_moyennes, niveau, classe, semestre):
    """
    Supprime dans la base et le fichier centralisé toutes les lignes correspondant aux IEN du DataFrame importé
    """
    from .excel_utils import synchroniser_suppression_eleve
    # Pour chaque IEN du DataFrame
    for ien in df_moyennes.get('IEN', []):
        if pd.notna(ien) and ien != '':
            synchroniser_suppression_eleve(ien, niveau, classe, semestre)