# 🚀 Déploiement Rapide en Ligne - Questionnaire EORTC QLQ-C30

Guide pour déployer votre application Flask directement en ligne en 5 minutes !

## 🎯 Déploiement Express (Recommandé)

### **Option 1 : Render (Gratuit, Automatique) ⭐**

#### **Étape 1 : Créer un repository GitHub**
1. Allez sur [GitHub](https://github.com)
2. Cliquez sur **"New repository"**
3. Nom : `questionnaire-eortc-flask`
4. Description : `Questionnaire EORTC QLQ-C30 avec reconnaissance vocale`
5. **Public** ou **Private** selon vos préférences
6. **Ne cochez PAS** "Add README"
7. Cliquez sur **"Create repository"**

#### **Étape 2 : Uploader le code**
```bash
# Dans le dossier questionnaire_flask
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/VOTRE-USERNAME/questionnaire-eortc-flask.git
git push -u origin main
```

#### **Étape 3 : Déployer sur Render**
1. Allez sur [Render](https://render.com)
2. Créez un compte ou connectez-vous
3. Cliquez sur **"New +"** → **"Web Service"**
4. Connectez votre repository GitHub
5. Configurez :
   - **Name** : `questionnaire-eortc`
   - **Environment** : `Python`
   - **Build Command** : `pip install -r requirements_flask.txt`
   - **Start Command** : `python app_flask.py`
6. Cliquez sur **"Create Web Service"**

#### **Étape 4 : Variables d'environnement**
Dans Render, allez dans **"Environment"** et ajoutez :
- `SECRET_KEY` : `votre-cle-secrete-production`
- `FLASK_DEBUG` : `False`
- `AUDIO_ENABLED` : `True`
- `USE_GEMINI_TTS` : `True`

#### **Étape 5 : Déploiement**
- Le déploiement se lance automatiquement
- ⏱️ **Temps** : 2-3 minutes
- 🌐 **URL** : `https://questionnaire-eortc.onrender.com`

---

### **Option 2 : Railway (Simple et Rapide)**

#### **Étape 1 : Repository GitHub** (même que Render)

#### **Étape 2 : Déployer sur Railway**
1. Allez sur [Railway](https://railway.app)
2. Créez un compte ou connectez-vous
3. Cliquez sur **"New Project"**
4. Sélectionnez **"Deploy from GitHub repo"**
5. Choisissez votre repository
6. Railway détectera automatiquement Python
7. Ajoutez les variables d'environnement :
   - `SECRET_KEY` : `votre-cle-secrete-production`
   - `FLASK_DEBUG` : `False`
   - `AUDIO_ENABLED` : `True`

#### **Étape 3 : Déploiement**
- Le déploiement se lance automatiquement
- ⏱️ **Temps** : 1-2 minutes
- 🌐 **URL** : `https://votre-projet.railway.app`

---

### **Option 3 : PythonAnywhere (Spécialisé Python)**

#### **Étape 1 : Créer un compte**
1. Allez sur [PythonAnywhere](https://www.pythonanywhere.com)
2. Créez un compte gratuit
3. Vérifiez votre email

#### **Étape 2 : Uploader les fichiers**
1. Allez dans **"Files"** → **"Upload a file"**
2. Uploadez tous les fichiers du dossier `questionnaire_flask`
3. Créez le dossier `data` et `static/audio_cache`

#### **Étape 3 : Configuration Web App**
1. Allez dans **"Web"** → **"Add a new web app"**
2. Choisissez **"Flask"** et **Python 3.10**
3. Source code : `/home/votre-username/questionnaire_flask`
4. Working directory : `/home/votre-username/questionnaire_flask`

#### **Étape 4 : Configuration WSGI**
Remplacez le contenu du fichier WSGI par :
```python
import sys
path = '/home/votre-username/questionnaire_flask'
if path not in sys.path:
    sys.path.append(path)

from app_flask import app as application
```

#### **Étape 5 : Variables d'environnement**
Dans **"Web"** → **"Environment variables"** :
- `SECRET_KEY` : `votre-cle-secrete-production`
- `FLASK_DEBUG` : `False`
- `AUDIO_ENABLED` : `True`

#### **Étape 6 : Redémarrage**
- Cliquez sur **"Reload"** dans l'onglet Web
- ⏱️ **Temps** : 5-10 minutes
- 🌐 **URL** : `https://votre-username.pythonanywhere.com`

---

## 🔧 Configuration Post-Déploiement

### **Variables d'environnement importantes**
```bash
# Obligatoires
SECRET_KEY=votre-cle-secrete-production
FLASK_DEBUG=False

# Optionnelles (pour l'audio)
GOOGLE_CLOUD_API_KEY=votre-cle-api-google
AUDIO_ENABLED=True
USE_GEMINI_TTS=True
USE_PRO_MODEL=True
```

### **Test de l'application**
1. **Page d'accueil** : `/`
2. **API de santé** : `/api/health`
3. **Test complet** : Parcourir tout le questionnaire

### **Fonctionnalités testées**
- ✅ **Navigation** : Toutes les pages
- ✅ **Audio** : Lecture des questions
- ✅ **Reconnaissance vocale** : Mots-clés
- ✅ **Export** : JSON, CSV, Excel
- ✅ **Responsive** : Mobile et desktop

---

## 🚨 Dépannage Rapide

### **Problème : Application ne démarre pas**
```bash
# Vérifier les logs
# Render : Dashboard → Logs
# Railway : Deployments → Logs
# PythonAnywhere : Web → Log files
```

### **Problème : Audio ne fonctionne pas**
- Ajoutez votre clé API Google Cloud
- Variable : `GOOGLE_CLOUD_API_KEY`

### **Problème : Base de données**
- Les fichiers SQLite sont créés automatiquement
- Vérifiez les permissions du dossier `data/`

### **Problème : Reconnaissance vocale**
- Utilisez Chrome/Edge pour le mode continu
- Autorisez l'accès au microphone

---

## 📊 Monitoring

### **Métriques importantes**
- **Temps de réponse** : < 200ms
- **Disponibilité** : > 99%
- **Erreurs** : < 1%

### **Logs à surveiller**
- **Erreurs 500** : Problèmes de code
- **Erreurs 404** : Fichiers manquants
- **Timeouts** : Problèmes de performance

---

## 🎉 Félicitations !

Votre application Flask est maintenant **déployée en ligne** !

### **Prochaines étapes**
1. **Tester** l'application complète
2. **Configurer** votre clé API Google Cloud
3. **Personnaliser** l'interface si nécessaire
4. **Partager** l'URL avec vos utilisateurs

### **Support**
- **Documentation** : `README_flask.md`
- **Déploiement** : `DEPLOYMENT_flask.md`
- **Issues** : Créez une issue sur GitHub

---

**🚀 Votre questionnaire EORTC QLQ-C30 est maintenant accessible en ligne !**
