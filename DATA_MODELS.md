# 📊 Modèles de Données - Questionnaire EORTC QLQ-C30

## 🎯 Vue d'ensemble

Ce document décrit les modèles de données utilisés dans l'application questionnaire EORTC QLQ-C30, incluant les schémas de base de données, les types TypeScript, et les relations entre entités.

---

## 🗄️ Schéma de Base de Données

### PostgreSQL avec Prisma ORM

```prisma
// schema.prisma
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
  @@index([category])
}

model AudioCache {
  id        String   @id @default(uuid())
  hash      String   @unique
  text      String
  voice     String
  speed     Float    @default(1.0)
  format    String   @default("wav")
  size      Int
  duration  Float
  createdAt DateTime @default(now())
  expiresAt DateTime?
  
  @@map("audio_cache")
  @@index([hash])
  @@index([expiresAt])
}

model Export {
  id          String    @id @default(uuid())
  sessionId   String?
  format      ExportFormat
  status      ExportStatus
  downloadUrl String?
  expiresAt   DateTime?
  createdAt   DateTime @default(now())
  completedAt DateTime?
  metadata    Json?
  
  @@map("exports")
  @@index([sessionId])
  @@index([status])
  @@index([expiresAt])
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

enum ExportFormat {
  JSON
  CSV
  EXCEL
  PDF
}

enum ExportStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
}
```

---

## 🔧 Types TypeScript

### Types de Base

```typescript
// types/common.ts
export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt?: Date;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any[];
  };
  metadata?: {
    timestamp: string;
    version: string;
    requestId: string;
  };
}
```

### Modèles de Session

```typescript
// types/session.ts
export interface Session extends BaseEntity {
  id: string;
  initials: string;
  birthDate: Date;
  todayDate: Date;
  mode: SessionMode;
  audioEnabled: boolean;
  createdAt: Date;
  completedAt?: Date;
  metadata?: SessionMetadata;
  responses?: Response[];
}

export interface SessionMetadata {
  browser?: string;
  device?: string;
  location?: string;
  userAgent?: string;
  ipAddress?: string;
  referrer?: string;
}

export interface CreateSessionRequest {
  initials: string;
  birthDate: string; // ISO 8601
  todayDate: string; // ISO 8601
  audioEnabled: boolean;
  mode: SessionMode;
  metadata?: SessionMetadata;
}

export interface UpdateSessionRequest {
  initials?: string;
  audioEnabled?: boolean;
  metadata?: SessionMetadata;
}

export interface SessionStatistics {
  totalQuestions: number;
  answered: number;
  missed: number;
  completionRate: number;
  averageScore?: number;
  duration?: number; // en minutes
  responseTypes: {
    voice: number;
    manual: number;
  };
  categories: {
    [category: string]: {
      average: number;
      questions: number[];
    };
  };
}

export enum SessionMode {
  CONTINUOUS = 'continuous',
  MANUAL = 'manual'
}
```

### Modèles de Question

```typescript
// types/question.ts
export interface Question {
  id: number;
  questionNum: number;
  text: string;
  scale: QuestionScale;
  options: string[];
  speechText: string;
  isTestQuestion: boolean;
  category?: string;
}

export interface QuestionWithAudio extends Question {
  audioUrl?: string;
  audioDuration?: number;
  audioSize?: number;
}

export interface CreateQuestionRequest {
  questionNum: number;
  text: string;
  scale: QuestionScale;
  options: string[];
  speechText: string;
  isTestQuestion?: boolean;
  category?: string;
}

export interface UpdateQuestionRequest {
  text?: string;
  scale?: QuestionScale;
  options?: string[];
  speechText?: string;
  isTestQuestion?: boolean;
  category?: string;
}

export enum QuestionScale {
  TEST = 'test',
  SCALE_1_4 = '1-4',
  SCALE_1_7 = '1-7'
}

export interface QuestionCategory {
  name: string;
  description: string;
  questions: number[];
  weight?: number;
}
```

### Modèles de Réponse

```typescript
// types/response.ts
export interface Response {
  id: number;
  sessionId: string;
  questionNum: number;
  questionText: string;
  score: number;
  responseText: string;
  transcript?: string;
  responseType: ResponseType;
  timestamp: Date;
  confidence?: number;
}

export interface CreateResponseRequest {
  sessionId: string;
  questionNum: number;
  score: number;
  responseType: ResponseType;
  transcript?: string;
  confidence?: number;
  timestamp?: string; // ISO 8601
}

export interface UpdateResponseRequest {
  score?: number;
  responseText?: string;
  transcript?: string;
  confidence?: number;
}

export interface ResponseWithQuestion extends Response {
  question: Question;
}

export interface ResponseStatistics {
  total: number;
  byType: {
    voice: number;
    manual: number;
  };
  byScore: {
    [score: number]: number;
  };
  averageConfidence: number;
  averageResponseTime: number; // en secondes
}

export enum ResponseType {
  VOICE = 'voice',
  MANUAL = 'manual'
}
```

### Modèles d'Audio

```typescript
// types/audio.ts
export interface AudioCache {
  id: string;
  hash: string;
  text: string;
  voice: string;
  speed: number;
  format: string;
  size: number;
  duration: number;
  createdAt: Date;
  expiresAt?: Date;
}

export interface GenerateAudioRequest {
  text: string;
  voice?: string;
  speed?: number;
  format?: string;
  cache?: boolean;
}

export interface GenerateAudioResponse {
  success: boolean;
  audioUrl?: string;
  hash?: string;
  duration: number;
  size: number;
  cached: boolean;
}

export interface AudioVoice {
  name: string;
  languageCode: string;
  gender: 'MALE' | 'FEMALE' | 'NEUTRAL';
  quality: 'STANDARD' | 'NEURAL' | 'WAVENET';
}

export interface AudioConfig {
  defaultVoice: string;
  defaultSpeed: number;
  defaultFormat: string;
  cacheEnabled: boolean;
  cacheTTL: number; // en secondes
  maxFileSize: number; // en bytes
  supportedFormats: string[];
  supportedVoices: AudioVoice[];
}
```

### Modèles de Reconnaissance Vocale

```typescript
// types/speech.ts
export interface TranscribeRequest {
  audio: File | Buffer;
  language: string;
  sessionId: string;
  config?: SpeechConfig;
}

export interface TranscribeResponse {
  success: boolean;
  transcript: string;
  confidence: number;
  alternatives: string[];
  language: string;
  duration: number;
  error?: string;
}

export interface InterpretRequest {
  transcript: string;
  questionNum: number;
  sessionId: string;
  context?: string;
}

export interface InterpretResponse {
  success: boolean;
  score?: number;
  responseText?: string;
  confidence?: number;
  suggestions?: string[];
  error?: string;
}

export interface SpeechConfig {
  languageCode: string;
  sampleRateHertz: number;
  encoding: string;
  enableAutomaticPunctuation: boolean;
  enableWordTimeOffsets: boolean;
  enableWordConfidence: boolean;
  useEnhanced: boolean;
  model: string;
}

export interface SpeechStatistics {
  totalRequests: number;
  averageConfidence: number;
  averageTranscriptionTime: number;
  errorRate: number;
  byLanguage: {
    [language: string]: number;
  };
}
```

### Modèles d'Export

```typescript
// types/export.ts
export interface Export {
  id: string;
  sessionId?: string;
  format: ExportFormat;
  status: ExportStatus;
  downloadUrl?: string;
  expiresAt?: Date;
  createdAt: Date;
  completedAt?: Date;
  metadata?: ExportMetadata;
}

export interface CreateExportRequest {
  sessionId?: string;
  sessionIds?: string[];
  format: ExportFormat;
  includeAudio?: boolean;
  includeMetadata?: boolean;
  filters?: ExportFilters;
}

export interface ExportMetadata {
  totalSessions: number;
  totalResponses: number;
  fileSize: number;
  generatedAt: Date;
  requestedBy: string;
}

export interface ExportFilters {
  from?: Date;
  to?: Date;
  status?: string[];
  completionRate?: {
    min: number;
    max: number;
  };
  averageScore?: {
    min: number;
    max: number;
  };
}

export interface ExportStatus {
  id: string;
  status: ExportStatus;
  progress: number;
  downloadUrl?: string;
  expiresAt?: Date;
  error?: string;
}

export enum ExportFormat {
  JSON = 'json',
  CSV = 'csv',
  EXCEL = 'excel',
  PDF = 'pdf'
}

export enum ExportStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}
```

### Modèles de Statistiques

```typescript
// types/statistics.ts
export interface GlobalStatistics {
  period: {
    from: Date;
    to: Date;
  };
  sessions: {
    total: number;
    completed: number;
    inProgress: number;
    completionRate: number;
  };
  responses: {
    total: number;
    averagePerSession: number;
    voiceResponses: number;
    manualResponses: number;
  };
  scores: {
    average: number;
    median: number;
    distribution: {
      [score: number]: number;
    };
  };
  categories: {
    [category: string]: {
      average: number;
      questions: number[];
    };
  };
  performance: {
    averageSessionDuration: number;
    averageResponseTime: number;
    audioCacheHitRate: number;
    speechRecognitionAccuracy: number;
  };
}

export interface SessionStatistics {
  session: {
    id: string;
    initials: string;
    createdAt: Date;
    completedAt?: Date;
    duration?: number;
  };
  completion: {
    totalQuestions: number;
    answered: number;
    missed: number;
    completionRate: number;
  };
  scores: {
    average: number;
    median: number;
    min: number;
    max: number;
    distribution: {
      [score: number]: number;
    };
  };
  categories: {
    [category: string]: {
      average: number;
      questions: number[];
    };
  };
  responseTypes: {
    voice: number;
    manual: number;
  };
}

export interface CategoryStatistics {
  name: string;
  description: string;
  questions: number[];
  average: number;
  median: number;
  distribution: {
    [score: number]: number;
  };
  trends: {
    period: string;
    average: number;
  }[];
}
```

---

## 🔗 Relations et Contraintes

### Relations Principales

```typescript
// Relations entre entités
export interface SessionWithResponses extends Session {
  responses: Response[];
  statistics: SessionStatistics;
}

export interface ResponseWithSession extends Response {
  session: Session;
}

export interface ResponseWithQuestion extends Response {
  question: Question;
}

export interface CompleteSessionData extends Session {
  responses: ResponseWithQuestion[];
  statistics: SessionStatistics;
  audioCache: AudioCache[];
  exports: Export[];
}
```

### Contraintes de Validation

```typescript
// Contraintes de validation
export interface ValidationConstraints {
  session: {
    initials: {
      minLength: 1;
      maxLength: 10;
      pattern: /^[A-Z\s]+$/;
    };
    birthDate: {
      min: '1900-01-01';
      max: 'today';
    };
    todayDate: {
      min: '1900-01-01';
      max: 'today';
    };
  };
  response: {
    score: {
      min: 1;
      max: 7;
    };
    questionNum: {
      min: 0;
      max: 30;
    };
    confidence: {
      min: 0;
      max: 1;
    };
  };
  question: {
    questionNum: {
      min: 0;
      max: 30;
      unique: true;
    };
    options: {
      minLength: 2;
      maxLength: 10;
    };
  };
}
```

---

## 📊 Index et Optimisations

### Index de Base de Données

```sql
-- Index pour les sessions
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_completed_at ON sessions(completed_at);
CREATE INDEX idx_sessions_mode ON sessions(mode);
CREATE INDEX idx_sessions_audio_enabled ON sessions(audio_enabled);

-- Index pour les réponses
CREATE INDEX idx_responses_session_id ON responses(session_id);
CREATE INDEX idx_responses_question_num ON responses(question_num);
CREATE INDEX idx_responses_timestamp ON responses(timestamp);
CREATE INDEX idx_responses_response_type ON responses(response_type);
CREATE INDEX idx_responses_score ON responses(score);

-- Index composite pour les requêtes fréquentes
CREATE INDEX idx_responses_session_question ON responses(session_id, question_num);
CREATE INDEX idx_responses_session_timestamp ON responses(session_id, timestamp);

-- Index pour les questions
CREATE INDEX idx_questions_question_num ON questions(question_num);
CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_scale ON questions(scale);

-- Index pour le cache audio
CREATE INDEX idx_audio_cache_hash ON audio_cache(hash);
CREATE INDEX idx_audio_cache_expires_at ON audio_cache(expires_at);
CREATE INDEX idx_audio_cache_created_at ON audio_cache(created_at);

-- Index pour les exports
CREATE INDEX idx_exports_session_id ON exports(session_id);
CREATE INDEX idx_exports_status ON exports(status);
CREATE INDEX idx_exports_expires_at ON exports(expires_at);
```

### Optimisations de Requêtes

```typescript
// Requêtes optimisées avec Prisma
export class OptimizedQueries {
  // Récupérer une session avec ses réponses (optimisé)
  static async getSessionWithResponses(sessionId: string) {
    return await prisma.session.findUnique({
      where: { id: sessionId },
      include: {
        responses: {
          orderBy: { questionNum: 'asc' }
        }
      }
    });
  }

  // Statistiques d'une session (optimisé)
  static async getSessionStatistics(sessionId: string) {
    const [session, responses] = await Promise.all([
      prisma.session.findUnique({
        where: { id: sessionId },
        select: {
          id: true,
          initials: true,
          createdAt: true,
          completedAt: true
        }
      }),
      prisma.response.findMany({
        where: { sessionId },
        select: {
          questionNum: true,
          score: true,
          responseType: true,
          timestamp: true
        }
      })
    ]);

    return this.calculateStatistics(session, responses);
  }

  // Recherche de sessions avec pagination (optimisé)
  static async searchSessions(params: SearchSessionsParams) {
    const { page = 1, limit = 10, q, status, from, to } = params;
    const skip = (page - 1) * limit;

    const where: any = {};
    
    if (q) {
      where.initials = { contains: q, mode: 'insensitive' };
    }
    
    if (status === 'completed') {
      where.completedAt = { not: null };
    } else if (status === 'in_progress') {
      where.completedAt = null;
    }
    
    if (from || to) {
      where.createdAt = {};
      if (from) where.createdAt.gte = from;
      if (to) where.createdAt.lte = to;
    }

    const [sessions, total] = await Promise.all([
      prisma.session.findMany({
        where,
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
      prisma.session.count({ where })
    ]);

    return {
      sessions,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
        hasNext: page * limit < total,
        hasPrev: page > 1
      }
    };
  }
}
```

---

## 🔄 Migration des Données

### Script de Migration SQLite → PostgreSQL

```typescript
// migration/sqlite-to-postgresql.ts
export class DataMigration {
  constructor(
    private sqliteDb: sqlite3.Database,
    private prisma: PrismaClient
  ) {}

  async migrateAll(): Promise<void> {
    console.log('🚀 Début de la migration SQLite → PostgreSQL');
    
    await this.migrateSessions();
    await this.migrateResponses();
    await this.migrateQuestions();
    
    console.log('✅ Migration terminée avec succès');
  }

  private async migrateSessions(): Promise<void> {
    console.log('📊 Migration des sessions...');
    
    const sessions = await this.getSessionsFromSQLite();
    
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
      } catch (error) {
        console.error(`❌ Erreur migration session ${session.id}:`, error);
      }
    }
    
    console.log(`✅ ${sessions.length} sessions migrées`);
  }

  private async migrateResponses(): Promise<void> {
    console.log('💬 Migration des réponses...');
    
    const responses = await this.getResponsesFromSQLite();
    
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
      } catch (error) {
        console.error(`❌ Erreur migration réponse ${response.id}:`, error);
      }
    }
    
    console.log(`✅ ${responses.length} réponses migrées`);
  }

  private async migrateQuestions(): Promise<void> {
    console.log('❓ Migration des questions...');
    
    const questions = await this.getQuestionsFromSQLite();
    
    for (const question of questions) {
      try {
        await this.prisma.question.create({
          data: {
            questionNum: question.question_num,
            text: question.text,
            scale: this.mapQuestionScale(question.scale),
            options: JSON.parse(question.options),
            speechText: question.speech_text,
            isTestQuestion: Boolean(question.is_test_question),
            category: question.category
          }
        });
      } catch (error) {
        console.error(`❌ Erreur migration question ${question.id}:`, error);
      }
    }
    
    console.log(`✅ ${questions.length} questions migrées`);
  }

  private mapSessionMode(mode: string): SessionMode {
    switch (mode) {
      case 'Continu (Web Speech)':
      case 'continuous':
        return SessionMode.CONTINUOUS;
      case 'Standard':
      case 'manual':
        return SessionMode.MANUAL;
      default:
        return SessionMode.MANUAL;
    }
  }

  private mapResponseType(type: string): ResponseType {
    switch (type) {
      case 'voice':
        return ResponseType.VOICE;
      case 'manual':
        return ResponseType.MANUAL;
      default:
        return ResponseType.MANUAL;
    }
  }

  private mapQuestionScale(scale: string): QuestionScale {
    switch (scale) {
      case 'test':
        return QuestionScale.TEST;
      case '1-4':
        return QuestionScale.SCALE_1_4;
      case '1-7':
        return QuestionScale.SCALE_1_7;
      default:
        return QuestionScale.SCALE_1_4;
    }
  }

  private parseMetadata(metadata: string): any {
    try {
      return metadata ? JSON.parse(metadata) : null;
    } catch {
      return null;
    }
  }
}
```

---

## 🧪 Tests des Modèles

### Tests Unitaires

```typescript
// tests/models/session.test.ts
describe('Session Model', () => {
  it('should create a session with valid data', async () => {
    const sessionData = {
      initials: 'A B',
      birthDate: new Date('1970-01-01'),
      todayDate: new Date('2024-01-15'),
      mode: SessionMode.CONTINUOUS,
      audioEnabled: true
    };

    const session = await prisma.session.create({
      data: sessionData
    });

    expect(session).toBeDefined();
    expect(session.initials).toBe('A B');
    expect(session.mode).toBe(SessionMode.CONTINUOUS);
    expect(session.audioEnabled).toBe(true);
  });

  it('should validate initials format', async () => {
    const invalidData = {
      initials: 'a b', // lowercase
      birthDate: new Date('1970-01-01'),
      todayDate: new Date('2024-01-15'),
      mode: SessionMode.CONTINUOUS,
      audioEnabled: true
    };

    await expect(
      prisma.session.create({ data: invalidData })
    ).rejects.toThrow();
  });
});

// tests/models/response.test.ts
describe('Response Model', () => {
  it('should create a response with valid data', async () => {
    const session = await createTestSession();
    
    const responseData = {
      sessionId: session.id,
      questionNum: 1,
      questionText: 'Test question',
      score: 3,
      responseText: 'Plutôt',
      responseType: ResponseType.VOICE,
      transcript: 'plutôt',
      confidence: 0.95
    };

    const response = await prisma.response.create({
      data: responseData
    });

    expect(response).toBeDefined();
    expect(response.score).toBe(3);
    expect(response.responseType).toBe(ResponseType.VOICE);
  });

  it('should enforce unique session-question constraint', async () => {
    const session = await createTestSession();
    
    const responseData = {
      sessionId: session.id,
      questionNum: 1,
      questionText: 'Test question',
      score: 3,
      responseText: 'Plutôt',
      responseType: ResponseType.VOICE
    };

    // Créer la première réponse
    await prisma.response.create({ data: responseData });

    // Tenter de créer une deuxième réponse pour la même question
    await expect(
      prisma.response.create({ data: responseData })
    ).rejects.toThrow();
  });
});
```

### Tests d'Intégration

```typescript
// tests/integration/session-responses.test.ts
describe('Session-Responses Integration', () => {
  it('should calculate session statistics correctly', async () => {
    const session = await createTestSession();
    
    // Créer des réponses de test
    await createTestResponses(session.id, [
      { questionNum: 1, score: 3 },
      { questionNum: 2, score: 2 },
      { questionNum: 3, score: 4 }
    ]);

    const statistics = await calculateSessionStatistics(session.id);

    expect(statistics.completion.answered).toBe(3);
    expect(statistics.completion.totalQuestions).toBe(30);
    expect(statistics.completion.completionRate).toBe(10);
    expect(statistics.scores.average).toBe(3);
  });

  it('should handle session completion correctly', async () => {
    const session = await createTestSession();
    
    // Marquer la session comme terminée
    await prisma.session.update({
      where: { id: session.id },
      data: { completedAt: new Date() }
    });

    const updatedSession = await prisma.session.findUnique({
      where: { id: session.id }
    });

    expect(updatedSession?.completedAt).toBeDefined();
  });
});
```

---

## 📈 Performance et Monitoring

### Métriques de Performance

```typescript
// monitoring/performance.ts
export class PerformanceMonitor {
  static async measureQueryPerformance<T>(
    queryName: string,
    query: () => Promise<T>
  ): Promise<T> {
    const start = performance.now();
    
    try {
      const result = await query();
      const duration = performance.now() - start;
      
      console.log(`📊 Query ${queryName}: ${duration.toFixed(2)}ms`);
      
      // Envoyer les métriques à votre système de monitoring
      await this.sendMetrics(queryName, duration, true);
      
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      
      console.error(`❌ Query ${queryName} failed: ${duration.toFixed(2)}ms`);
      
      await this.sendMetrics(queryName, duration, false);
      
      throw error;
    }
  }

  private static async sendMetrics(
    queryName: string,
    duration: number,
    success: boolean
  ): Promise<void> {
    // Intégration avec votre système de monitoring (DataDog, New Relic, etc.)
    // await monitoringClient.increment('database.queries', 1, { query: queryName });
    // await monitoringClient.histogram('database.query.duration', duration, { query: queryName });
    // await monitoringClient.increment('database.query.success', success ? 1 : 0, { query: queryName });
  }
}
```

### Optimisations de Requêtes

```typescript
// optimizations/query-optimizations.ts
export class QueryOptimizations {
  // Requête optimisée pour récupérer les statistiques
  static async getOptimizedSessionStatistics(sessionId: string) {
    return await PerformanceMonitor.measureQueryPerformance(
      'getSessionStatistics',
      async () => {
        const [session, responses, totalResponses] = await Promise.all([
          prisma.session.findUnique({
            where: { id: sessionId },
            select: {
              id: true,
              initials: true,
              createdAt: true,
              completedAt: true
            }
          }),
          prisma.response.findMany({
            where: { sessionId },
            select: {
              questionNum: true,
              score: true,
              responseType: true,
              timestamp: true
            }
          }),
          prisma.response.count({
            where: { sessionId }
          })
        ]);

        return this.calculateStatistics(session, responses, totalResponses);
      }
    );
  }

  // Requête optimisée pour la recherche de sessions
  static async getOptimizedSessionSearch(params: SearchParams) {
    return await PerformanceMonitor.measureQueryPerformance(
      'searchSessions',
      async () => {
        const { page = 1, limit = 10, ...filters } = params;
        const skip = (page - 1) * limit;

        const where = this.buildWhereClause(filters);

        const [sessions, total] = await Promise.all([
          prisma.session.findMany({
            where,
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
          prisma.session.count({ where })
        ]);

        return {
          sessions,
          pagination: this.buildPagination(page, limit, total)
        };
      }
    );
  }
}
```

---

## 🔒 Sécurité et Validation

### Validation des Données

```typescript
// validation/data-validation.ts
export class DataValidation {
  static validateSession(data: any): CreateSessionRequest {
    const schema = Joi.object({
      initials: Joi.string()
        .min(1)
        .max(10)
        .pattern(/^[A-Z\s]+$/)
        .required(),
      birthDate: Joi.date()
        .max('now')
        .min('1900-01-01')
        .required(),
      todayDate: Joi.date()
        .max('now')
        .min('1900-01-01')
        .required(),
      audioEnabled: Joi.boolean().required(),
      mode: Joi.string()
        .valid('continuous', 'manual')
        .required(),
      metadata: Joi.object().optional()
    });

    const { error, value } = schema.validate(data);
    if (error) {
      throw new ValidationError('Données de session invalides', error.details);
    }

    return value;
  }

  static validateResponse(data: any): CreateResponseRequest {
    const schema = Joi.object({
      sessionId: Joi.string().uuid().required(),
      questionNum: Joi.number().integer().min(0).max(30).required(),
      score: Joi.number().integer().min(1).max(7).required(),
      responseType: Joi.string().valid('voice', 'manual').required(),
      transcript: Joi.string().optional(),
      confidence: Joi.number().min(0).max(1).optional(),
      timestamp: Joi.date().optional()
    });

    const { error, value } = schema.validate(data);
    if (error) {
      throw new ValidationError('Données de réponse invalides', error.details);
    }

    return value;
  }
}
```

### Audit et Logging

```typescript
// audit/data-audit.ts
export class DataAudit {
  static async logSessionCreation(session: Session, metadata: any): Promise<void> {
    await this.logEvent('session.created', {
      sessionId: session.id,
      initials: session.initials,
      mode: session.mode,
      audioEnabled: session.audioEnabled,
      metadata
    });
  }

  static async logResponseCreation(response: Response, metadata: any): Promise<void> {
    await this.logEvent('response.created', {
      responseId: response.id,
      sessionId: response.sessionId,
      questionNum: response.questionNum,
      score: response.score,
      responseType: response.responseType,
      confidence: response.confidence,
      metadata
    });
  }

  static async logDataExport(exportData: Export, metadata: any): Promise<void> {
    await this.logEvent('export.created', {
      exportId: exportData.id,
      sessionId: exportData.sessionId,
      format: exportData.format,
      metadata
    });
  }

  private static async logEvent(eventType: string, data: any): Promise<void> {
    // Intégration avec votre système de logging
    console.log(`📝 Audit: ${eventType}`, data);
    
    // Envoyer vers votre système de logging centralisé
    // await loggingClient.info(eventType, data);
  }
}
```

---

## 📚 Documentation des Modèles

### Documentation Automatique

```typescript
// docs/model-documentation.ts
export class ModelDocumentation {
  static generateModelDocs(): string {
    return `
# 📊 Documentation des Modèles de Données

## 🏥 Session
- **Description** : Représente une session de questionnaire pour un patient
- **Clé primaire** : \`id\` (UUID)
- **Relations** : One-to-Many avec \`Response\`
- **Index** : \`createdAt\`, \`completedAt\`, \`mode\`

## 💬 Response  
- **Description** : Représente une réponse à une question
- **Clé primaire** : \`id\` (Auto-increment)
- **Clé étrangère** : \`sessionId\` → \`Session.id\`
- **Contraintes** : Unique \`(sessionId, questionNum)\`

## ❓ Question
- **Description** : Représente une question du questionnaire EORTC
- **Clé primaire** : \`id\` (Auto-increment)
- **Index unique** : \`questionNum\`
- **Échelles** : \`test\`, \`1-4\`, \`1-7\`

## 🔊 AudioCache
- **Description** : Cache des fichiers audio générés
- **Clé primaire** : \`id\` (UUID)
- **Index unique** : \`hash\`
- **TTL** : Expiration automatique

## 📤 Export
- **Description** : Exports de données générés
- **Clé primaire** : \`id\` (UUID)
- **Statuts** : \`pending\`, \`processing\`, \`completed\`, \`failed\`
    `;
  }
}
```

---

*Cette documentation des modèles de données est maintenue à jour avec les dernières évolutions de l'API. Pour toute question sur les modèles, contactez l'équipe de développement.*
