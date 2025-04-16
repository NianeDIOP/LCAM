import sqlite3
import os
from pathlib import Path

# Chemin vers la base de données
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.path.join(BASE_DIR, "src", "data", "lcams.db")

def inspect_and_fix_database():
    """Inspecte et corrige la structure de la base de données"""
    
    # Vérifier si la base de données existe
    if not os.path.exists(DB_PATH):
        print(f"La base de données n'existe pas à l'emplacement: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Afficher la structure des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Tables trouvées: {[table[0] for table in tables]}")
    
    # Vérifier la structure de la table Eleves
    cursor.execute("PRAGMA table_info(Eleves);")
    eleves_columns = cursor.fetchall()
    
    print("\nStructure de la table Eleves:")
    for col in eleves_columns:
        print(f"  {col[1]} ({col[2]}), NULL: {'Oui' if col[3] == 0 else 'Non'}, Default: {col[4]}")
    
    # Modifier la table Eleves pour permettre des valeurs NULL sur les champs problématiques
    try:
        # Créer une table temporaire
        cursor.execute("""
        CREATE TABLE Eleves_temp (
            ien TEXT PRIMARY KEY,
            prenom TEXT,
            nom TEXT,
            sexe TEXT,
            date_naissance TEXT,
            lieu_naissance TEXT,
            id_classe INTEGER,
            annee_scolaire TEXT,
            FOREIGN KEY (id_classe) REFERENCES Classes(id)
        );
        """)
        
        # Copier les données de l'ancienne table
        cursor.execute("INSERT INTO Eleves_temp SELECT * FROM Eleves;")
        
        # Supprimer l'ancienne table
        cursor.execute("DROP TABLE Eleves;")
        
        # Renommer la table temporaire
        cursor.execute("ALTER TABLE Eleves_temp RENAME TO Eleves;")
        
        conn.commit()
        print("\nLa table Eleves a été recréée avec des contraintes plus souples.")
    except Exception as e:
        conn.rollback()
        print(f"\nErreur lors de la modification de la table: {str(e)}")
    
    # Si la base est vide, recréer les tables
    cursor.execute("SELECT COUNT(*) FROM Eleves")
    eleves_count = cursor.fetchone()[0]
    
    print(f"\nNombre d'élèves dans la base: {eleves_count}")
    
    conn.close()

if __name__ == "__main__":
    inspect_and_fix_database()