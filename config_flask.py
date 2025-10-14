"""
Configuration pour l'application Flask - Version optimisée
"""

import os
from pathlib import Path

class Config:
    """Configuration de base optimisée"""
    
    # Clé secrète Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Base de données SQLite
    DATABASE_PATH = os.path.join('data', 'responses.db')
    
    # Cache audio
    AUDIO_CACHE_DIR = os.path.join('static', 'audio_cache')
    
    # Configuration audio
    AUDIO_ENABLED = os.environ.get('AUDIO_ENABLED', 'True').lower() == 'true'
    
    # Clé API Google Cloud (optionnelle)
    GOOGLE_CLOUD_API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY')
    
    # Configuration TTS (désactivé par défaut)
    USE_GEMINI_TTS = os.environ.get('USE_GEMINI_TTS', 'False').lower() == 'true'
    USE_PRO_MODEL = os.environ.get('USE_PRO_MODEL', 'False').lower() == 'true'
    
    # Configuration reconnaissance vocale
    SPEECH_LANGUAGE = 'fr-FR'
    SPEECH_TIMEOUT = 10  # secondes
    
    # Configuration session
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure
    
    # Configuration upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Mode debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuration production
    @staticmethod
    def init_app(app):
        """Initialisation de l'application"""
        # Créer les dossiers nécessaires
        os.makedirs('data', exist_ok=True)
        os.makedirs('static/audio_cache', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('templates', exist_ok=True)

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    TESTING = False
    
    # Sécurité renforcée en production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Configuration de test"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = ':memory:'

# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig  # Production par défaut
}