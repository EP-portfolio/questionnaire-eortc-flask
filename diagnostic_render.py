#!/usr/bin/env python3
"""
Script de diagnostic pour Render
"""

import os
import sys
from pathlib import Path

def diagnostic_render():
    """Diagnostic complet de l'environnement Render"""
    print("=== DIAGNOSTIC RENDER ===")
    
    # 1. Variables d'environnement
    print("\n1. Variables d'environnement:")
    env_vars = [
        'SECRET_KEY',
        'GOOGLE_CLOUD_API_KEY', 
        'FLASK_DEBUG',
        'AUDIO_ENABLED',
        'USE_GEMINI_TTS',
        'USE_PRO_MODEL'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NON DÉFINIE')
        if var == 'GOOGLE_CLOUD_API_KEY' and value != 'NON DÉFINIE':
            value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
        print(f"  {var}: {value}")
    
    # 2. Structure des dossiers
    print("\n2. Structure des dossiers:")
    folders = ['data', 'static', 'static/audio_cache', 'templates', 'models', 'routes']
    for folder in folders:
        path = Path(folder)
        exists = path.exists()
        print(f"  {folder}: {'✅' if exists else '❌'}")
        if exists:
            files = list(path.glob('*'))
            print(f"    Fichiers: {len(files)}")
    
    # 3. Base de données
    print("\n3. Base de données:")
    db_path = Path('data/responses.db')
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"  Fichier DB: ✅ ({size} bytes)")
        
        # Tester la connexion
        try:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sessions")
                sessions_count = cursor.fetchone()[0]
                print(f"  Sessions: {sessions_count}")
        except Exception as e:
            print(f"  Erreur DB: {e}")
    else:
        print("  Fichier DB: ❌")
    
    # 4. Configuration Flask
    print("\n4. Configuration Flask:")
    try:
        from config_flask import Config
        config = Config()
        print(f"  SECRET_KEY: {'✅' if config.SECRET_KEY else '❌'}")
        print(f"  GOOGLE_CLOUD_API_KEY: {'✅' if config.GOOGLE_CLOUD_API_KEY else '❌'}")
        print(f"  DEBUG: {config.DEBUG}")
        print(f"  AUDIO_ENABLED: {config.AUDIO_ENABLED}")
    except Exception as e:
        print(f"  Erreur config: {e}")
    
    # 5. Dépendances Python
    print("\n5. Dépendances Python:")
    required_packages = [
        'flask', 'flask_cors', 'pandas', 'requests', 
        'google_cloud_texttospeech', 'openpyxl'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}: ✅")
        except ImportError:
            print(f"  {package}: ❌")
    
    print("\n=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    diagnostic_render()
