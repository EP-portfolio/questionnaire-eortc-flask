#!/usr/bin/env python3
"""
Script de debug pour tester les sessions
"""

import sqlite3
import os
from pathlib import Path

def debug_sessions():
    """Debug des sessions en base"""
    db_path = Path('data/responses.db')
    
    if not db_path.exists():
        print("ERREUR: Base de donnees introuvable:", db_path)
        return
    
    print("DEBUG: Sessions en base de donnees...")
    print(f"Chemin DB: {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Lister toutes les sessions
            cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10')
            sessions = cursor.fetchall()
            
            print(f"\nSessions trouvees: {len(sessions)}")
            
            for session in sessions:
                print(f"\nSession: {session['id']}")
                print(f"   Initiales: {session['initials']}")
                print(f"   Creee: {session['created_at']}")
                print(f"   Mode: {session.get('mode', 'N/A')}")
                print(f"   Audio: {session.get('audio_enabled', 'N/A')}")
                
                # Compter les reponses
                cursor.execute('SELECT COUNT(*) FROM responses WHERE session_id = ?', (session['id'],))
                response_count = cursor.fetchone()[0]
                print(f"   Reponses: {response_count}")
            
            # Verifier la structure de la table
            cursor.execute("PRAGMA table_info(sessions)")
            columns = cursor.fetchall()
            print(f"\nStructure table sessions:")
            for col in columns:
                print(f"   {col['name']}: {col['type']}")
                
    except Exception as e:
        print(f"ERREUR debug: {e}")

if __name__ == "__main__":
    debug_sessions()
