# 🏥 Questionnaire EORTC QLQ-C30 - Documentation Professionnelle

## 📋 Vue d'ensemble du Projet

Ce projet est un **POC (Proof of Concept)** d'application web pour le questionnaire médical EORTC QLQ-C30, développé en Flask Python et destiné à être migré vers un environnement Node.js/TypeScript pour une intégration dans un site web professionnel.

### 🎯 Objectif
Développer une application interactive de questionnaire médical avec reconnaissance vocale continue pour l'évaluation de la qualité de vie des patients atteints de cancer, selon les standards EORTC QLQ-C30.

### 🏗️ Architecture Actuelle (Flask)
- **Backend** : Flask 3.0.0 + SQLite
- **Frontend** : HTML5 + CSS3 + JavaScript ES6+
- **Audio** : Google Cloud TTS + Gemini TTS
- **Reconnaissance vocale** : Web Speech API + Fallback serveur
- **Déploiement** : Render + PythonAnywhere

### 🚀 Architecture Cible (Node.js/TypeScript)
- **Backend** : Node.js + Express + TypeScript
- **Base de données** : PostgreSQL + Prisma ORM
- **Cache** : Redis
- **Audio** : Google Cloud TTS optimisé
- **Reconnaissance vocale** : Web Speech API + Google Speech-to-Text
- **Déploiement** : Docker + Kubernetes

---

## 📚 Documentation Technique

### 📖 Guides Principaux

1. **[Guide d'Intégration](INTEGRATION_GUIDE.md)** - Migration Flask → Node.js/TypeScript
   - Architecture technique détaillée
   - Configuration des services
   - Exemples de code TypeScript
   - Tests et validation

2. **[Référence API](API_REFERENCE.md)** - Documentation complète de l'API REST
   - Endpoints détaillés avec exemples
   - Codes d'erreur et gestion
   - Rate limiting et sécurité
   - Intégration JavaScript/Python

3. **[Modèles de Données](DATA_MODELS.md)** - Schémas et relations
   - Structure de base de données
   - Types TypeScript
   - Relations et contraintes
   - Migration SQLite → PostgreSQL

4. **[Guide de Déploiement](DEPLOYMENT_GUIDE.md)** - Procédures de déploiement
   - Containerisation Docker
   - Déploiement Kubernetes
   - CI/CD Pipeline
   - Monitoring et maintenance

---

## 🔧 Fonctionnalités Principales

### ✅ Implémentées (Flask)
- **Questionnaire EORTC QLQ-C30** : 30 questions + Question 0 de test
- **Reconnaissance vocale continue** : Web Speech API (Chrome/Edge) + Fallback serveur (Firefox/Safari)
- **Synthèse vocale** : Google Cloud TTS + Gemini TTS avec cache intelligent
- **Interface utilisateur** : Design moderne et accessible
- **Gestion des sessions** : Création, sauvegarde, finalisation
- **Export des données** : JSON, CSV, Excel
- **Statistiques** : Calculs automatiques des scores
- **Tests audio** : Validation microphone et audio

### 🎯 À Implémenter (Node.js/TypeScript)
- **API REST complète** : Endpoints standardisés
- **Authentification JWT** : Sécurité renforcée
- **Base de données PostgreSQL** : Scalabilité améliorée
- **Cache Redis** : Performance optimisée
- **Monitoring** : Métriques et alertes
- **Tests automatisés** : Couverture complète
- **Documentation API** : OpenAPI/Swagger
- **Déploiement containerisé** : Docker + Kubernetes

---

## 🛠️ Stack Technologique

### Actuel (Flask)
```
Frontend: HTML5 + CSS3 + JavaScript ES6+
Backend: Flask 3.0.0 + SQLite
Audio: Google Cloud TTS + Gemini TTS
Reconnaissance: Web Speech API + Google Speech-to-Text
Déploiement: Render + PythonAnywhere
```

### Cible (Node.js/TypeScript)
```
Frontend: React/Vue.js + TypeScript
Backend: Node.js + Express + TypeScript
Base de données: PostgreSQL + Prisma ORM
Cache: Redis
Audio: Google Cloud TTS optimisé
Reconnaissance: Web Speech API + Google Speech-to-Text
Déploiement: Docker + Kubernetes
Monitoring: Prometheus + Grafana
```

---

## 📊 Modèles de Données

### Entités Principales
- **Session** : Session de questionnaire pour un patient
- **Response** : Réponse à une question (vocale ou manuelle)
- **Question** : Question du questionnaire EORTC QLQ-C30
- **AudioCache** : Cache des fichiers audio générés
- **Export** : Exports de données générés

### Relations
```
Session (1) ←→ (N) Response
Question (1) ←→ (N) Response
Session (1) ←→ (N) Export
```

---

## 🔌 API REST

### Endpoints Principaux
- **Sessions** : `POST /sessions`, `GET /sessions/:id`, `PUT /sessions/:id/complete`
- **Questions** : `GET /questions/:id`, `GET /questions`
- **Réponses** : `POST /responses`, `GET /sessions/:id/responses`
- **Audio** : `GET /audio/:questionId`, `POST /audio/generate`
- **Reconnaissance vocale** : `POST /speech/transcribe`, `POST /speech/interpret`
- **Export** : `GET /sessions/:id/export`, `POST /export/batch`
- **Statistiques** : `GET /sessions/:id/statistics`, `GET /statistics/global`

### Authentification
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-API-Version: 1.0
```

---

## 🚀 Déploiement

### Environnements
- **Développement** : Local avec Docker Compose
- **Staging** : Kubernetes avec base de données de test
- **Production** : Kubernetes avec base de données de production

### Infrastructure
- **Containerisation** : Docker + Docker Compose
- **Orchestration** : Kubernetes
- **Base de données** : PostgreSQL (primary) + Redis (cache)
- **Load Balancer** : Nginx + HAProxy
- **Monitoring** : Prometheus + Grafana
- **Logs** : ELK Stack (Elasticsearch + Logstash + Kibana)

---

## 🔒 Sécurité et Conformité

### Sécurité
- **Authentification** : JWT avec expiration
- **Autorisation** : RBAC (Role-Based Access Control)
- **Validation** : Joi pour la validation des données
- **Rate Limiting** : Protection contre les abus
- **CORS** : Configuration sécurisée
- **Headers** : Helmet pour les headers de sécurité

### Conformité RGPD
- **Anonymisation** : Données personnelles anonymisées
- **Suppression** : Droit à l'oubli
- **Export** : Portabilité des données
- **Consentement** : Gestion des consentements
- **Audit** : Traçabilité des accès

---

## 📈 Performance et Monitoring

### Métriques
- **Requêtes** : Nombre, durée, taux d'erreur
- **Sessions** : Actives, terminées, durée moyenne
- **Audio** : Cache hit rate, temps de génération
- **Reconnaissance vocale** : Précision, temps de traitement
- **Base de données** : Connexions, requêtes lentes

### Alertes
- **Disponibilité** : < 99.9%
- **Temps de réponse** : > 200ms (P95)
- **Erreurs** : > 1% de taux d'erreur
- **Ressources** : CPU > 80%, RAM > 90%

---

## 🧪 Tests et Qualité

### Types de Tests
- **Tests unitaires** : Jest + TypeScript
- **Tests d'intégration** : Supertest + Jest
- **Tests de performance** : Artillery + K6
- **Tests de sécurité** : OWASP ZAP
- **Tests de charge** : JMeter + Gatling

### Couverture
- **Code** : > 90% de couverture
- **API** : 100% des endpoints testés
- **Fonctionnalités** : Tests end-to-end
- **Performance** : Tests de charge réguliers

---

## 📞 Support et Maintenance

### Contacts
- **Équipe Backend** : backend@questionnaire-eortc.com
- **Équipe DevOps** : devops@questionnaire-eortc.com
- **Support Production** : support@questionnaire-eortc.com

### Documentation
- **API** : https://docs.questionnaire-eortc.com
- **Architecture** : https://docs.questionnaire-eortc.com/architecture
- **Monitoring** : https://monitoring.questionnaire-eortc.com
- **Status** : https://status.questionnaire-eortc.com

### SLA
- **Disponibilité** : 99.9%
- **Temps de réponse** : < 200ms (P95)
- **Support** : 24/7 pour les incidents critiques
- **Maintenance** : Fenêtres planifiées le dimanche 2h-4h

---

## 🎯 Prochaines Étapes

### Phase 1 : Migration (2-3 semaines)
1. **Setup** de l'environnement Node.js/TypeScript
2. **Migration** des données SQLite → PostgreSQL
3. **Implémentation** des services principaux
4. **Tests** et validation

### Phase 2 : Optimisation (1-2 semaines)
1. **Performance** : Cache Redis, optimisations DB
2. **Sécurité** : Authentification, validation
3. **Monitoring** : Métriques, alertes
4. **Documentation** : API, architecture

### Phase 3 : Déploiement (1 semaine)
1. **Containerisation** : Docker + Kubernetes
2. **CI/CD** : Pipeline automatisé
3. **Production** : Déploiement et monitoring
4. **Formation** : Équipe et support

---

## 📋 Checklist de Migration

### Pré-requis
- [ ] Environnement Node.js configuré
- [ ] Base de données PostgreSQL créée
- [ ] Redis configuré
- [ ] Google Cloud configuré
- [ ] Docker et Kubernetes prêts

### Migration
- [ ] Données migrées (SQLite → PostgreSQL)
- [ ] Services implémentés
- [ ] API REST complète
- [ ] Tests écrits et passants
- [ ] Documentation mise à jour

### Déploiement
- [ ] Images Docker construites
- [ ] Configuration Kubernetes
- [ ] CI/CD Pipeline
- [ ] Monitoring configuré
- [ ] Tests de charge

### Post-déploiement
- [ ] Health checks passent
- [ ] Monitoring fonctionnel
- [ ] Alertes configurées
- [ ] Documentation finale
- [ ] Équipe formée

---

## 🔗 Liens Utiles

### Documentation
- [Guide d'Intégration](INTEGRATION_GUIDE.md)
- [Référence API](API_REFERENCE.md)
- [Modèles de Données](DATA_MODELS.md)
- [Guide de Déploiement](DEPLOYMENT_GUIDE.md)

### Ressources Externes
- [EORTC QLQ-C30](https://www.eortc.org/app/uploads/2021/08/QLQ-C30.pdf)
- [Google Cloud TTS](https://cloud.google.com/text-to-speech)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Prisma ORM](https://www.prisma.io/docs)

---

*Cette documentation est maintenue à jour avec les dernières évolutions du projet. Pour toute question, contactez l'équipe de développement.*
