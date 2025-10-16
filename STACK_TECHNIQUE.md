# 🏗️ Stack Technique - Questionnaire EORTC QLQ-C30

## 📋 Vue d'Ensemble

Cette application Flask utilise une stack technique moderne et optimisée pour la reconnaissance vocale continue et l'accessibilité web. Voici l'analyse complète des technologies nécessaires.

---

## 🐍 **Backend - Python & Flask**

### **Core Framework**
```python
Flask==3.0.0                    # Framework web principal
flask-cors==4.0.0               # Gestion CORS pour API
gunicorn==21.2.0                # Serveur WSGI production
```

### **Base de Données**
```python
# SQLite intégré à Python (pas de dépendance externe)
# Gestionnaire personnalisé : models/database_flask.py
```

### **HTTP & API**
```python
requests==2.31.0                 # Requêtes HTTP vers Google Cloud
python-dotenv==1.0.0            # Variables d'environnement
```

### **Modules Python Standard**
```python
import os                       # Gestion fichiers et variables d'env
import sqlite3                  # Base de données SQLite
import uuid                     # Génération d'identifiants uniques
import datetime                 # Gestion des dates
import hashlib                  # Hachage MD5 pour cache audio
import threading                # Threading pour TTS asynchrone
import tempfile                 # Fichiers temporaires
import wave                     # Manipulation fichiers audio WAV
import struct                   # Manipulation binaire
import re                       # Expressions régulières
import base64                   # Encodage base64 pour API
import json                      # Sérialisation JSON
```

---

## 🌐 **Frontend - Web Technologies**

### **HTML5 & CSS3**
```html
<!-- Templates Jinja2 -->
- base_flask.html              # Template de base
- accueil_flask.html          # Page d'accueil
- questionnaire_flask_simple.html  # Interface principale
- resultat_flask.html         # Page de résultats
```

### **JavaScript ES6+**
```javascript
// speech_recognition_flask.js - Reconnaissance vocale
- Web Speech API (Chrome/Edge)
- MediaRecorder API (Firefox/Safari)
- Fallback avec transcription serveur

// questionnaire_flask.js - Logique frontend
- Gestion du questionnaire
- Navigation entre questions
- Interface utilisateur
```

### **CSS3 Avancé**
```css
/* style_flask.css */
- Variables CSS personnalisées
- Flexbox et Grid Layout
- Animations et transitions
- Design responsive mobile-first
- Mode sombre/clair
```

---

## 🎤 **Reconnaissance Vocale**

### **Web Speech API (Chrome/Edge)**
```javascript
// Support natif navigateur
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'fr-FR';
```

### **Fallback Firefox/Safari**
```javascript
// MediaRecorder + Transcription serveur
const mediaRecorder = new MediaRecorder(stream);
// Envoi vers /api/transcribe_chunk
```

### **Google Cloud Speech-to-Text**
```python
# API REST pour transcription
url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
payload = {
    "config": {
        "encoding": "WEBM_OPUS",
        "sampleRateHertz": 48000,
        "languageCode": "fr-FR",
        "model": "latest_long"
    },
    "audio": {"content": audio_base64}
}
```

---

## 🔊 **Synthèse Vocale (TTS)**

### **Google Cloud Text-to-Speech**
```python
# API REST pour synthèse
url = "https://texttospeech.googleapis.com/v1/text:synthesize"
voice_name = "fr-FR-Neural2-A"
language_code = "fr-FR"
```

### **Gemini TTS (Alternative)**
```python
# API Gemini pour TTS
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
model = "gemini-2.5-pro-preview-tts"  # ou "gemini-2.5-flash-preview-tts"
voice_name = "Achernar"
```

### **Cache Audio MD5**
```python
# Optimisation avec hachage
audio_hash = hashlib.md5(text.encode()).hexdigest()
cache_path = f"static/audio_cache/{voice_name}/{audio_hash}.wav"
```

---

## 🗄️ **Base de Données**

### **SQLite Schema**
```sql
-- Table sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    initials TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    today_date TEXT NOT NULL,
    audio_enabled BOOLEAN DEFAULT 1,
    mode TEXT DEFAULT 'Continu (Web Speech)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'active'
);

-- Table responses
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_num INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    score INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    transcript TEXT,
    response_type TEXT DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### **Gestionnaire ORM**
```python
class DatabaseManager:
    def create_session(self, initials, birth_date, today_date, audio_enabled, mode)
    def save_response(self, session_id, question_num, question_text, score, response_text)
    def get_session(self, session_id)
    def get_session_responses(self, session_id)
    def calculate_statistics(self, session_id)
```

---

## 🌐 **API REST**

### **Endpoints Principaux**
```python
# Routes principales
GET  /                           # Page d'accueil
GET  /questionnaire              # Interface questionnaire
GET  /resultat/<session_id>      # Page de résultats
GET  /admin                      # Interface admin

# API AJAX
POST /api/start_session          # Créer session
GET  /api/validate_session       # Valider session
GET  /api/get_question/<num>     # Récupérer question
POST /api/process_voice          # Traiter reconnaissance vocale
POST /api/save_manual_response   # Sauvegarder réponse manuelle
GET  /api/get_audio/<num>        # Récupérer audio TTS
POST /api/transcribe_chunk       # Transcription serveur
GET  /api/export_session/<id>    # Export données
GET  /api/health                 # Health check
GET  /api/diagnostic             # Diagnostic complet
```

### **Format JSON**
```json
// POST /api/start_session
{
  "initials": "JD",
  "birth_date": "01/01/1990",
  "today_date": "14/10/2025",
  "audio_enabled": true,
  "mode": "Continu (Web Speech)"
}

// POST /api/process_voice
{
  "session_id": "uuid",
  "question_num": 1,
  "transcript": "beaucoup"
}
```

---

## 🚀 **Déploiement**

### **Serveur WSGI**
```python
# Procfile
web: gunicorn app_flask:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --log-level info --max-requests 1000 --max-requests-jitter 100
```

### **Configuration Render**
```yaml
# render.yaml
services:
  - type: web
    name: questionnaire-eortc-flask
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements_flask.txt
    startCommand: python app_flask.py
    envVars:
      - key: SECRET_KEY
        value: your-secret-key
      - key: GOOGLE_CLOUD_API_KEY
        sync: false
```

### **Variables d'Environnement**
```bash
# Configuration de base
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DEBUG=False

# API Keys (optionnelles)
GOOGLE_CLOUD_API_KEY=your-google-cloud-api-key
USE_GEMINI_TTS=False
USE_PRO_MODEL=False

# Configuration audio
AUDIO_ENABLED=True
SPEECH_LANGUAGE=fr-FR
```

---

## 🔧 **Outils de Développement**

### **Linting & Formatting**
```bash
# Python
flake8 .                    # Linting
black .                      # Formatting
mypy .                       # Type checking

# JavaScript
eslint static/js/           # Linting JS
prettier static/js/         # Formatting JS
```

### **Tests**
```python
# Tests unitaires
pytest tests/
pytest tests/test_questionnaire_logic.py
pytest tests/test_database.py
pytest tests/test_api.py

# Tests d'intégration
python test_integration.py
```

### **Debugging**
```python
# Mode debug Flask
export FLASK_ENV=development
export DEBUG=True

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 **Performance & Monitoring**

### **Optimisations**
```python
# Cache audio MD5
audio_cache = {}
cache_path = f"static/audio_cache/{voice_name}/{hash}.wav"

# Compression Gzip
from flask_compress import Compress
Compress(app)

# Database indexing
CREATE INDEX idx_session_id ON responses(session_id);
CREATE INDEX idx_question_num ON responses(question_num);
```

### **Métriques**
```python
# Health check
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'database': check_database(),
        'audio_cache': check_audio_cache(),
        'timestamp': datetime.now().isoformat()
    }
```

---

## 🛡️ **Sécurité**

### **Mesures Implémentées**
```python
# Clé secrète forte
SECRET_KEY = os.environ.get('SECRET_KEY', generate_strong_key())

# Protection CSRF
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# Validation des entrées
def validate_input(data):
    # Sanitisation des données utilisateur
    pass

# HTTPS obligatoire
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

### **Conformité RGPD**
```python
# Anonymisation des données
def anonymize_session(session_id):
    # Suppression des données personnelles
    # Conservation des données anonymisées
    pass
```

---

## 🌍 **Compatibilité Navigateurs**

### **Web Speech API**
```javascript
// Chrome 25+, Edge 79+, Safari 14.1+
const isSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
```

### **MediaRecorder API**
```javascript
// Firefox 25+, Chrome 47+, Safari 14+
const isSupported = 'MediaRecorder' in window;
```

### **Fallback Strategy**
```javascript
// Détection automatique du support
if (isWebSpeechSupported) {
    // Utiliser Web Speech API
} else if (isMediaRecorderSupported) {
    // Utiliser MediaRecorder + transcription serveur
} else {
    // Mode manuel uniquement
}
```

---

## 📱 **Responsive Design**

### **Breakpoints CSS**
```css
/* Mobile First */
@media (max-width: 768px) { /* Mobile */ }
@media (min-width: 769px) and (max-width: 1024px) { /* Tablet */ }
@media (min-width: 1025px) { /* Desktop */ }
```

### **Accessibilité**
```html
<!-- ARIA Labels -->
<button aria-label="Démarrer reconnaissance vocale">
<!-- Focus Management -->
<div tabindex="0" role="button">
<!-- Screen Reader Support -->
<span class="sr-only">Texte pour lecteurs d'écran</span>
```

---

## 🔄 **Architecture des Données**

### **Flux de Données**
```
Utilisateur → Interface Web → Reconnaissance Vocale → Interprétation → Base de Données
     ↓              ↓                    ↓                    ↓              ↓
   Parole      JavaScript         Web Speech API      Python Logic    SQLite
     ↓              ↓                    ↓                    ↓              ↓
   Audio      MediaRecorder       Google Cloud        Validation      Persistance
```

### **Cache Strategy**
```
Texte Question → Hash MD5 → Cache Audio → Fichier WAV → Lecture Navigateur
```

---

## 📈 **Scalabilité**

### **Limitations Actuelles**
- **SQLite** : Base de données fichier (limite ~1000 utilisateurs simultanés)
- **Cache Audio** : Stockage local (limite ~50MB)
- **API Google** : 60 minutes/mois gratuit

### **Évolutions Possibles**
- **PostgreSQL** : Base de données relationnelle
- **Redis** : Cache distribué
- **CDN** : Distribution des fichiers audio
- **Load Balancer** : Répartition de charge

---

## 🎯 **Résumé Technique**

### **Stack Complète**
```
Frontend: HTML5 + CSS3 + JavaScript ES6+ + Web Speech API
Backend: Python 3.11+ + Flask 3.0+ + SQLite
Audio: Google Cloud TTS + Gemini TTS + Cache MD5
Reconnaissance: Web Speech API + MediaRecorder + Google Cloud STT
Déploiement: Gunicorn + Render/Heroku + Docker
Sécurité: HTTPS + CSRF + Validation + RGPD
```

### **Dépendances Critiques**
1. **Python 3.11+** (Runtime)
2. **Flask 3.0+** (Framework web)
3. **Navigateur moderne** (Web Speech API)
4. **Clé API Google Cloud** (TTS/STT - optionnelle)
5. **HTTPS** (Sécurité)

### **Performance Cible**
- **Temps de réponse** : < 200ms (API)
- **Reconnaissance vocale** : < 2s (transcription)
- **Cache audio** : 100% hit rate
- **Concurrent users** : 50+ (avec optimisations)

---

<div align="center">

**Stack technique optimisée pour la reconnaissance vocale continue et l'accessibilité web** 🚀

</div>
