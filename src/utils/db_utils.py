import sqlite3
import os
import pandas as pd
from ..config import DB_PATH, DATA_DIR

def init_database():
    """Initialise la base de données si elle n'existe pas"""
    # Créer le dossier data s'il n'existe pas
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Vérifier si la base existe déjà
    if os.path.exists(DB_PATH):
        return
    
    # Créer une nouvelle base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer les tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Configuration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_etablissement TEXT,
        adresse TEXT,
        telephone TEXT,
        inspection_academique TEXT,
        inspection_education TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Annee_Scolaire (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL,
        etat TEXT DEFAULT 'inactif',
        date_debut TEXT,
        date_fin TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Niveaux (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL,
        etat TEXT DEFAULT 'actif'
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_niveau INTEGER,
        libelle TEXT NOT NULL,
        effectif INTEGER DEFAULT 0,
        etat TEXT DEFAULT 'actif',
        FOREIGN KEY (id_niveau) REFERENCES Niveaux(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Eleves (
        ien TEXT PRIMARY KEY,
        prenom TEXT NOT NULL,
        nom TEXT NOT NULL,
        sexe TEXT,
        date_naissance TEXT,
        lieu_naissance TEXT,
        id_classe INTEGER,
        annee_scolaire TEXT,
        FOREIGN KEY (id_classe) REFERENCES Classes(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Disciplines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL,
        coefficient REAL DEFAULT 1,
        type TEXT DEFAULT 'principale',
        id_discipline_parent INTEGER,
        FOREIGN KEY (id_discipline_parent) REFERENCES Disciplines(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Notes_S1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ien TEXT,
        id_discipline INTEGER,
        moy_dd REAL,
        comp_d REAL,
        moy_d REAL,
        rang_d INTEGER,
        annee_scolaire TEXT,
        FOREIGN KEY (ien) REFERENCES Eleves(ien),
        FOREIGN KEY (id_discipline) REFERENCES Disciplines(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Notes_S2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ien TEXT,
        id_discipline INTEGER,
        moy_dd REAL,
        comp_d REAL,
        moy_d REAL,
        rang_d INTEGER,
        annee_scolaire TEXT,
        FOREIGN KEY (ien) REFERENCES Eleves(ien),
        FOREIGN KEY (id_discipline) REFERENCES Disciplines(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Moyennes_Generales_S1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ien TEXT,
        moyenne REAL,
        rang INTEGER,
        retard INTEGER,
        absence INTEGER,
        conseil_discipline TEXT,
        appreciation TEXT,
        observation TEXT,
        annee_scolaire TEXT,
        FOREIGN KEY (ien) REFERENCES Eleves(ien)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Moyennes_Generales_S2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ien TEXT,
        moyenne REAL,
        rang INTEGER,
        retard INTEGER,
        absence INTEGER,
        conseil_discipline TEXT,
        appreciation TEXT,
        observation TEXT,
        annee_scolaire TEXT,
        FOREIGN KEY (ien) REFERENCES Eleves(ien)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Decisions_Finales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ien TEXT,
        decision TEXT,
        moyenne_annuelle REAL,
        rang_annuel INTEGER,
        annee_scolaire TEXT,
        FOREIGN KEY (ien) REFERENCES Eleves(ien)
    )
    ''')
    
    # Insérer les niveaux par défaut
    niveaux = ["6ème", "5ème", "4ème", "3ème", "Seconde", "Première", "Terminale"]
    for niveau in niveaux:
        cursor.execute("INSERT INTO Niveaux (libelle) VALUES (?)", (niveau,))
    
    # Insérer année scolaire actuelle par défaut
    cursor.execute("INSERT INTO Annee_Scolaire (libelle, etat) VALUES (?, ?)", 
                  ("2023-2024", "actif"))
    
    # Valider les changements
    conn.commit()
    conn.close()

def get_db_connection():
    """Établit et retourne une connexion à la base de données"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    return conn

def execute_query(query, params=(), fetchall=False):
    """Exécute une requête SQL et retourne le résultat"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    result = None
    if fetchall:
        result = cursor.fetchall()
    else:
        conn.commit()
    
    conn.close()
    return result

def insert_data(table, data_dict):
    """Insère des données dans une table spécifiée"""
    placeholders = ', '.join(['?'] * len(data_dict))
    columns = ', '.join(data_dict.keys())
    values = tuple(data_dict.values())
    
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return last_id

def update_data(table, data_dict, condition):
    """Met à jour des données dans une table spécifiée selon une condition"""
    set_clause = ', '.join([f"{k} = ?" for k in data_dict.keys()])
    values = tuple(data_dict.values())
    
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected