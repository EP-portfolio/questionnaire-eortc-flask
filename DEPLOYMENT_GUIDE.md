# 🚀 Guide de Déploiement - Questionnaire EORTC QLQ-C30

## 📋 Vue d'ensemble

Ce guide présente les procédures complètes de déploiement et de migration du POC Flask vers un environnement Node.js/TypeScript en production. Il couvre la préparation, la migration, le déploiement et la maintenance.

---

## 🎯 Objectifs du Déploiement

### Migration Flask → Node.js
- **Backend** : Flask Python → Node.js + Express + TypeScript
- **Base de données** : SQLite → PostgreSQL
- **Cache** : Fichiers locaux → Redis
- **Audio** : Google Cloud TTS → Service optimisé
- **Reconnaissance vocale** : Web Speech API + Fallback serveur
- **Déploiement** : Monolithe → Microservices containerisés

### Architecture Cible
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend API   │
│   (React/Vue)   │◄──►│   (Kong/Nginx)  │◄──►│   (Node.js)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Load Balancer │
                       │   (HAProxy)     │
                       └─────────────────┘
                                │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│   PostgreSQL   │    │     Redis       │    │  Google Cloud   │
│   (Primary)    │    │     (Cache)     │    │   (TTS/STT)     │
└────────────────┘    └────────────────┘    └────────────────┘
```

---

## 🛠️ Préparation de l'Environnement

### 1. Prérequis Système

#### Serveur de Production
```bash
# Spécifications minimales
CPU: 4 cores (2.4GHz)
RAM: 8GB
Storage: 100GB SSD
Network: 1Gbps
OS: Ubuntu 20.04 LTS / CentOS 8 / RHEL 8
```

#### Outils de Développement
```bash
# Node.js et npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Docker et Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git
sudo apt-get install -y git

# PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Redis
sudo apt-get install -y redis-server
```

### 2. Configuration des Services

#### PostgreSQL
```bash
# Configuration PostgreSQL
sudo -u postgres psql
CREATE DATABASE questionnaire_prod;
CREATE USER questionnaire_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE questionnaire_prod TO questionnaire_user;
\q
```

#### Redis
```bash
# Configuration Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configuration de sécurité
sudo nano /etc/redis/redis.conf
# requirepass your_redis_password
# bind 127.0.0.1
sudo systemctl restart redis-server
```

#### Google Cloud
```bash
# Installation Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Configuration des services
gcloud services enable texttospeech.googleapis.com
gcloud services enable speech.googleapis.com
gcloud auth application-default login
```

---

## 📦 Structure du Projet Node.js

### 1. Initialisation du Projet

```bash
# Créer le projet
mkdir questionnaire-api
cd questionnaire-api

# Initialiser npm
npm init -y

# Installer TypeScript
npm install -D typescript @types/node ts-node nodemon
npx tsc --init

# Installer les dépendances principales
npm install express cors helmet compression morgan dotenv
npm install prisma @prisma/client
npm install redis ioredis
npm install @google-cloud/text-to-speech @google-cloud/speech
npm install multer uuid joi winston
npm install jsonwebtoken bcryptjs
npm install -D @types/express @types/cors @types/morgan @types/multer @types/uuid @types/jsonwebtoken @types/bcryptjs
```

### 2. Configuration TypeScript

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 3. Structure des Dossiers

```
questionnaire-api/
├── src/
│   ├── controllers/          # Contrôleurs API
│   │   ├── SessionController.ts
│   │   ├── ResponseController.ts
│   │   ├── QuestionController.ts
│   │   ├── AudioController.ts
│   │   ├── SpeechController.ts
│   │   └── ExportController.ts
│   ├── services/            # Services métier
│   │   ├── SessionService.ts
│   │   ├── ResponseService.ts
│   │   ├── AudioService.ts
│   │   ├── SpeechService.ts
│   │   └── StatisticsService.ts
│   ├── models/              # Modèles de données
│   │   ├── Session.ts
│   │   ├── Response.ts
│   │   ├── Question.ts
│   │   └── Export.ts
│   ├── middleware/          # Middleware Express
│   │   ├── auth.ts
│   │   ├── validation.ts
│   │   ├── errorHandler.ts
│   │   ├── rateLimiter.ts
│   │   └── logging.ts
│   ├── routes/              # Routes API
│   │   ├── sessions.ts
│   │   ├── responses.ts
│   │   ├── questions.ts
│   │   ├── audio.ts
│   │   ├── speech.ts
│   │   └── exports.ts
│   ├── utils/               # Utilitaires
│   │   ├── database.ts
│   │   ├── cache.ts
│   │   ├── validation.ts
│   │   ├── encryption.ts
│   │   └── helpers.ts
│   ├── types/               # Types TypeScript
│   │   ├── common.ts
│   │   ├── session.ts
│   │   ├── response.ts
│   │   ├── audio.ts
│   │   └── speech.ts
│   ├── config/              # Configuration
│   │   ├── database.ts
│   │   ├── redis.ts
│   │   ├── googleCloud.ts
│   │   └── app.ts
│   └── index.ts             # Point d'entrée
├── tests/                   # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                    # Documentation
│   ├── api/
│   ├── deployment/
│   └── architecture/
├── docker/                  # Configuration Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── k8s/                     # Configuration Kubernetes
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secret.yaml
├── scripts/                 # Scripts utilitaires
│   ├── migrate.ts
│   ├── seed.ts
│   └── backup.ts
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

---

## 🗄️ Migration de la Base de Données

### 1. Configuration Prisma

```typescript
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Session {
  id          String    @id @default(uuid())
  initials    String
  birthDate   DateTime
  todayDate   DateTime
  mode        SessionMode
  audioEnabled Boolean
  createdAt   DateTime @default(now())
  completedAt DateTime?
  metadata    Json?
  
  responses   Response[]
  
  @@map("sessions")
  @@index([createdAt])
  @@index([completedAt])
}

model Response {
  id          Int      @id @default(autoincrement())
  sessionId   String
  questionNum Int
  questionText String
  score       Int
  responseText String
  transcript  String?
  responseType ResponseType
  timestamp   DateTime @default(now())
  confidence  Float?
  
  session     Session  @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  
  @@map("responses")
  @@index([sessionId])
  @@index([questionNum])
  @@index([timestamp])
  @@unique([sessionId, questionNum])
}

model Question {
  id            Int     @id @default(autoincrement())
  questionNum   Int     @unique
  text          String
  scale         QuestionScale
  options       String[]
  speechText    String
  isTestQuestion Boolean @default(false)
  category      String?
  
  @@map("questions")
}

enum SessionMode {
  CONTINUOUS
  MANUAL
}

enum ResponseType {
  VOICE
  MANUAL
}

enum QuestionScale {
  TEST
  SCALE_1_4
  SCALE_1_7
}
```

### 2. Script de Migration

```typescript
// scripts/migrate.ts
import { PrismaClient } from '@prisma/client';
import sqlite3 from 'sqlite3';
import { promisify } from 'util';

export class DataMigration {
  private prisma: PrismaClient;
  private sqliteDb: sqlite3.Database;

  constructor() {
    this.prisma = new PrismaClient();
    this.sqliteDb = new sqlite3.Database('data/responses.db');
  }

  async migrateAll(): Promise<void> {
    console.log('🚀 Début de la migration SQLite → PostgreSQL');
    
    try {
      await this.migrateSessions();
      await this.migrateResponses();
      await this.migrateQuestions();
      
      console.log('✅ Migration terminée avec succès');
    } catch (error) {
      console.error('❌ Erreur lors de la migration:', error);
      throw error;
    } finally {
      await this.prisma.$disconnect();
      this.sqliteDb.close();
    }
  }

  private async migrateSessions(): Promise<void> {
    console.log('📊 Migration des sessions...');
    
    const sessions = await this.getSessionsFromSQLite();
    let migrated = 0;
    
    for (const session of sessions) {
      try {
        await this.prisma.session.create({
          data: {
            id: session.id,
            initials: session.initials,
            birthDate: new Date(session.birth_date),
            todayDate: new Date(session.today_date),
            mode: this.mapSessionMode(session.mode),
            audioEnabled: Boolean(session.audio_enabled),
            createdAt: new Date(session.created_at),
            completedAt: session.completed_at ? new Date(session.completed_at) : null,
            metadata: this.parseMetadata(session.metadata)
          }
        });
        migrated++;
      } catch (error) {
        console.error(`❌ Erreur migration session ${session.id}:`, error);
      }
    }
    
    console.log(`✅ ${migrated}/${sessions.length} sessions migrées`);
  }

  private async migrateResponses(): Promise<void> {
    console.log('💬 Migration des réponses...');
    
    const responses = await this.getResponsesFromSQLite();
    let migrated = 0;
    
    for (const response of responses) {
      try {
        await this.prisma.response.create({
          data: {
            sessionId: response.session_id,
            questionNum: response.question_num,
            questionText: response.question_text,
            score: response.score,
            responseText: response.response_text,
            transcript: response.transcript,
            responseType: this.mapResponseType(response.response_type),
            timestamp: new Date(response.timestamp),
            confidence: response.confidence
          }
        });
        migrated++;
      } catch (error) {
        console.error(`❌ Erreur migration réponse ${response.id}:`, error);
      }
    }
    
    console.log(`✅ ${migrated}/${responses.length} réponses migrées`);
  }

  private async migrateQuestions(): Promise<void> {
    console.log('❓ Migration des questions...');
    
    // Créer les questions EORTC QLQ-C30
    const questions = this.getEORTCQuestions();
    let migrated = 0;
    
    for (const question of questions) {
      try {
        await this.prisma.question.create({
          data: {
            questionNum: question.questionNum,
            text: question.text,
            scale: question.scale,
            options: question.options,
            speechText: question.speechText,
            isTestQuestion: question.isTestQuestion,
            category: question.category
          }
        });
        migrated++;
      } catch (error) {
        console.error(`❌ Erreur migration question ${question.questionNum}:`, error);
      }
    }
    
    console.log(`✅ ${migrated}/${questions.length} questions migrées`);
  }

  private async getSessionsFromSQLite(): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.sqliteDb.all('SELECT * FROM sessions', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  private async getResponsesFromSQLite(): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.sqliteDb.all('SELECT * FROM responses', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  private mapSessionMode(mode: string): string {
    switch (mode) {
      case 'Continu (Web Speech)':
      case 'continuous':
        return 'CONTINUOUS';
      case 'Standard':
      case 'manual':
        return 'MANUAL';
      default:
        return 'MANUAL';
    }
  }

  private mapResponseType(type: string): string {
    switch (type) {
      case 'voice':
        return 'VOICE';
      case 'manual':
        return 'MANUAL';
      default:
        return 'MANUAL';
    }
  }

  private parseMetadata(metadata: string): any {
    try {
      return metadata ? JSON.parse(metadata) : null;
    } catch {
      return null;
    }
  }

  private getEORTCQuestions(): any[] {
    // Retourner les 31 questions EORTC QLQ-C30
    return [
      {
        questionNum: 0,
        text: "Question 0 - Tests préalables",
        scale: "TEST",
        options: ["Test audio réussi", "Microphone validé"],
        speechText: "Question zéro. Tests audio et microphone...",
        isTestQuestion: true,
        category: "test"
      },
      // ... autres questions
    ];
  }
}

// Exécution du script
if (require.main === module) {
  const migration = new DataMigration();
  migration.migrateAll()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Migration failed:', error);
      process.exit(1);
    });
}
```

### 3. Exécution de la Migration

```bash
# Générer le client Prisma
npx prisma generate

# Appliquer les migrations
npx prisma migrate deploy

# Exécuter le script de migration
npx ts-node scripts/migrate.ts

# Vérifier les données
npx prisma studio
```

---

## 🐳 Containerisation Docker

### 1. Dockerfile

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

# Installer les dépendances de build
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./
COPY prisma ./prisma/

# Installer les dépendances
RUN npm ci --only=production

# Copier le code source
COPY . .

# Générer le client Prisma
RUN npx prisma generate

# Compiler TypeScript
RUN npm run build

# Stage de production
FROM node:18-alpine AS production

# Installer les dépendances runtime
RUN apk add --no-cache dumb-init

# Créer un utilisateur non-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

WORKDIR /app

# Copier les fichiers nécessaires
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./
COPY --from=builder --chown=nodejs:nodejs /app/prisma ./prisma

# Exposer le port
EXPOSE 3000

# Utilisateur non-root
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node dist/health-check.js

# Point d'entrée
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://questionnaire_user:secure_password@db:5432/questionnaire_prod
      - REDIS_URL=redis://redis:6379
      - GOOGLE_CLOUD_PROJECT_ID=your-project-id
      - GOOGLE_CLOUD_API_KEY=your-api-key
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=questionnaire_prod
      - POSTGRES_USER=questionnaire_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U questionnaire_user -d questionnaire_prod"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass your_redis_password
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. Configuration Nginx

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:3000;
    }

    server {
        listen 80;
        server_name api.questionnaire-eortc.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.questionnaire-eortc.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        location / {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
```

---

## ☸️ Déploiement Kubernetes

### 1. Configuration de Base

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: questionnaire
  labels:
    name: questionnaire
```

### 2. ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: questionnaire-config
  namespace: questionnaire
data:
  NODE_ENV: "production"
  PORT: "3000"
  API_VERSION: "1.0"
  LOG_LEVEL: "info"
  RATE_LIMIT_WINDOW_MS: "3600000"
  RATE_LIMIT_MAX_REQUESTS: "1000"
  AUDIO_CACHE_TTL: "86400"
  AUDIO_CACHE_BUCKET: "questionnaire-audio-cache"
```

### 3. Secrets

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: questionnaire-secrets
  namespace: questionnaire
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL3F1ZXN0aW9ubmFpcmVfdXNlcjpzZWN1cmVfcGFzc3dvcmRAZGI6NTQzMi9xdWVzdGlvbm5haXJlX3Byb2Q=
  REDIS_URL: cmVkaXM6Ly9yZWRpczozNjM3OQ==
  JWT_SECRET: eW91cl9qd3Rfc2VjcmV0
  GOOGLE_CLOUD_API_KEY: eW91cl9hcGlfa2V5
```

### 4. Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: questionnaire-api
  namespace: questionnaire
spec:
  replicas: 3
  selector:
    matchLabels:
      app: questionnaire-api
  template:
    metadata:
      labels:
        app: questionnaire-api
    spec:
      containers:
      - name: api
        image: questionnaire-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: questionnaire-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: questionnaire-secrets
              key: REDIS_URL
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: questionnaire-secrets
              key: JWT_SECRET
        - name: GOOGLE_CLOUD_API_KEY
          valueFrom:
            secretKeyRef:
              name: questionnaire-secrets
              key: GOOGLE_CLOUD_API_KEY
        envFrom:
        - configMapRef:
            name: questionnaire-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: uploads
          mountPath: /app/uploads
      volumes:
      - name: logs
        emptyDir: {}
      - name: uploads
        emptyDir: {}
```

### 5. Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: questionnaire-api-service
  namespace: questionnaire
spec:
  selector:
    app: questionnaire-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

### 6. Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: questionnaire-ingress
  namespace: questionnaire
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.questionnaire-eortc.com
    secretName: questionnaire-tls
  rules:
  - host: api.questionnaire-eortc.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: questionnaire-api-service
            port:
              number: 80
```

---

## 🔄 CI/CD Pipeline

### 1. GitHub Actions

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test
      
      - name: Run test coverage
        run: npm run test:coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Run Prisma generate
        run: npx prisma generate
      
      - name: Build Docker image
        run: docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - name: Deploy to Staging
        run: |
          echo "Deploying to staging environment"
          # Déploiement vers staging

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          echo "Deploying to production environment"
          # Déploiement vers production
```

### 2. Scripts de Déploiement

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Déploiement vers $ENVIRONMENT (version: $VERSION)"

# Variables d'environnement
case $ENVIRONMENT in
  staging)
    NAMESPACE="questionnaire-staging"
    DOMAIN="staging-api.questionnaire-eortc.com"
    ;;
  production)
    NAMESPACE="questionnaire"
    DOMAIN="api.questionnaire-eortc.com"
    ;;
  *)
    echo "❌ Environnement invalide: $ENVIRONMENT"
    exit 1
    ;;
esac

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."
kubectl version --client
kubectl get nodes

# Appliquer les configurations
echo "📦 Application des configurations Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Mettre à jour l'image
echo "🔄 Mise à jour de l'image Docker..."
kubectl set image deployment/questionnaire-api api=$REGISTRY/$IMAGE_NAME:$VERSION -n $NAMESPACE

# Attendre le déploiement
echo "⏳ Attente du déploiement..."
kubectl rollout status deployment/questionnaire-api -n $NAMESPACE --timeout=300s

# Vérifier la santé
echo "🏥 Vérification de la santé..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# Test de connectivité
echo "🔗 Test de connectivité..."
kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never -- \
  curl -f http://questionnaire-api-service:80/health

echo "✅ Déploiement terminé avec succès!"
echo "🌐 URL: https://$DOMAIN"
```

---

## 📊 Monitoring et Observabilité

### 1. Configuration Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'questionnaire-api'
    static_configs:
      - targets: ['questionnaire-api-service:80']
    metrics_path: /metrics
    scrape_interval: 30s
```

### 2. Métriques Personnalisées

```typescript
// monitoring/metrics.ts
import { register, Counter, Histogram, Gauge } from 'prom-client';

export const metrics = {
  // Compteurs
  requestsTotal: new Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code']
  }),

  sessionsCreated: new Counter({
    name: 'sessions_created_total',
    help: 'Total number of sessions created'
  }),

  responsesSaved: new Counter({
    name: 'responses_saved_total',
    help: 'Total number of responses saved',
    labelNames: ['type']
  }),

  // Histogrammes
  requestDuration: new Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route'],
    buckets: [0.1, 0.5, 1, 2, 5]
  }),

  audioGenerationTime: new Histogram({
    name: 'audio_generation_duration_seconds',
    help: 'Duration of audio generation in seconds',
    buckets: [0.5, 1, 2, 5, 10]
  }),

  speechRecognitionTime: new Histogram({
    name: 'speech_recognition_duration_seconds',
    help: 'Duration of speech recognition in seconds',
    buckets: [0.1, 0.5, 1, 2, 5]
  }),

  // Jauges
  activeSessions: new Gauge({
    name: 'active_sessions',
    help: 'Number of active sessions'
  }),

  audioCacheSize: new Gauge({
    name: 'audio_cache_size_bytes',
    help: 'Size of audio cache in bytes'
  }),

  databaseConnections: new Gauge({
    name: 'database_connections_active',
    help: 'Number of active database connections'
  })
};

// Middleware pour collecter les métriques
export const metricsMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    
    metrics.requestsTotal.inc({
      method: req.method,
      route: req.route?.path || req.path,
      status_code: res.statusCode
    });
    
    metrics.requestDuration.observe({
      method: req.method,
      route: req.route?.path || req.path
    }, duration);
  });
  
  next();
};
```

### 3. Configuration Grafana

```json
{
  "dashboard": {
    "title": "Questionnaire EORTC QLQ-C30 - Monitoring",
    "panels": [
      {
        "title": "Requests per Second",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{route}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "type": "singlestat",
        "targets": [
          {
            "expr": "active_sessions",
            "legendFormat": "Active Sessions"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

---

## 🔒 Sécurité et Conformité

### 1. Configuration de Sécurité

```typescript
// security/security.ts
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { Request, Response, NextFunction } from 'express';

export const securityMiddleware = [
  // Helmet pour les headers de sécurité
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", "https://api.questionnaire-eortc.com"],
        fontSrc: ["'self'", "https://fonts.gstatic.com"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    }
  }),

  // Rate limiting
  rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limite par IP
    message: {
      error: 'Trop de requêtes, veuillez réessayer plus tard',
      retryAfter: 15 * 60
    },
    standardHeaders: true,
    legacyHeaders: false
  }),

  // CORS
  cors({
    origin: process.env.CORS_ORIGIN?.split(',') || ['https://questionnaire-eortc.com'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Version']
  })
];

// Validation des entrées
export const inputValidation = (req: Request, res: Response, next: NextFunction) => {
  // Sanitisation des entrées
  const sanitizeInput = (obj: any): any => {
    if (typeof obj === 'string') {
      return obj.trim().replace(/[<>]/g, '');
    }
    if (typeof obj === 'object' && obj !== null) {
      const sanitized: any = {};
      for (const key in obj) {
        sanitized[key] = sanitizeInput(obj[key]);
      }
      return sanitized;
    }
    return obj;
  };

  req.body = sanitizeInput(req.body);
  req.query = sanitizeInput(req.query);
  req.params = sanitizeInput(req.params);

  next();
};
```

### 2. Audit et Logging

```typescript
// audit/audit.ts
import winston from 'winston';
import { Request, Response } from 'express';

export const auditLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/audit.log' }),
    new winston.transports.Console()
  ]
});

export const auditMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    auditLogger.info('API Request', {
      timestamp: new Date().toISOString(),
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      sessionId: req.headers['x-session-id'],
      userId: req.user?.id
    });
  });
  
  next();
};
```

### 3. Conformité RGPD

```typescript
// gdpr/gdpr.ts
export class GDPRService {
  // Anonymisation des données
  static async anonymizeSession(sessionId: string): Promise<void> {
    await prisma.session.update({
      where: { id: sessionId },
      data: {
        initials: 'ANONYMIZED',
        metadata: null
      }
    });
  }

  // Suppression des données
  static async deleteSession(sessionId: string): Promise<void> {
    await prisma.response.deleteMany({
      where: { sessionId }
    });
    
    await prisma.session.delete({
      where: { id: sessionId }
    });
  }

  // Export des données
  static async exportSessionData(sessionId: string): Promise<any> {
    const session = await prisma.session.findUnique({
      where: { id: sessionId },
      include: { responses: true }
    });

    return {
      session: {
        id: session.id,
        initials: session.initials,
        birthDate: session.birthDate,
        todayDate: session.todayDate,
        mode: session.mode,
        audioEnabled: session.audioEnabled,
        createdAt: session.createdAt,
        completedAt: session.completedAt
      },
      responses: session.responses.map(response => ({
        questionNum: response.questionNum,
        score: response.score,
        responseText: response.responseText,
        responseType: response.responseType,
        timestamp: response.timestamp
      }))
    };
  }

  // Consentement
  static async recordConsent(sessionId: string, consent: any): Promise<void> {
    await prisma.session.update({
      where: { id: sessionId },
      data: {
        metadata: {
          consent: {
            audio: consent.audio,
            dataProcessing: consent.dataProcessing,
            timestamp: new Date().toISOString()
          }
        }
      }
    });
  }
}
```

---

## 📈 Performance et Optimisation

### 1. Optimisations de Base de Données

```typescript
// optimizations/database.ts
export class DatabaseOptimizations {
  // Connection pooling
  static getPrismaClient(): PrismaClient {
    return new PrismaClient({
      datasources: {
        db: {
          url: process.env.DATABASE_URL
        }
      },
      log: ['query', 'info', 'warn', 'error']
    });
  }

  // Requêtes optimisées
  static async getSessionWithResponses(sessionId: string) {
    return await prisma.session.findUnique({
      where: { id: sessionId },
      include: {
        responses: {
          orderBy: { questionNum: 'asc' },
          select: {
            id: true,
            questionNum: true,
            score: true,
            responseText: true,
            responseType: true,
            timestamp: true,
            confidence: true
          }
        }
      }
    });
  }

  // Pagination optimisée
  static async getSessionsPaginated(page: number, limit: number, filters: any) {
    const skip = (page - 1) * limit;
    
    const [sessions, total] = await Promise.all([
      prisma.session.findMany({
        where: filters,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          initials: true,
          createdAt: true,
          completedAt: true,
          _count: {
            select: { responses: true }
          }
        }
      }),
      prisma.session.count({ where: filters })
    ]);

    return { sessions, total };
  }
}
```

### 2. Cache Redis

```typescript
// cache/redis.ts
import Redis from 'ioredis';

export class CacheService {
  private redis: Redis;

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL, {
      retryDelayOnFailover: 100,
      enableReadyCheck: false,
      maxRetriesPerRequest: null
    });
  }

  // Cache des sessions
  async getSession(sessionId: string): Promise<Session | null> {
    const cached = await this.redis.get(`session:${sessionId}`);
    return cached ? JSON.parse(cached) : null;
  }

  async setSession(sessionId: string, session: Session, ttl: number = 3600): Promise<void> {
    await this.redis.setex(`session:${sessionId}`, ttl, JSON.stringify(session));
  }

  // Cache des questions
  async getQuestion(questionNum: number): Promise<Question | null> {
    const cached = await this.redis.get(`question:${questionNum}`);
    return cached ? JSON.parse(cached) : null;
  }

  async setQuestion(questionNum: number, question: Question, ttl: number = 86400): Promise<void> {
    await this.redis.setex(`question:${questionNum}`, ttl, JSON.stringify(question));
  }

  // Cache des statistiques
  async getStatistics(sessionId: string): Promise<SessionStatistics | null> {
    const cached = await this.redis.get(`stats:${sessionId}`);
    return cached ? JSON.parse(cached) : null;
  }

  async setStatistics(sessionId: string, stats: SessionStatistics, ttl: number = 1800): Promise<void> {
    await this.redis.setex(`stats:${sessionId}`, ttl, JSON.stringify(stats));
  }

  // Invalidation du cache
  async invalidateSession(sessionId: string): Promise<void> {
    await this.redis.del(`session:${sessionId}`);
    await this.redis.del(`stats:${sessionId}`);
  }
}
```

### 3. Optimisations Audio

```typescript
// audio/optimizations.ts
export class AudioOptimizations {
  // Cache audio intelligent
  static async getCachedAudio(text: string, voice: string, speed: number): Promise<Buffer | null> {
    const hash = this.generateAudioHash(text, voice, speed);
    const cache = new CacheService();
    
    const cached = await cache.redis.get(`audio:${hash}`);
    return cached ? Buffer.from(cached, 'base64') : null;
  }

  static async setCachedAudio(text: string, voice: string, speed: number, audio: Buffer, ttl: number = 86400): Promise<void> {
    const hash = this.generateAudioHash(text, voice, speed);
    const cache = new CacheService();
    
    await cache.redis.setex(`audio:${hash}`, ttl, audio.toString('base64'));
  }

  // Génération audio optimisée
  static async generateAudioOptimized(text: string, voice: string, speed: number): Promise<Buffer> {
    // Vérifier le cache d'abord
    const cached = await this.getCachedAudio(text, voice, speed);
    if (cached) {
      return cached;
    }

    // Générer l'audio
    const audio = await this.generateAudio(text, voice, speed);
    
    // Mettre en cache
    await this.setCachedAudio(text, voice, speed, audio);
    
    return audio;
  }

  private static generateAudioHash(text: string, voice: string, speed: number): string {
    const crypto = require('crypto');
    return crypto.createHash('md5').update(`${text}:${voice}:${speed}`).digest('hex');
  }
}
```

---

## 🧪 Tests et Validation

### 1. Tests d'Intégration

```typescript
// tests/integration/api.test.ts
import request from 'supertest';
import { app } from '../src/app';

describe('API Integration Tests', () => {
  let sessionId: string;

  beforeAll(async () => {
    // Setup de la base de données de test
    await setupTestDatabase();
  });

  afterAll(async () => {
    // Nettoyage
    await cleanupTestDatabase();
  });

  describe('Sessions', () => {
    it('should create a session', async () => {
      const response = await request(app)
        .post('/api/v1/sessions')
        .send({
          initials: 'A B',
          birthDate: '1970-01-01',
          todayDate: '2024-01-15',
          audioEnabled: true,
          mode: 'continuous'
        })
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.sessionId).toBeDefined();
      
      sessionId = response.body.sessionId;
    });

    it('should get a session', async () => {
      const response = await request(app)
        .get(`/api/v1/sessions/${sessionId}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.session.id).toBe(sessionId);
    });
  });

  describe('Responses', () => {
    it('should save a response', async () => {
      const response = await request(app)
        .post('/api/v1/responses')
        .send({
          sessionId,
          questionNum: 1,
          score: 3,
          responseType: 'voice',
          transcript: 'plutôt',
          confidence: 0.95
        })
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.responseId).toBeDefined();
    });
  });

  describe('Audio', () => {
    it('should generate audio', async () => {
      const response = await request(app)
        .post('/api/v1/audio/generate')
        .send({
          text: 'Question 1. Test question',
          voice: 'fr-FR-Neural2-A',
          speed: 1.0
        })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.audioUrl).toBeDefined();
    });
  });
});
```

### 2. Tests de Performance

```typescript
// tests/performance/load.test.ts
import { performance } from 'perf_hooks';

describe('Performance Tests', () => {
  it('should handle concurrent sessions', async () => {
    const start = performance.now();
    
    const promises = Array.from({ length: 100 }, (_, i) => 
      request(app)
        .post('/api/v1/sessions')
        .send({
          initials: `A${i} B${i}`,
          birthDate: '1970-01-01',
          todayDate: '2024-01-15',
          audioEnabled: true,
          mode: 'continuous'
        })
    );

    const responses = await Promise.all(promises);
    const duration = performance.now() - start;

    expect(duration).toBeLessThan(5000); // Moins de 5 secondes
    expect(responses.every(r => r.status === 201)).toBe(true);
  });

  it('should handle audio generation under load', async () => {
    const start = performance.now();
    
    const promises = Array.from({ length: 50 }, () =>
      request(app)
        .post('/api/v1/audio/generate')
        .send({
          text: 'Test audio generation',
          voice: 'fr-FR-Neural2-A',
          speed: 1.0
        })
    );

    const responses = await Promise.all(promises);
    const duration = performance.now() - start;

    expect(duration).toBeLessThan(10000); // Moins de 10 secondes
    expect(responses.every(r => r.status === 200)).toBe(true);
  });
});
```

---

## 📋 Checklist de Déploiement

### Pré-déploiement
- [ ] Tests unitaires passent
- [ ] Tests d'intégration passent
- [ ] Tests de performance passent
- [ ] Code review approuvé
- [ ] Documentation mise à jour
- [ ] Variables d'environnement configurées
- [ ] Secrets et certificats en place
- [ ] Base de données migrée
- [ ] Cache Redis configuré
- [ ] Google Cloud configuré

### Déploiement
- [ ] Images Docker construites
- [ ] Configuration Kubernetes appliquée
- [ ] Services déployés
- [ ] Ingress configuré
- [ ] Certificats SSL installés
- [ ] DNS configuré
- [ ] Load balancer configuré
- [ ] Monitoring activé
- [ ] Logs centralisés
- [ ] Alertes configurées

### Post-déploiement
- [ ] Health checks passent
- [ ] Tests de connectivité
- [ ] Tests de charge
- [ ] Monitoring fonctionnel
- [ ] Logs collectés
- [ ] Alertes testées
- [ ] Backup configuré
- [ ] Documentation mise à jour
- [ ] Équipe formée
- [ ] Support activé

---

## 🆘 Dépannage et Maintenance

### Problèmes Courants

#### 1. Erreurs de Base de Données
```bash
# Vérifier la connexion
kubectl exec -it deployment/questionnaire-api -- npx prisma db push

# Vérifier les migrations
kubectl exec -it deployment/questionnaire-api -- npx prisma migrate status

# Réinitialiser la base
kubectl exec -it deployment/questionnaire-api -- npx prisma migrate reset
```

#### 2. Problèmes de Cache Redis
```bash
# Vérifier Redis
kubectl exec -it deployment/questionnaire-api -- redis-cli ping

# Vider le cache
kubectl exec -it deployment/questionnaire-api -- redis-cli flushall
```

#### 3. Problèmes Audio
```bash
# Vérifier Google Cloud
kubectl exec -it deployment/questionnaire-api -- gcloud auth list

# Tester TTS
kubectl exec -it deployment/questionnaire-api -- node -e "
const { TextToSpeechClient } = require('@google-cloud/text-to-speech');
const client = new TextToSpeechClient();
console.log('TTS client initialized');
"
```

### Maintenance

#### 1. Sauvegarde
```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

# Sauvegarde PostgreSQL
kubectl exec -it deployment/postgres -- pg_dump -U questionnaire_user questionnaire_prod > "$BACKUP_DIR/database.sql"

# Sauvegarde Redis
kubectl exec -it deployment/questionnaire-api -- redis-cli --rdb "$BACKUP_DIR/redis.rdb"

# Compression
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

#### 2. Mise à Jour
```bash
#!/bin/bash
# scripts/update.sh

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

echo "🔄 Mise à jour vers la version $VERSION"

# Mettre à jour l'image
kubectl set image deployment/questionnaire-api api=questionnaire-api:$VERSION

# Attendre le déploiement
kubectl rollout status deployment/questionnaire-api --timeout=300s

# Vérifier la santé
kubectl get pods -l app=questionnaire-api

echo "✅ Mise à jour terminée"
```

---

## 📞 Support et Documentation

### Contacts
- **Équipe DevOps** : devops@questionnaire-eortc.com
- **Équipe Backend** : backend@questionnaire-eortc.com
- **Support Production** : support@questionnaire-eortc.com

### Documentation
- **API Documentation** : https://docs.questionnaire-eortc.com
- **Architecture** : https://docs.questionnaire-eortc.com/architecture
- **Monitoring** : https://monitoring.questionnaire-eortc.com
- **Status Page** : https://status.questionnaire-eortc.com

### SLA
- **Disponibilité** : 99.9%
- **Temps de réponse** : < 200ms (P95)
- **Support** : 24/7 pour les incidents critiques
- **Maintenance** : Fenêtres planifiées le dimanche 2h-4h

---

*Ce guide de déploiement est maintenu à jour avec les dernières évolutions de l'infrastructure. Pour toute question, contactez l'équipe DevOps.*
