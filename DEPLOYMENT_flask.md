# 🚀 Guide de Déploiement - Questionnaire EORTC QLQ-C30 Flask

Guide complet pour déployer l'application Flask sur différentes plateformes.

## 📋 Prérequis

### **Avant le déploiement**
- ✅ Code source complet
- ✅ Clé API Google Cloud (optionnel)
- ✅ Compte sur la plateforme choisie
- ✅ Repository Git (recommandé)

### **Variables d'environnement requises**
```bash
# Obligatoires
SECRET_KEY="votre_cle_secrete_production"
FLASK_DEBUG=False

# Optionnelles
GOOGLE_CLOUD_API_KEY="votre_cle_api_google"
AUDIO_ENABLED=True
USE_GEMINI_TTS=True
USE_PRO_MODEL=True
```

## 🌐 PythonAnywhere (Recommandé)

### **1. Créer un compte**
1. Aller sur [PythonAnywhere](https://www.pythonanywhere.com)
2. Créer un compte gratuit
3. Vérifier l'email

### **2. Configuration du projet**
```bash
# Se connecter via SSH
ssh username@ssh.pythonanywhere.com

# Cloner le repository
git clone https://github.com/votre-username/questionnaire-flask.git
cd questionnaire-flask

# Installer les dépendances
pip3.10 install --user -r requirements_flask.txt
```

### **3. Configuration des variables**
```bash
# Créer le fichier .env
echo "SECRET_KEY=votre_cle_secrete" > .env
echo "GOOGLE_CLOUD_API_KEY=votre_cle_api" >> .env
echo "FLASK_DEBUG=False" >> .env
```

### **4. Configuration du serveur web**
1. Aller dans **Web** → **Add a new web app**
2. Choisir **Flask**
3. Python version : **3.10**
4. Source code : `/home/username/questionnaire-flask`
5. Working directory : `/home/username/questionnaire-flask`

### **5. Configuration WSGI**
```python
# Fichier : /var/www/username_pythonanywhere_com_wsgi.py
import sys
path = '/home/username/questionnaire-flask'
if path not in sys.path:
    sys.path.append(path)

from app_flask import app as application
```

### **6. Configuration du domaine**
1. Aller dans **Web** → **Domains**
2. Ajouter votre domaine personnalisé
3. Configurer le certificat SSL

### **7. Démarrage**
```bash
# Redémarrer le serveur web
# L'application sera accessible sur votre domaine
```

## 🚀 Render

### **1. Préparation du repository**
```bash
# Créer un fichier render.yaml
cat > render.yaml << EOF
services:
  - type: web
    name: questionnaire-eortc
    env: python
    buildCommand: pip install -r requirements_flask.txt
    startCommand: python app_flask.py
    envVars:
      - key: SECRET_KEY
        value: votre_cle_secrete
      - key: GOOGLE_CLOUD_API_KEY
        value: votre_cle_api
      - key: FLASK_DEBUG
        value: False
EOF
```

### **2. Déploiement**
1. Aller sur [Render](https://render.com)
2. Se connecter avec GitHub
3. Sélectionner le repository
4. Configurer les variables d'environnement
5. Déployer

### **3. Configuration automatique**
- **Build Command** : `pip install -r requirements_flask.txt`
- **Start Command** : `python app_flask.py`
- **Python Version** : 3.10

## 🚄 Railway

### **1. Configuration Railway**
```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Initialiser le projet
railway init
```

### **2. Configuration des variables**
```bash
# Définir les variables d'environnement
railway variables set SECRET_KEY="votre_cle_secrete"
railway variables set GOOGLE_CLOUD_API_KEY="votre_cle_api"
railway variables set FLASK_DEBUG="False"
```

### **3. Déploiement**
```bash
# Déployer
railway up

# Vérifier les logs
railway logs
```

## 🐳 Docker (Optionnel)

### **1. Créer Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements_flask.txt .
RUN pip install --no-cache-dir -r requirements_flask.txt

COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p data static/audio_cache

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app_flask.py"]
```

### **2. Créer docker-compose.yml**
```yaml
# docker-compose.yml
version: '3.8'

services:
  questionnaire:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=votre_cle_secrete
      - GOOGLE_CLOUD_API_KEY=votre_cle_api
      - FLASK_DEBUG=False
    volumes:
      - ./data:/app/data
      - ./static/audio_cache:/app/static/audio_cache
```

### **3. Déploiement Docker**
```bash
# Construire l'image
docker build -t questionnaire-flask .

# Lancer le conteneur
docker run -p 5000:5000 \
  -e SECRET_KEY="votre_cle_secrete" \
  -e GOOGLE_CLOUD_API_KEY="votre_cle_api" \
  questionnaire-flask
```

## 🔧 Configuration Production

### **1. Variables d'environnement**
```bash
# Sécurité
SECRET_KEY="cle_secrete_longue_et_complexe"
FLASK_DEBUG=False

# Base de données
DATABASE_URL="sqlite:///data/responses.db"

# Audio
GOOGLE_CLOUD_API_KEY="votre_cle_api_google"
AUDIO_ENABLED=True
USE_GEMINI_TTS=True
USE_PRO_MODEL=True

# Serveur
HOST=0.0.0.0
PORT=5000
```

### **2. Configuration HTTPS**
```bash
# Certificat SSL (Let's Encrypt)
sudo apt-get install certbot
sudo certbot --nginx -d votre-domaine.com
```

### **3. Configuration Nginx (Optionnel)**
```nginx
# /etc/nginx/sites-available/questionnaire
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring et Logs

### **1. Logs d'application**
```bash
# Voir les logs en temps réel
tail -f logs/app.log

# Logs d'erreur
tail -f logs/error.log
```

### **2. Monitoring des performances**
```python
# Ajouter dans app_flask.py
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### **3. Métriques importantes**
- **Temps de réponse** : < 200ms
- **Utilisation CPU** : < 50%
- **Utilisation mémoire** : < 100MB
- **Taux d'erreur** : < 1%

## 🔒 Sécurité Production

### **1. Configuration sécurisée**
```python
# config_flask.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Sécurité renforcée
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Limitation de taux
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"
```

### **2. Validation des entrées**
```python
# Validation stricte des données
def validate_session_data(data):
    required_fields = ['initials', 'birth_date', 'today_date']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f'Champ requis manquant: {field}')
    
    # Validation des dates
    try:
        datetime.datetime.strptime(data['birth_date'], '%Y-%m-%d')
        datetime.datetime.strptime(data['today_date'], '%Y-%m-%d')
    except ValueError:
        raise ValueError('Format de date invalide')
```

### **3. Protection CSRF**
```python
# Ajouter dans app_flask.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

## 🧪 Tests de Déploiement

### **1. Tests fonctionnels**
```bash
# Test de l'API
curl -X POST http://localhost:5000/api/start_session \
  -H "Content-Type: application/json" \
  -d '{"initials":"A B","birth_date":"1970-01-01","today_date":"2024-01-01"}'

# Test de l'audio
curl http://localhost:5000/api/get_audio/1

# Test de la base de données
python -c "from models.database_flask import DatabaseManager; print('DB OK')"
```

### **2. Tests de performance**
```bash
# Test de charge (optionnel)
pip install locust
locust -f tests/locustfile.py --host=http://localhost:5000
```

### **3. Tests de sécurité**
```bash
# Vérification des permissions
ls -la data/
ls -la static/audio_cache/

# Vérification des variables d'environnement
echo $SECRET_KEY
echo $GOOGLE_CLOUD_API_KEY
```

## 🚨 Dépannage Déploiement

### **Problèmes courants**

#### **Erreur 500 - Internal Server Error**
```bash
# Vérifier les logs
tail -f logs/app.log

# Vérifier les permissions
chmod 755 data/
chmod 755 static/audio_cache/

# Vérifier les variables d'environnement
env | grep FLASK
```

#### **Audio ne fonctionne pas**
```bash
# Vérifier la clé API
echo $GOOGLE_CLOUD_API_KEY

# Tester l'API Google
curl -H "Authorization: Bearer $GOOGLE_CLOUD_API_KEY" \
  https://texttospeech.googleapis.com/v1/voices
```

#### **Base de données corrompue**
```bash
# Sauvegarder
cp data/responses.db data/responses.db.backup

# Recréer
rm data/responses.db
python -c "from models.database_flask import DatabaseManager; DatabaseManager()"
```

#### **Problèmes de mémoire**
```bash
# Vérifier l'utilisation
free -h
ps aux | grep python

# Nettoyer le cache
rm -rf static/audio_cache/*
```

## 📈 Optimisations Production

### **1. Cache audio**
```python
# Pré-générer tous les audios
python -c "
from audio_handler_gcp_tts import AudioHandler
from questionnaire_logic import EORTCQuestionnaire

audio_handler = AudioHandler()
questionnaire = EORTCQuestionnaire()

texts = []
for i in range(1, 31):
    texts.append(questionnaire.get_speech_text(i))

audio_handler.pregenerate_audio(texts)
"
```

### **2. Optimisation base de données**
```sql
-- Ajouter des index
CREATE INDEX idx_responses_session_question ON responses(session_id, question_num);
CREATE INDEX idx_sessions_created ON sessions(created_at);
```

### **3. Compression des assets**
```bash
# Minifier CSS/JS
pip install cssmin jsmin
python -c "
import cssmin, jsmin
# Minifier les fichiers
"
```

## 🎯 Checklist Déploiement

### **Avant le déploiement**
- [ ] Code testé localement
- [ ] Variables d'environnement configurées
- [ ] Clé API Google Cloud (si audio activé)
- [ ] Base de données initialisée
- [ ] Cache audio pré-généré
- [ ] Tests fonctionnels passés

### **Après le déploiement**
- [ ] Application accessible
- [ ] Audio fonctionne
- [ ] Reconnaissance vocale fonctionne
- [ ] Base de données accessible
- [ ] Export fonctionne
- [ ] HTTPS configuré
- [ ] Logs configurés
- [ ] Monitoring activé

### **Tests finaux**
- [ ] Test complet du questionnaire
- [ ] Test sur différents navigateurs
- [ ] Test sur mobile
- [ ] Test de performance
- [ ] Test de sécurité

---

**🎉 Votre application est maintenant déployée et prête à être utilisée !**
