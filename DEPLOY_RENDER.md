# Guide de Déploiement Render - Questionnaire EORTC QLQ-C30

## 🚀 Configuration Render Optimisée

### 1. **Variables d'Environnement Requises**

Dans le dashboard Render, configurez ces variables :

```
SECRET_KEY = questionnaire-eortc-2025-secret-key-production-very-secure
FLASK_DEBUG = False
AUDIO_ENABLED = True
USE_GEMINI_TTS = False
USE_PRO_MODEL = False
GOOGLE_CLOUD_API_KEY = (vide - pas nécessaire)
```

### 2. **Configuration du Service**

- **Type** : Web Service
- **Environment** : Python
- **Python Version** : 3.11.9
- **Build Command** : `pip install --upgrade pip && pip install -r requirements_flask.txt`
- **Start Command** : `python app_flask.py`
- **Health Check Path** : `/api/health`

### 3. **Structure des Fichiers**

```
questionnaire_flask/
├── app_flask.py              # Application principale
├── config_flask.py           # Configuration
├── requirements_flask.txt    # Dépendances
├── render.yaml              # Configuration Render
├── runtime.txt              # Version Python
├── Procfile                 # Commande de démarrage
├── models/
│   └── database_flask.py    # Base de données
├── routes/
│   ├── main_flask.py        # Routes principales
│   └── api_flask.py         # Routes API
├── static/
│   ├── css/
│   ├── js/
│   └── audio_cache/         # Audios préenregistrés
├── templates/
└── data/                    # Base de données SQLite
```

### 4. **Fonctionnalités**

#### ✅ **Fonctionnelles**
- Reconnaissance vocale continue
- Interface utilisateur responsive
- Base de données SQLite
- Export CSV/Excel
- Gestion des sessions

#### ⚠️ **Nécessitent des Audios Préenregistrés**
- Lecture automatique des questions
- Audio de test
- Messages d'aide vocaux

### 5. **Tests de Validation**

#### **Test 1 : Santé de l'Application**
```bash
curl https://votre-app.onrender.com/api/health
```

#### **Test 2 : Diagnostic Complet**
```bash
curl https://votre-app.onrender.com/api/diagnostic
```

#### **Test 3 : Session et Reconnaissance Vocale**
```bash
# Créer une session
curl -X POST https://votre-app.onrender.com/api/start_session \
  -H "Content-Type: application/json" \
  -d '{"initials":"TEST","birth_date":"01/01/1990","today_date":"14/10/2025","audio_enabled":true,"mode":"Continu (Web Speech)"}'

# Tester la reconnaissance vocale
curl -X POST https://votre-app.onrender.com/api/process_voice \
  -H "Content-Type: application/json" \
  -d '{"session_id":"SESSION_ID","question_num":1,"transcript":"beaucoup"}'
```

### 6. **Résolution des Problèmes**

#### **Problème : Session Invalide**
- Vérifier que la base de données est accessible
- Vérifier les logs Render pour les erreurs SQLite

#### **Problème : Audio Non Disponible**
- Vérifier que les fichiers audio sont dans `static/audio_cache/`
- Vérifier les permissions des fichiers

#### **Problème : Reconnaissance Vocale**
- Vérifier que le navigateur supporte Web Speech API
- Vérifier les permissions microphone
- Vérifier la console JavaScript pour les erreurs

### 7. **Optimisations**

#### **Performance**
- Cache des audios préenregistrés
- Base de données SQLite optimisée
- Compression des fichiers statiques

#### **Sécurité**
- Clé secrète forte
- Validation des entrées
- Protection CSRF
- HTTPS obligatoire

### 8. **Monitoring**

#### **Logs Render**
- Surveiller les erreurs de démarrage
- Vérifier l'utilisation mémoire
- Contrôler les timeouts

#### **Métriques**
- Temps de réponse API
- Taux de succès des sessions
- Erreurs de reconnaissance vocale

## 🎯 **Checklist de Déploiement**

- [ ] Variables d'environnement configurées
- [ ] Build réussi sans erreurs
- [ ] Application démarre correctement
- [ ] Route `/api/health` répond
- [ ] Route `/api/diagnostic` fonctionne
- [ ] Base de données accessible
- [ ] Reconnaissance vocale active
- [ ] Interface utilisateur responsive
- [ ] Tests de session réussis
- [ ] Export CSV fonctionnel

## 📞 **Support**

En cas de problème :
1. Vérifier les logs Render
2. Tester les routes API
3. Vérifier la configuration
4. Consulter la documentation Render
