# 🏥 Questionnaire EORTC QLQ-C30 - Version Flask

Application Flask avec reconnaissance vocale continue pour l'évaluation de la qualité de vie des patients.

## 🎯 Fonctionnalités Principales

### ✨ **Reconnaissance Vocale Continue**
- **1 SEUL clic** au démarrage pour les 30 questions
- **Parlez naturellement** pour chaque question
- **Passage automatique** à la question suivante
- **Support Web Speech API** (Chrome/Edge) + Fallback (Firefox/Safari)

### 🔊 **Assistance Audio**
- **Lecture automatique** des questions
- **Synthèse vocale** avec Google Cloud TTS/Gemini TTS
- **Cache audio** pour optimiser les performances
- **Interface accessible** pour personnes âgées

### 📊 **Gestion des Données**
- **Base de données SQLite** pour la persistance
- **Export multi-format** (JSON, CSV, Excel)
- **Statistiques détaillées** de complétion
- **Conformité RGPD** avec anonymisation

## 🏗️ Architecture

```
questionnaire_flask/
├── app_flask.py                    # Application principale Flask
├── config_flask.py                 # Configuration
├── requirements_flask.txt          # Dépendances Python
├── models/
│   ├── __init__.py
│   └── database_flask.py           # Gestionnaire SQLite
├── routes/
│   ├── __init__.py
│   ├── main_flask.py               # Routes principales
│   └── api_flask.py                # API AJAX
├── static/
│   ├── css/
│   │   └── style_flask.css         # Styles CSS
│   ├── js/
│   │   ├── speech_recognition_flask.js  # Web Speech API
│   │   └── questionnaire_flask.js       # Logique questionnaire
│   └── audio_cache/                # Cache fichiers audio
├── templates/
│   ├── base_flask.html             # Template de base
│   ├── permission_flask.html       # Tests navigateur
│   ├── accueil_flask.html           # Informations personnelles
│   ├── questionnaire_flask.html    # Questionnaire principal
│   └── resultat_flask.html          # Résultats et export
├── data/
│   └── responses.db                 # Base de données SQLite
└── README_flask.md                  # Documentation
```

## 🚀 Installation

### 1. **Prérequis**
- Python 3.8+
- Navigateur moderne (Chrome/Edge recommandé)
- Clé API Google Cloud (optionnel)

### 2. **Installation des dépendances**
```bash
cd questionnaire_flask
pip install -r requirements_flask.txt
```

### 3. **Configuration**
```bash
# Variables d'environnement
export GOOGLE_CLOUD_API_KEY="votre_cle_api"
export FLASK_DEBUG=True
export AUDIO_ENABLED=True
```

### 4. **Lancement**
```bash
python app_flask.py
```

L'application sera accessible sur `http://localhost:5000`

## 🔧 Configuration

### **Variables d'Environnement**

| Variable | Description | Défaut |
|----------|-------------|---------|
| `GOOGLE_CLOUD_API_KEY` | Clé API Google Cloud TTS | Optionnel |
| `FLASK_DEBUG` | Mode debug Flask | `False` |
| `AUDIO_ENABLED` | Activation audio | `True` |
| `USE_GEMINI_TTS` | Utiliser Gemini TTS | `True` |
| `USE_PRO_MODEL` | Modèle Pro Gemini | `True` |
| `SECRET_KEY` | Clé secrète Flask | `dev-secret-key` |

### **Configuration Base de Données**
- **Type** : SQLite
- **Fichier** : `data/responses.db`
- **Tables** : `sessions`, `responses`
- **Index** : Optimisés pour les performances

## 🎤 Reconnaissance Vocale

### **Mode Web Speech API (Chrome/Edge)**
- **Reconnaissance continue** avec 1 seul clic
- **Langue** : Français (fr-FR)
- **Confiance** : Validation automatique
- **Redémarrage** : Automatique en cas d'erreur

### **Mode Fallback (Firefox/Safari)**
- **Enregistrement** par question
- **Traitement** côté serveur
- **Interface** adaptée

### **Mots-clés Supportés**

#### **Échelle 1-4**
- **1** : "pas du tout", "pas", "jamais", "aucun"
- **2** : "peu", "un petit peu", "légèrement"
- **3** : "assez", "moyennement", "modérément"
- **4** : "beaucoup", "très", "tout à fait", "complètement"

#### **Échelle 1-7**
- **1** : "très mauvais", "horrible", "terrible"
- **2** : "mauvais", "mal"
- **3** : "plutôt mauvais", "pas bien"
- **4** : "moyen", "neutre", "correct"
- **5** : "plutôt bon", "plutôt bien", "assez bien"
- **6** : "bon", "bien"
- **7** : "très bon", "excellent", "parfait", "super"

## 🔊 Système Audio

### **Configuration TTS**
- **Google Cloud TTS** : Voix Neural2-A
- **Gemini TTS** : Voix Achernar (recommandé)
- **Cache** : Fichiers .wav pré-générés
- **Qualité** : 24kHz, 16-bit, mono

### **Gestion du Cache**
- **Dossier** : `static/audio_cache/`
- **Format** : Hash MD5 des textes
- **Nettoyage** : Automatique
- **Performance** : Lecture instantanée

## 📊 Base de Données

### **Table `sessions`**
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    initials TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    today_date TEXT NOT NULL,
    mode TEXT NOT NULL,
    audio_enabled BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);
```

### **Table `responses`**
```sql
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_num INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    score INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    transcript TEXT,
    response_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

## 🌐 API Endpoints

### **Routes Principales**
- `GET /` → Page de permissions
- `GET /accueil` → Informations personnelles
- `GET /questionnaire` → Questionnaire principal
- `GET /resultat/<session_id>` → Résultats

### **API AJAX**
- `POST /api/start_session` → Créer une session
- `GET /api/get_question/<int:question_num>` → Récupérer une question
- `POST /api/process_voice` → Traiter réponse vocale
- `POST /api/save_manual_response` → Sauvegarder réponse manuelle
- `GET /api/get_audio/<int:question_num>` → Servir fichier audio
- `GET /api/get_session_data/<session_id>` → Données de session
- `POST /api/complete_session/<session_id>` → Finaliser session
- `GET /api/export_session/<session_id>` → Exporter données

## 🎨 Interface Utilisateur

### **Design**
- **Couleurs** : Gradient violet/bleu (#667eea → #764ba2)
- **Typographie** : System fonts, tailles accessibles
- **Responsive** : Mobile-first
- **Accessibilité** : Contrastes élevés, gros textes

### **Composants**
- **Box question** : Gradient violet, texte blanc
- **Indicateur micro** : Box verte animée 🎤
- **Feedback visuel** : Notifications colorées
- **Barre progression** : Pourcentage + barre visuelle

## 🚀 Déploiement

### **PythonAnywhere (Recommandé)**
1. Créer un compte sur [PythonAnywhere](https://www.pythonanywhere.com)
2. Uploader les fichiers via Git ou interface web
3. Configurer les variables d'environnement
4. Installer les dépendances
5. Configurer le domaine

### **Render**
1. Connecter le repository Git
2. Configurer les variables d'environnement
3. Déployer automatiquement

### **Railway**
1. Connecter le repository
2. Configurer les variables
3. Déployer

### **Configuration Production**
```bash
# Variables d'environnement
export FLASK_DEBUG=False
export SECRET_KEY="cle_secrete_production"
export GOOGLE_CLOUD_API_KEY="votre_cle_api"
```

## 🔒 Sécurité et RGPD

### **Conformité RGPD**
- **Anonymisation** : Initiales uniquement
- **Consentement** : Checkbox obligatoire
- **Suppression** : Données supprimables
- **Export** : Données exportables

### **Sécurité**
- **Validation** : Côté serveur obligatoire
- **Session** : Gestion sécurisée
- **HTTPS** : Obligatoire en production
- **CORS** : Configuré pour les requêtes AJAX

## 🧪 Tests

### **Tests Manuels**
1. **Navigation** : Toutes les pages
2. **Audio** : Lecture et reconnaissance
3. **Reconnaissance vocale** : Mots-clés
4. **Export** : Tous les formats
5. **Responsive** : Mobile et desktop

### **Tests Navigateurs**
- ✅ **Chrome** : Mode continu
- ✅ **Edge** : Mode continu
- ⚠️ **Firefox** : Mode standard
- ⚠️ **Safari** : Mode standard

## 📈 Performance

### **Optimisations**
- **Cache audio** : Fichiers pré-générés
- **Base de données** : Index optimisés
- **CSS/JS** : Minifiés en production
- **Images** : Optimisées

### **Métriques**
- **Temps de réponse** : < 200ms
- **Taille cache** : ~50MB pour 30 questions
- **Mémoire** : < 100MB
- **CPU** : Faible utilisation

## 🐛 Dépannage

### **Problèmes Courants**

#### **Audio ne fonctionne pas**
```bash
# Vérifier la clé API
echo $GOOGLE_CLOUD_API_KEY

# Vérifier les permissions
chmod 755 static/audio_cache/
```

#### **Reconnaissance vocale ne fonctionne pas**
- Vérifier les permissions microphone
- Utiliser Chrome/Edge pour le mode continu
- Vérifier la connexion internet

#### **Base de données corrompue**
```bash
# Supprimer et recréer
rm data/responses.db
python -c "from models.database_flask import DatabaseManager; DatabaseManager()"
```

### **Logs**
```bash
# Activer les logs détaillés
export FLASK_DEBUG=True
python app_flask.py
```

## 📚 Documentation API

### **Exemple de requête**
```javascript
// Créer une session
fetch('/api/start_session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        initials: 'A B',
        birth_date: '1970-01-01',
        today_date: '2024-01-01',
        audio_enabled: true,
        mode: 'Continu (Web Speech)'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### **Exemple de réponse**
```json
{
    "success": true,
    "session_id": "uuid-string",
    "message": "Session créée avec succès"
}
```

## 🤝 Contribution

### **Développement**
1. Fork le repository
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Créer une Pull Request

### **Structure du Code**
- **Modèles** : `models/`
- **Routes** : `routes/`
- **Templates** : `templates/`
- **Statiques** : `static/`
- **Configuration** : `config_flask.py`

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

### **Contact**
- **Email** : support@questionnaire-eortc.fr
- **Documentation** : [Wiki du projet](https://github.com/username/questionnaire-flask/wiki)
- **Issues** : [GitHub Issues](https://github.com/username/questionnaire-flask/issues)

### **FAQ**
- **Q** : L'audio ne fonctionne pas
- **R** : Vérifiez votre clé API Google Cloud et les permissions

- **Q** : La reconnaissance vocale ne fonctionne pas
- **R** : Utilisez Chrome/Edge et autorisez l'accès au microphone

- **Q** : Comment déployer en production ?
- **R** : Suivez le guide de déploiement dans la documentation

---

**🎉 Félicitations ! Votre application Flask est prête à être déployée !**
