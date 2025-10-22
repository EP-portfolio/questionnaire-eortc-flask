# 🏥 Questionnaire EORTC QLQ-C30 - Guide d'Intégration

## 📋 Vue d'ensemble

Ce document présente l'intégration du POC Flask vers un environnement Node.js/TypeScript. L'application actuelle est un questionnaire médical avec reconnaissance vocale continue pour l'évaluation de la qualité de vie des patients.

### 🎯 Objectifs de l'Intégration

- **Migration** : Flask Python → Node.js/TypeScript
- **Architecture** : Microservices ou monolithe modulaire
- **API** : RESTful avec documentation OpenAPI
- **Base de données** : Migration SQLite → PostgreSQL/MongoDB
- **Reconnaissance vocale** : Intégration services cloud
- **Déploiement** : Containerisation Docker + orchestration

---

## 🏗️ Architecture Actuelle (Flask)

### Structure du Projet
```
questionnaire_flask/
├── app_flask.py                    # Application principale
├── config_flask.py                 # Configuration
├── questionnaire_logic.py         # Logique métier (30 questions)
├── audio_handler_simple_flask.py  # Gestion audio
├── models/
│   └── database_flask.py          # Gestionnaire SQLite
├── routes/
│   ├── main_flask.py              # Routes principales
│   └── api_flask.py               # API AJAX
├── static/
│   ├── css/style_flask.css        # Styles
│   ├── js/
│   │   ├── questionnaire_flask.js # Logique questionnaire
│   │   └── speech_recognition_flask.js # Reconnaissance vocale
│   └── audio_cache/               # Cache fichiers audio
├── templates/                      # Templates Jinja2
└── data/responses.db              # Base SQLite
```

### Technologies Utilisées
- **Backend** : Flask 3.0.0, SQLite, Gunicorn
- **Frontend** : HTML5, CSS3, JavaScript ES6+
- **Audio** : Google Cloud TTS, Gemini TTS
- **Reconnaissance** : Web Speech API + Fallback serveur
- **Déploiement** : Render, PythonAnywhere

---

## 🔄 Architecture Cible (Node.js/TypeScript)

### Structure Proposée
```
questionnaire-api/
├── src/
│   ├── controllers/               # Contrôleurs API
│   ├── services/                  # Services métier
│   ├── models/                    # Modèles de données
│   ├── middleware/                # Middleware Express
│   ├── routes/                    # Routes API
│   ├── utils/                     # Utilitaires
│   └── types/                     # Types TypeScript
├── public/                        # Assets statiques
├── tests/                         # Tests unitaires/intégration
├── docs/                          # Documentation API
├── docker/                        # Configuration Docker
└── package.json                   # Dépendances Node.js
```

### Stack Technologique Recommandée
- **Backend** : Node.js + Express + TypeScript
- **Base de données** : PostgreSQL + Prisma ORM
- **Cache** : Redis
- **Audio** : Google Cloud TTS API
- **Reconnaissance** : Web Speech API + Google Speech-to-Text
- **Frontend** : React/Vue.js + TypeScript
- **Déploiement** : Docker + Kubernetes

---

## 📊 Modèles de Données

### 1. Session (Sessions)
```typescript
interface Session {
  id: string;                    // UUID v4
  initials: string;              // Initiales patient
  birthDate: string;             // Date naissance (ISO 8601)
  todayDate: string;             // Date questionnaire (ISO 8601)
  mode: 'continuous' | 'manual'; // Mode de réponse
  audioEnabled: boolean;         // Audio activé
  createdAt: Date;               // Timestamp création
  completedAt?: Date;            // Timestamp fin
  metadata?: Record<string, any>; // Données additionnelles
}
```

### 2. Response (Réponses)
```typescript
interface Response {
  id: number;                    // ID auto-incrément
  sessionId: string;             // Référence session
  questionNum: number;           // Numéro question (1-30)
  questionText: string;          // Texte question
  score: number;                 // Score réponse (1-4 ou 1-7)
  responseText: string;          // Texte réponse
  transcript?: string;           // Transcription vocale
  responseType: 'voice' | 'manual'; // Type réponse
  timestamp: Date;               // Timestamp réponse
  confidence?: number;           // Confiance reconnaissance
}
```

### 3. Question (Questions)
```typescript
interface Question {
  id: number;                    // Numéro question (0-30)
  text: string;                  // Texte question
  scale: '1-4' | '1-7' | 'test'; // Échelle réponse
  options: string[];             // Options de réponse
  speechText: string;            // Texte synthèse vocale
  isTestQuestion: boolean;       // Question test (Q0)
  category?: string;             // Catégorie question
}
```

---

## 🔌 API REST Complète

### Base URL
```
https://api.questionnaire-eortc.com/v1
```

### Authentification
```typescript
// Headers requis
{
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json",
  "X-API-Version": "1.0"
}
```

### Endpoints Principaux

#### 1. Sessions
```typescript
// POST /sessions - Créer une session
interface CreateSessionRequest {
  initials: string;
  birthDate: string;
  todayDate: string;
  audioEnabled: boolean;
  mode: 'continuous' | 'manual';
}

interface CreateSessionResponse {
  success: boolean;
  sessionId: string;
  message: string;
}

// GET /sessions/:id - Récupérer une session
interface GetSessionResponse {
  success: boolean;
  session: Session;
}

// PUT /sessions/:id/complete - Finaliser une session
interface CompleteSessionResponse {
  success: boolean;
  message: string;
}
```

#### 2. Questions
```typescript
// GET /questions/:id - Récupérer une question
interface GetQuestionResponse {
  success: boolean;
  question: Question;
  questionNum: number;
}

// GET /questions - Lister toutes les questions
interface ListQuestionsResponse {
  success: boolean;
  questions: Question[];
  total: number;
}
```

#### 3. Réponses
```typescript
// POST /responses - Sauvegarder une réponse
interface SaveResponseRequest {
  sessionId: string;
  questionNum: number;
  score: number;
  responseType: 'voice' | 'manual';
  transcript?: string;
  confidence?: number;
}

interface SaveResponseResponse {
  success: boolean;
  responseId: number;
  nextQuestion?: number;
  isComplete: boolean;
}

// GET /sessions/:id/responses - Récupérer les réponses
interface GetResponsesResponse {
  success: boolean;
  responses: Response[];
  statistics: SessionStatistics;
}
```

#### 4. Audio
```typescript
// GET /audio/:questionId - Récupérer fichier audio
// Response: Audio file (audio/wav)

// POST /audio/generate - Générer audio personnalisé
interface GenerateAudioRequest {
  text: string;
  voice?: string;
  speed?: number;
}

interface GenerateAudioResponse {
  success: boolean;
  audioUrl: string;
  duration: number;
}
```

#### 5. Reconnaissance Vocale
```typescript
// POST /speech/transcribe - Transcrire audio
interface TranscribeRequest {
  audio: File; // Audio file
  language: string;
  sessionId: string;
}

interface TranscribeResponse {
  success: boolean;
  transcript: string;
  confidence: number;
  alternatives: string[];
}

// POST /speech/interpret - Interpréter transcription
interface InterpretRequest {
  transcript: string;
  questionNum: number;
  sessionId: string;
}

interface InterpretResponse {
  success: boolean;
  score?: number;
  responseText?: string;
  suggestions?: string[];
  error?: string;
}
```

#### 6. Export
```typescript
// GET /sessions/:id/export - Exporter données
interface ExportRequest {
  format: 'json' | 'csv' | 'excel';
  includeAudio?: boolean;
}

interface ExportResponse {
  success: boolean;
  downloadUrl: string;
  expiresAt: Date;
}
```

---

## 🛠️ Guide d'Intégration Node.js/TypeScript

### 1. Configuration du Projet

#### package.json
```json
{
  "name": "questionnaire-api",
  "version": "1.0.0",
  "description": "EORTC QLQ-C30 Questionnaire API",
  "main": "dist/index.js",
  "scripts": {
    "dev": "nodemon src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "compression": "^1.7.4",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "prisma": "^5.0.0",
    "@prisma/client": "^5.0.0",
    "redis": "^4.6.0",
    "google-cloud-text-to-speech": "^4.0.0",
    "google-cloud-speech": "^6.0.0",
    "multer": "^1.4.5",
    "uuid": "^9.0.0",
    "joi": "^17.9.0",
    "winston": "^3.10.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.0",
    "@types/cors": "^2.8.0",
    "@types/morgan": "^1.9.0",
    "@types/multer": "^1.4.0",
    "@types/uuid": "^9.0.0",
    "typescript": "^5.0.0",
    "nodemon": "^3.0.0",
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "ts-jest": "^29.0.0"
  }
}
```

#### tsconfig.json
```json
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
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 2. Configuration Base de Données

#### schema.prisma
```prisma
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
  mode        String
  audioEnabled Boolean
  createdAt   DateTime @default(now())
  completedAt DateTime?
  metadata    Json?
  
  responses   Response[]
  
  @@map("sessions")
}

model Response {
  id          Int      @id @default(autoincrement())
  sessionId   String
  questionNum Int
  questionText String
  score       Int
  responseText String
  transcript  String?
  responseType String
  timestamp   DateTime @default(now())
  confidence  Float?
  
  session     Session  @relation(fields: [sessionId], references: [id])
  
  @@map("responses")
}

model Question {
  id            Int     @id @default(autoincrement())
  questionNum   Int     @unique
  text          String
  scale         String
  options       String[]
  speechText    String
  isTestQuestion Boolean @default(false)
  category      String?
  
  @@map("questions")
}
```

### 3. Services Principaux

#### SessionService
```typescript
import { PrismaClient } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export class SessionService {
  constructor(private prisma: PrismaClient) {}

  async createSession(data: CreateSessionRequest): Promise<Session> {
    const session = await this.prisma.session.create({
      data: {
        id: uuidv4(),
        initials: data.initials,
        birthDate: new Date(data.birthDate),
        todayDate: new Date(data.todayDate),
        mode: data.mode,
        audioEnabled: data.audioEnabled,
      },
    });
    return session;
  }

  async getSession(id: string): Promise<Session | null> {
    return await this.prisma.session.findUnique({
      where: { id },
      include: { responses: true },
    });
  }

  async completeSession(id: string): Promise<void> {
    await this.prisma.session.update({
      where: { id },
      data: { completedAt: new Date() },
    });
  }
}
```

#### AudioService
```typescript
import { TextToSpeechClient } from '@google-cloud/text-to-speech';
import { Storage } from '@google-cloud/storage';

export class AudioService {
  private ttsClient: TextToSpeechClient;
  private storage: Storage;

  constructor() {
    this.ttsClient = new TextToSpeechClient();
    this.storage = new Storage();
  }

  async generateAudio(text: string, voice: string = 'fr-FR-Neural2-A'): Promise<Buffer> {
    const request = {
      input: { text },
      voice: { languageCode: 'fr-FR', name: voice },
      audioConfig: { audioEncoding: 'LINEAR16' as const },
    };

    const [response] = await this.ttsClient.synthesizeSpeech(request);
    return response.audioContent as Buffer;
  }

  async getCachedAudio(hash: string): Promise<Buffer | null> {
    try {
      const [file] = await this.storage
        .bucket('questionnaire-audio-cache')
        .file(`${hash}.wav`)
        .download();
      return file;
    } catch {
      return null;
    }
  }
}
```

#### SpeechRecognitionService
```typescript
import { SpeechClient } from '@google-cloud/speech';

export class SpeechRecognitionService {
  private speechClient: SpeechClient;

  constructor() {
    this.speechClient = new SpeechClient();
  }

  async transcribeAudio(audioBuffer: Buffer): Promise<TranscribeResponse> {
    const request = {
      audio: { content: audioBuffer.toString('base64') },
      config: {
        encoding: 'WEBM_OPUS' as const,
        sampleRateHertz: 48000,
        languageCode: 'fr-FR',
        enableAutomaticPunctuation: false,
        enableWordTimeOffsets: false,
        enableWordConfidence: true,
        useEnhanced: true,
      },
    };

    const [response] = await this.speechClient.recognize(request);
    const result = response.results[0];
    
    if (!result) {
      return {
        success: false,
        transcript: '',
        confidence: 0,
        alternatives: [],
      };
    }

    const alternative = result.alternatives[0];
    return {
      success: true,
      transcript: alternative.transcript,
      confidence: alternative.confidence,
      alternatives: result.alternatives.map(alt => alt.transcript),
    };
  }
}
```

### 4. Contrôleurs API

#### SessionController
```typescript
import { Request, Response } from 'express';
import { SessionService } from '../services/SessionService';
import { validateSessionData } from '../utils/validation';

export class SessionController {
  constructor(private sessionService: SessionService) {}

  async createSession(req: Request, res: Response): Promise<void> {
    try {
      const { error, value } = validateSessionData(req.body);
      if (error) {
        res.status(400).json({ error: error.details[0].message });
        return;
      }

      const session = await this.sessionService.createSession(value);
      res.status(201).json({
        success: true,
        sessionId: session.id,
        message: 'Session créée avec succès',
      });
    } catch (error) {
      res.status(500).json({ error: 'Erreur création session' });
    }
  }

  async getSession(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const session = await this.sessionService.getSession(id);
      
      if (!session) {
        res.status(404).json({ error: 'Session non trouvée' });
        return;
      }

      res.json({ success: true, session });
    } catch (error) {
      res.status(500).json({ error: 'Erreur récupération session' });
    }
  }
}
```

### 5. Middleware

#### Validation Middleware
```typescript
import Joi from 'joi';

export const validateSessionData = (data: any) => {
  const schema = Joi.object({
    initials: Joi.string().min(1).max(10).required(),
    birthDate: Joi.date().required(),
    todayDate: Joi.date().required(),
    audioEnabled: Joi.boolean().required(),
    mode: Joi.string().valid('continuous', 'manual').required(),
  });

  return schema.validate(data);
};
```

#### Error Handling Middleware
```typescript
import { Request, Response, NextFunction } from 'express';

export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  console.error('Error:', error);
  
  res.status(500).json({
    success: false,
    error: 'Erreur interne du serveur',
    message: process.env.NODE_ENV === 'development' ? error.message : undefined,
  });
};
```

### 6. Configuration Docker

#### Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/questionnaire
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=questionnaire
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 🚀 Migration et Déploiement

### 1. Migration des Données

#### Script de Migration SQLite → PostgreSQL
```typescript
import { PrismaClient } from '@prisma/client';
import sqlite3 from 'sqlite3';

export class DataMigration {
  constructor(private prisma: PrismaClient) {}

  async migrateFromSQLite(sqlitePath: string): Promise<void> {
    const db = new sqlite3.Database(sqlitePath);
    
    // Migrer les sessions
    const sessions = await this.getSessionsFromSQLite(db);
    for (const session of sessions) {
      await this.prisma.session.create({
        data: {
          id: session.id,
          initials: session.initials,
          birthDate: new Date(session.birth_date),
          todayDate: new Date(session.today_date),
          mode: session.mode,
          audioEnabled: session.audio_enabled,
          createdAt: new Date(session.created_at),
          completedAt: session.completed_at ? new Date(session.completed_at) : null,
        },
      });
    }

    // Migrer les réponses
    const responses = await this.getResponsesFromSQLite(db);
    for (const response of responses) {
      await this.prisma.response.create({
        data: {
          sessionId: response.session_id,
          questionNum: response.question_num,
          questionText: response.question_text,
          score: response.score,
          responseText: response.response_text,
          transcript: response.transcript,
          responseType: response.response_type,
          timestamp: new Date(response.timestamp),
          confidence: response.confidence,
        },
      });
    }

    db.close();
  }

  private async getSessionsFromSQLite(db: sqlite3.Database): Promise<any[]> {
    return new Promise((resolve, reject) => {
      db.all('SELECT * FROM sessions', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  private async getResponsesFromSQLite(db: sqlite3.Database): Promise<any[]> {
    return new Promise((resolve, reject) => {
      db.all('SELECT * FROM responses', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }
}
```

### 2. Configuration Production

#### Variables d'Environnement
```bash
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/questionnaire

# Redis
REDIS_URL=redis://localhost:6379

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_API_KEY=your-api-key

# Application
NODE_ENV=production
PORT=3000
API_VERSION=1.0

# Sécurité
JWT_SECRET=your-jwt-secret
CORS_ORIGIN=https://your-frontend.com

# Audio
AUDIO_CACHE_BUCKET=questionnaire-audio-cache
AUDIO_CACHE_TTL=86400

# Logs
LOG_LEVEL=info
LOG_FORMAT=json
```

### 3. Monitoring et Observabilité

#### Health Check
```typescript
export const healthCheck = async (req: Request, res: Response): Promise<void> => {
  try {
    // Vérifier la base de données
    await prisma.$queryRaw`SELECT 1`;
    
    // Vérifier Redis
    await redis.ping();
    
    // Vérifier Google Cloud
    const ttsClient = new TextToSpeechClient();
    await ttsClient.listVoices();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'ok',
        redis: 'ok',
        googleCloud: 'ok',
      },
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
    });
  }
};
```

---

## 📚 Documentation API

### OpenAPI Specification
```yaml
openapi: 3.0.0
info:
  title: Questionnaire EORTC QLQ-C30 API
  version: 1.0.0
  description: API pour questionnaire médical avec reconnaissance vocale
  contact:
    name: Équipe Développement
    email: dev@questionnaire-eortc.com

servers:
  - url: https://api.questionnaire-eortc.com/v1
    description: Production
  - url: https://staging-api.questionnaire-eortc.com/v1
    description: Staging

paths:
  /sessions:
    post:
      summary: Créer une nouvelle session
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSessionRequest'
      responses:
        '201':
          description: Session créée
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateSessionResponse'
        '400':
          description: Données invalides
        '500':
          description: Erreur serveur

components:
  schemas:
    CreateSessionRequest:
      type: object
      required:
        - initials
        - birthDate
        - todayDate
        - audioEnabled
        - mode
      properties:
        initials:
          type: string
          minLength: 1
          maxLength: 10
          example: "A B"
        birthDate:
          type: string
          format: date
          example: "1970-01-01"
        todayDate:
          type: string
          format: date
          example: "2024-01-01"
        audioEnabled:
          type: boolean
          example: true
        mode:
          type: string
          enum: [continuous, manual]
          example: "continuous"
```

---

## 🧪 Tests et Qualité

### Tests Unitaires
```typescript
import { SessionService } from '../services/SessionService';
import { PrismaClient } from '@prisma/client';

describe('SessionService', () => {
  let sessionService: SessionService;
  let prisma: PrismaClient;

  beforeEach(() => {
    prisma = new PrismaClient();
    sessionService = new SessionService(prisma);
  });

  it('should create a session', async () => {
    const sessionData = {
      initials: 'A B',
      birthDate: '1970-01-01',
      todayDate: '2024-01-01',
      audioEnabled: true,
      mode: 'continuous' as const,
    };

    const session = await sessionService.createSession(sessionData);
    
    expect(session).toBeDefined();
    expect(session.initials).toBe('A B');
    expect(session.audioEnabled).toBe(true);
  });
});
```

### Tests d'Intégration
```typescript
import request from 'supertest';
import { app } from '../app';

describe('Session API', () => {
  it('should create a session via API', async () => {
    const sessionData = {
      initials: 'A B',
      birthDate: '1970-01-01',
      todayDate: '2024-01-01',
      audioEnabled: true,
      mode: 'continuous',
    };

    const response = await request(app)
      .post('/api/v1/sessions')
      .send(sessionData)
      .expect(201);

    expect(response.body.success).toBe(true);
    expect(response.body.sessionId).toBeDefined();
  });
});
```

---

## 🔒 Sécurité et Conformité

### 1. Authentification et Autorisation
```typescript
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';

export const authenticateToken = (req: Request, res: Response, next: NextFunction): void => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    res.status(401).json({ error: 'Token d\'authentification requis' });
    return;
  }

  jwt.verify(token, process.env.JWT_SECRET!, (err, user) => {
    if (err) {
      res.status(403).json({ error: 'Token invalide' });
      return;
    }
    req.user = user;
    next();
  });
};
```

### 2. Validation des Données
```typescript
import Joi from 'joi';

export const validateResponseData = (data: any) => {
  const schema = Joi.object({
    sessionId: Joi.string().uuid().required(),
    questionNum: Joi.number().integer().min(1).max(30).required(),
    score: Joi.number().integer().min(1).max(7).required(),
    responseType: Joi.string().valid('voice', 'manual').required(),
    transcript: Joi.string().optional(),
    confidence: Joi.number().min(0).max(1).optional(),
  });

  return schema.validate(data);
};
```

### 3. Conformité RGPD
```typescript
export class GDPRService {
  async anonymizeSession(sessionId: string): Promise<void> {
    await prisma.session.update({
      where: { id: sessionId },
      data: {
        initials: 'ANONYMIZED',
        metadata: null,
      },
    });
  }

  async deleteSession(sessionId: string): Promise<void> {
    await prisma.response.deleteMany({
      where: { sessionId },
    });
    
    await prisma.session.delete({
      where: { id: sessionId },
    });
  }

  async exportSessionData(sessionId: string): Promise<any> {
    const session = await prisma.session.findUnique({
      where: { id: sessionId },
      include: { responses: true },
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
        completedAt: session.completedAt,
      },
      responses: session.responses.map(response => ({
        questionNum: response.questionNum,
        score: response.score,
        responseText: response.responseText,
        responseType: response.responseType,
        timestamp: response.timestamp,
      })),
    };
  }
}
```

---

## 📈 Performance et Monitoring

### 1. Métriques de Performance
```typescript
import { performance } from 'perf_hooks';

export const performanceMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const start = performance.now();
  
  res.on('finish', () => {
    const duration = performance.now() - start;
    console.log(`${req.method} ${req.path} - ${res.statusCode} - ${duration.toFixed(2)}ms`);
  });
  
  next();
};
```

### 2. Cache Redis
```typescript
import Redis from 'redis';

export class CacheService {
  private redis: Redis.RedisClientType;

  constructor() {
    this.redis = Redis.createClient({
      url: process.env.REDIS_URL,
    });
  }

  async get(key: string): Promise<string | null> {
    return await this.redis.get(key);
  }

  async set(key: string, value: string, ttl: number = 3600): Promise<void> {
    await this.redis.setEx(key, ttl, value);
  }

  async getAudioCache(hash: string): Promise<Buffer | null> {
    const cached = await this.redis.get(`audio:${hash}`);
    return cached ? Buffer.from(cached, 'base64') : null;
  }

  async setAudioCache(hash: string, audio: Buffer, ttl: number = 86400): Promise<void> {
    await this.redis.setEx(`audio:${hash}`, ttl, audio.toString('base64'));
  }
}
```

---

## 🚀 Déploiement et CI/CD

### 1. GitHub Actions
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test
      - run: npm run test:coverage

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - run: docker build -t questionnaire-api .

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Production
        run: |
          # Déploiement vers Kubernetes
          kubectl apply -f k8s/
```

### 2. Configuration Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: questionnaire-api
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
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
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
```

---

## 📞 Support et Maintenance

### 1. Documentation Technique
- **API Documentation** : Swagger/OpenAPI
- **Architecture Decision Records** : ADR dans `/docs/adr/`
- **Runbooks** : Procédures opérationnelles
- **Troubleshooting Guide** : Guide de dépannage

### 2. Monitoring et Alertes
```typescript
import { createLogger, format, transports } from 'winston';

export const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  transports: [
    new transports.File({ filename: 'error.log', level: 'error' }),
    new transports.File({ filename: 'combined.log' }),
    new transports.Console({
      format: format.simple()
    })
  ]
});
```

### 3. Métriques Business
```typescript
export class AnalyticsService {
  async getSessionMetrics(): Promise<SessionMetrics> {
    const totalSessions = await prisma.session.count();
    const completedSessions = await prisma.session.count({
      where: { completedAt: { not: null } }
    });
    const averageCompletionTime = await prisma.session.aggregate({
      _avg: {
        completedAt: true,
        createdAt: true
      }
    });

    return {
      totalSessions,
      completedSessions,
      completionRate: (completedSessions / totalSessions) * 100,
      averageCompletionTime: averageCompletionTime._avg
    };
  }
}
```

---

## 🎯 Conclusion

Cette documentation fournit une base solide pour l'intégration du POC Flask vers un environnement Node.js/TypeScript. L'architecture proposée maintient les fonctionnalités existantes tout en améliorant la scalabilité, la maintenabilité et les performances.

### Points Clés pour l'Équipe
1. **Migration progressive** : Commencer par l'API, puis le frontend
2. **Tests complets** : Unitaires, intégration, et end-to-end
3. **Monitoring** : Métriques, logs, et alertes
4. **Sécurité** : Authentification, validation, et conformité RGPD
5. **Performance** : Cache, optimisation, et scalabilité

### Prochaines Étapes
1. **Setup** de l'environnement de développement
2. **Migration** des données existantes
3. **Implémentation** des services principaux
4. **Tests** et validation
5. **Déploiement** en production

Pour toute question technique, référez-vous à cette documentation ou contactez l'équipe de développement.
