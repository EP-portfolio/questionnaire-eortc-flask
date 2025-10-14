"""
Application Flask pour le questionnaire EORTC QLQ-C30
Version avec reconnaissance vocale continue - 1 SEUL CLIC pour 30 questions
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import uuid
import datetime
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules existants
sys.path.append(str(Path(__file__).parent.parent))

# Importer les modules existants
from questionnaire_logic import EORTCQuestionnaire
from audio_handler_simple_flask import AudioHandlerSimple as AudioHandler, VoiceRecognitionHandler

# Importer les routes
from routes.main_flask import main_bp
from routes.api_flask import api_bp

# Importer la configuration
from config_flask import Config

# Importer la base de données
from models.database_flask import DatabaseManager

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # CORS pour les requêtes AJAX
    CORS(app)
    
    # Initialiser les gestionnaires
    app.questionnaire = EORTCQuestionnaire()
    app.db = DatabaseManager()
    
    # Forcer l'initialisation de la base de données
    print("Initialisation de la base de donnees...")
    try:
        # Tester la connexion
        test_session = app.db.get_session("test")
        print("Base de donnees initialisee avec succes")
    except Exception as e:
        print(f"ERREUR initialisation base: {e}")
    
    # Configuration audio (sans API pour audios préenregistrés)
    api_key = os.environ.get('GOOGLE_CLOUD_API_KEY')
    if api_key and api_key.strip():
        app.audio_handler = AudioHandler(
            api_key=api_key,
            use_gemini_tts=True,
            use_pro_model=True
        )
        print("INFO: Audio handler configuré avec API TTS")
    else:
        app.audio_handler = None
        print("INFO: Mode audios préenregistrés uniquement (pas d'API TTS)")
    
    app.voice_handler = VoiceRecognitionHandler()
    
    # Enregistrer les blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Créer les dossiers nécessaires
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/audio_cache', exist_ok=True)
    
    return app

def main():
    """Point d'entrée principal"""
    app = create_app()
    
    # Mode debug en développement
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🏥 Questionnaire EORTC QLQ-C30 - Version Flask")
    print("🎤 Reconnaissance vocale continue (1 clic pour 30 questions)")
    print("🌐 Interface optimisée pour personnes âgées")
    
    if debug_mode:
        print("🔧 Mode debug activé")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode
    )

if __name__ == '__main__':
    main()
