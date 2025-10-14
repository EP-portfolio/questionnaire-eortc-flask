"""
Application Flask principale - Version optimisée
"""

import os
from flask import Flask
from flask_cors import CORS

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
    print("INFO: Initialisation de la base de donnees...")
    try:
        # Tester la connexion
        test_session = app.db.get_session("test")
        print("INFO: Base de donnees initialisee avec succes")
    except Exception as e:
        print(f"WARNING: Erreur initialisation base: {e}")
    
    # Configuration audio (mode préenregistré par défaut)
    api_key = os.environ.get('GOOGLE_CLOUD_API_KEY')
    if api_key and api_key.strip():
        app.audio_handler = AudioHandler(
            api_key=api_key,
            use_gemini_tts=app.config.get('USE_GEMINI_TTS', False),
            use_pro_model=app.config.get('USE_PRO_MODEL', False)
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
    
    # Configuration du port
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"INFO: Démarrage sur le port {port}")
    print(f"INFO: Mode debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()