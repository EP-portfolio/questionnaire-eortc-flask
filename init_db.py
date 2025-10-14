#!/usr/bin/env python3
"""
Script pour initialiser la base de données
"""

from models.database_flask import DatabaseManager

def init_database():
    """Initialiser la base de données"""
    print("Initialisation de la base de donnees...")
    
    try:
        db = DatabaseManager()
        print("Base de donnees initialisee avec succes!")
        
        # Tester la creation d'une session
        session_id = db.create_session({
            'initials': 'TEST',
            'birth_date': '01/01/1990',
            'today_date': '14/10/2025',
            'mode': 'Test',
            'audio_enabled': True
        })
        
        print(f"Session de test creee: {session_id}")
        
        # Verifier que la session existe
        session = db.get_session(session_id)
        if session:
            print("Session de test validee!")
        else:
            print("ERREUR: Session de test non trouvee!")
            
    except Exception as e:
        print(f"ERREUR: {e}")

if __name__ == "__main__":
    init_database()
