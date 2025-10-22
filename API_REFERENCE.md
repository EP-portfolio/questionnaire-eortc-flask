# 📚 API Reference - Questionnaire EORTC QLQ-C30

## 🔗 Base URL
```
Production: https://api.questionnaire-eortc.com/v1
Staging:    https://staging-api.questionnaire-eortc.com/v1
Local:      http://localhost:3000/api/v1
```

## 🔐 Authentification

### Headers Requis
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-API-Version: 1.0
X-Client-Version: 1.0.0
```

### Obtenir un Token
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Réponse:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "user": {
    "id": "user-123",
    "email": "user@example.com",
    "role": "admin"
  }
}
```

---

## 📊 Endpoints Principaux

### 🏥 Sessions

#### Créer une Session
```http
POST /sessions
```

**Request Body:**
```typescript
interface CreateSessionRequest {
  initials: string;           // Initiales patient (1-10 caractères)
  birthDate: string;          // Date naissance (ISO 8601)
  todayDate: string;          // Date questionnaire (ISO 8601)
  audioEnabled: boolean;      // Audio activé
  mode: 'continuous' | 'manual'; // Mode de réponse
  metadata?: {               // Données additionnelles
    browser?: string;
    device?: string;
    location?: string;
  };
}
```

**Exemple:**
```json
{
  "initials": "A B",
  "birthDate": "1970-01-01",
  "todayDate": "2024-01-15",
  "audioEnabled": true,
  "mode": "continuous",
  "metadata": {
    "browser": "Chrome 120.0",
    "device": "desktop"
  }
}
```

**Réponse:**
```json
{
  "success": true,
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session créée avec succès",
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "initials": "A B",
    "birthDate": "1970-01-01T00:00:00.000Z",
    "todayDate": "2024-01-15T00:00:00.000Z",
    "mode": "continuous",
    "audioEnabled": true,
    "createdAt": "2024-01-15T10:30:00.000Z",
    "completedAt": null
  }
}
```

#### Récupérer une Session
```http
GET /sessions/{sessionId}
```

**Réponse:**
```json
{
  "success": true,
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "initials": "A B",
    "birthDate": "1970-01-01T00:00:00.000Z",
    "todayDate": "2024-01-15T00:00:00.000Z",
    "mode": "continuous",
    "audioEnabled": true,
    "createdAt": "2024-01-15T10:30:00.000Z",
    "completedAt": "2024-01-15T11:15:00.000Z",
    "responses": [
      {
        "id": 1,
        "questionNum": 1,
        "questionText": "Avez-vous des difficultés à faire certains efforts physiques...",
        "score": 3,
        "responseText": "Plutôt",
        "transcript": "plutôt",
        "responseType": "voice",
        "timestamp": "2024-01-15T10:32:00.000Z",
        "confidence": 0.95
      }
    ],
    "statistics": {
      "totalQuestions": 30,
      "answered": 30,
      "missed": 0,
      "completionRate": 100.0,
      "averageScore": 2.8,
      "duration": 45
    }
  }
}
```

#### Finaliser une Session
```http
PUT /sessions/{sessionId}/complete
```

**Réponse:**
```json
{
  "success": true,
  "message": "Session marquée comme terminée",
  "completedAt": "2024-01-15T11:15:00.000Z"
}
```

#### Lister les Sessions
```http
GET /sessions?page=1&limit=10&status=completed
```

**Query Parameters:**
- `page` (number): Numéro de page (défaut: 1)
- `limit` (number): Nombre d'éléments par page (défaut: 10, max: 100)
- `status` (string): `all`, `completed`, `in_progress`
- `from` (string): Date de début (ISO 8601)
- `to` (string): Date de fin (ISO 8601)

**Réponse:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "initials": "A B",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "completedAt": "2024-01-15T11:15:00.000Z",
      "completionRate": 100.0,
      "responseCount": 30
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 150,
    "totalPages": 15,
    "hasNext": true,
    "hasPrev": false
  }
}
```

---

### ❓ Questions

#### Récupérer une Question
```http
GET /questions/{questionId}
```

**Réponse:**
```json
{
  "success": true,
  "question": {
    "id": 1,
    "questionNum": 1,
    "text": "Avez-vous des difficultés à faire certains efforts physiques pénibles comme porter un sac à provisions chargé ou une valise?",
    "scale": "1-4",
    "options": [
      "Pas du tout",
      "Un peu", 
      "Plutôt",
      "Beaucoup"
    ],
    "speechText": "Question 1. Avez-vous des difficultés à faire certains efforts physiques pénibles comme porter un sac à provisions chargé ou une valise? Répondez par Pas du tout, Un peu, Plutôt, ou Beaucoup",
    "isTestQuestion": false,
    "category": "physical_functioning"
  }
}
```

#### Lister toutes les Questions
```http
GET /questions
```

**Réponse:**
```json
{
  "success": true,
  "questions": [
    {
      "id": 0,
      "questionNum": 0,
      "text": "Question 0 - Tests préalables",
      "scale": "test",
      "options": ["Test audio réussi", "Microphone validé"],
      "speechText": "Question zéro. Tests audio et microphone...",
      "isTestQuestion": true,
      "category": "test"
    },
    {
      "id": 1,
      "questionNum": 1,
      "text": "Avez-vous des difficultés à faire certains efforts physiques...",
      "scale": "1-4",
      "options": ["Pas du tout", "Un peu", "Plutôt", "Beaucoup"],
      "speechText": "Question 1. Avez-vous des difficultés...",
      "isTestQuestion": false,
      "category": "physical_functioning"
    }
  ],
  "total": 31
}
```

---

### 💬 Réponses

#### Sauvegarder une Réponse
```http
POST /responses
```

**Request Body:**
```typescript
interface SaveResponseRequest {
  sessionId: string;          // UUID de la session
  questionNum: number;        // Numéro question (1-30)
  score: number;              // Score réponse (1-4 ou 1-7)
  responseType: 'voice' | 'manual'; // Type de réponse
  transcript?: string;       // Transcription vocale
  confidence?: number;        // Confiance (0-1)
  timestamp?: string;         // Timestamp personnalisé
}
```

**Exemple:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "questionNum": 1,
  "score": 3,
  "responseType": "voice",
  "transcript": "plutôt",
  "confidence": 0.95
}
```

**Réponse:**
```json
{
  "success": true,
  "responseId": 123,
  "nextQuestion": 2,
  "isComplete": false,
  "response": {
    "id": 123,
    "sessionId": "550e8400-e29b-41d4-a716-446655440000",
    "questionNum": 1,
    "questionText": "Avez-vous des difficultés à faire certains efforts physiques...",
    "score": 3,
    "responseText": "Plutôt",
    "transcript": "plutôt",
    "responseType": "voice",
    "timestamp": "2024-01-15T10:32:00.000Z",
    "confidence": 0.95
  }
}
```

#### Récupérer les Réponses d'une Session
```http
GET /sessions/{sessionId}/responses
```

**Réponse:**
```json
{
  "success": true,
  "responses": [
    {
      "id": 123,
      "questionNum": 1,
      "questionText": "Avez-vous des difficultés à faire certains efforts physiques...",
      "score": 3,
      "responseText": "Plutôt",
      "transcript": "plutôt",
      "responseType": "voice",
      "timestamp": "2024-01-15T10:32:00.000Z",
      "confidence": 0.95
    }
  ],
  "statistics": {
    "totalQuestions": 30,
    "answered": 1,
    "missed": 29,
    "completionRate": 3.33,
    "averageScore": 3.0
  }
}
```

#### Mettre à jour une Réponse
```http
PUT /responses/{responseId}
```

**Request Body:**
```json
{
  "score": 2,
  "responseText": "Un peu",
  "transcript": "un peu",
  "confidence": 0.88
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Réponse mise à jour avec succès",
  "response": {
    "id": 123,
    "sessionId": "550e8400-e29b-41d4-a716-446655440000",
    "questionNum": 1,
    "score": 2,
    "responseText": "Un peu",
    "transcript": "un peu",
    "responseType": "voice",
    "timestamp": "2024-01-15T10:32:00.000Z",
    "confidence": 0.88
  }
}
```

#### Supprimer une Réponse
```http
DELETE /responses/{responseId}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Réponse supprimée avec succès"
}
```

---

### 🔊 Audio

#### Récupérer un Fichier Audio
```http
GET /audio/{questionId}
```

**Query Parameters:**
- `voice` (string): Voix à utiliser (défaut: fr-FR-Neural2-A)
- `speed` (number): Vitesse de lecture (0.5-2.0, défaut: 1.0)
- `format` (string): Format audio (`wav`, `mp3`, `ogg`)

**Réponse:**
```
Content-Type: audio/wav
Content-Length: 123456

[Binary audio data]
```

#### Générer un Audio Personnalisé
```http
POST /audio/generate
```

**Request Body:**
```json
{
  "text": "Question 1. Avez-vous des difficultés à faire certains efforts physiques...",
  "voice": "fr-FR-Neural2-A",
  "speed": 1.2,
  "format": "wav"
}
```

**Réponse:**
```json
{
  "success": true,
  "audioUrl": "https://api.questionnaire-eortc.com/v1/audio/cache/abc123.wav",
  "duration": 15.5,
  "size": 248832,
  "hash": "abc123def456"
}
```

#### Vérifier le Cache Audio
```http
GET /audio/cache/{hash}
```

**Réponse:**
```json
{
  "success": true,
  "exists": true,
  "audioUrl": "https://api.questionnaire-eortc.com/v1/audio/cache/abc123.wav",
  "duration": 15.5,
  "size": 248832,
  "createdAt": "2024-01-15T10:30:00.000Z",
  "expiresAt": "2024-01-16T10:30:00.000Z"
}
```

---

### 🎤 Reconnaissance Vocale

#### Transcrire un Audio
```http
POST /speech/transcribe
Content-Type: multipart/form-data
```

**Request Body:**
```
audio: [Audio file]
language: fr-FR
sessionId: 550e8400-e29b-41d4-a716-446655440000
```

**Réponse:**
```json
{
  "success": true,
  "transcript": "plutôt",
  "confidence": 0.95,
  "alternatives": [
    "plutôt",
    "plus tôt",
    "plutot"
  ],
  "language": "fr-FR",
  "duration": 2.5
}
```

#### Interpréter une Transcription
```http
POST /speech/interpret
```

**Request Body:**
```json
{
  "transcript": "plutôt",
  "questionNum": 1,
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Réponse:**
```json
{
  "success": true,
  "score": 3,
  "responseText": "Plutôt",
  "confidence": 0.95,
  "suggestions": [
    "Pas du tout",
    "Un peu",
    "Plutôt",
    "Beaucoup"
  ]
}
```

#### Obtenir les Suggestions
```http
GET /speech/suggestions?questionNum=1&partial=pl
```

**Réponse:**
```json
{
  "success": true,
  "suggestions": [
    {
      "text": "plutôt",
      "score": 3,
      "confidence": 0.95
    },
    {
      "text": "plus tôt",
      "score": 3,
      "confidence": 0.88
    }
  ]
}
```

---

### 📊 Statistiques

#### Statistiques d'une Session
```http
GET /sessions/{sessionId}/statistics
```

**Réponse:**
```json
{
  "success": true,
  "statistics": {
    "session": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "initials": "A B",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "completedAt": "2024-01-15T11:15:00.000Z",
      "duration": 45
    },
    "completion": {
      "totalQuestions": 30,
      "answered": 30,
      "missed": 0,
      "completionRate": 100.0
    },
    "scores": {
      "average": 2.8,
      "median": 3.0,
      "min": 1,
      "max": 4,
      "distribution": {
        "1": 5,
        "2": 8,
        "3": 12,
        "4": 5
      }
    },
    "categories": {
      "physical_functioning": {
        "average": 2.5,
        "questions": [1, 2, 3, 4, 5]
      },
      "emotional_functioning": {
        "average": 3.2,
        "questions": [21, 22, 23, 24]
      }
    },
    "responseTypes": {
      "voice": 25,
      "manual": 5
    }
  }
}
```

#### Statistiques Globales
```http
GET /statistics/global?from=2024-01-01&to=2024-01-31
```

**Réponse:**
```json
{
  "success": true,
  "statistics": {
    "period": {
      "from": "2024-01-01T00:00:00.000Z",
      "to": "2024-01-31T23:59:59.999Z"
    },
    "sessions": {
      "total": 150,
      "completed": 120,
      "inProgress": 30,
      "completionRate": 80.0
    },
    "responses": {
      "total": 3600,
      "averagePerSession": 24.0,
      "voiceResponses": 2880,
      "manualResponses": 720
    },
    "scores": {
      "average": 2.7,
      "median": 3.0,
      "distribution": {
        "1": 450,
        "2": 720,
        "3": 1080,
        "4": 450
      }
    },
    "categories": {
      "physical_functioning": {
        "average": 2.4,
        "questions": 5
      },
      "emotional_functioning": {
        "average": 3.1,
        "questions": 4
      }
    }
  }
}
```

---

### 📤 Export

#### Exporter une Session
```http
GET /sessions/{sessionId}/export?format=json
```

**Query Parameters:**
- `format` (string): `json`, `csv`, `excel`, `pdf`
- `includeAudio` (boolean): Inclure les fichiers audio
- `includeMetadata` (boolean): Inclure les métadonnées

**Réponse:**
```json
{
  "success": true,
  "downloadUrl": "https://api.questionnaire-eortc.com/v1/exports/abc123.json",
  "expiresAt": "2024-01-15T12:30:00.000Z",
  "format": "json",
  "size": 12345,
  "filename": "eortc_questionnaire_2024-01-15_10-30-00.json"
}
```

#### Exporter Multiple Sessions
```http
POST /export/batch
```

**Request Body:**
```json
{
  "sessionIds": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ],
  "format": "excel",
  "includeAudio": false,
  "includeMetadata": true
}
```

**Réponse:**
```json
{
  "success": true,
  "exportId": "export-123",
  "status": "processing",
  "downloadUrl": null,
  "estimatedTime": 30
}
```

#### Vérifier le Statut d'un Export
```http
GET /export/{exportId}/status
```

**Réponse:**
```json
{
  "success": true,
  "exportId": "export-123",
  "status": "completed",
  "downloadUrl": "https://api.questionnaire-eortc.com/v1/exports/export-123.xlsx",
  "expiresAt": "2024-01-15T12:30:00.000Z",
  "progress": 100,
  "filename": "eortc_questionnaire_batch_2024-01-15.xlsx"
}
```

---

### 🔍 Recherche et Filtres

#### Rechercher des Sessions
```http
GET /sessions/search?q=initials:A&status=completed&from=2024-01-01
```

**Query Parameters:**
- `q` (string): Requête de recherche
- `status` (string): `all`, `completed`, `in_progress`
- `from` (string): Date de début (ISO 8601)
- `to` (string): Date de fin (ISO 8601)
- `completionRate` (number): Taux de complétion minimum
- `averageScore` (number): Score moyen minimum
- `sort` (string): `createdAt`, `completedAt`, `completionRate`
- `order` (string): `asc`, `desc`

**Réponse:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "initials": "A B",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "completedAt": "2024-01-15T11:15:00.000Z",
      "completionRate": 100.0,
      "averageScore": 2.8,
      "responseCount": 30
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 5,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  },
  "filters": {
    "q": "initials:A",
    "status": "completed",
    "from": "2024-01-01T00:00:00.000Z"
  }
}
```

---

### 🏥 Santé et Monitoring

#### Health Check
```http
GET /health
```

**Réponse:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0",
  "uptime": 86400,
  "services": {
    "database": {
      "status": "healthy",
      "responseTime": 5
    },
    "redis": {
      "status": "healthy",
      "responseTime": 2
    },
    "googleCloud": {
      "status": "healthy",
      "responseTime": 150
    }
  }
}
```

#### Readiness Check
```http
GET /ready
```

**Réponse:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "googleCloud": "ok"
  }
}
```

#### Métriques
```http
GET /metrics
```

**Réponse:**
```json
{
  "success": true,
  "metrics": {
    "requests": {
      "total": 1500,
      "perSecond": 2.5,
      "errors": 15,
      "errorRate": 0.01
    },
    "sessions": {
      "active": 25,
      "completed": 120,
      "averageDuration": 45
    },
    "responses": {
      "total": 3600,
      "voiceResponses": 2880,
      "manualResponses": 720
    },
    "audio": {
      "cacheHitRate": 0.85,
      "averageGenerationTime": 2.5
    },
    "speech": {
      "averageConfidence": 0.92,
      "averageTranscriptionTime": 1.2
    }
  }
}
```

---

## 🚨 Codes d'Erreur

### Codes HTTP Standards
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

### Codes d'Erreur Spécifiques
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies ne sont pas valides",
    "details": [
      {
        "field": "initials",
        "message": "Les initiales doivent contenir entre 1 et 10 caractères"
      }
    ]
  }
}
```

**Codes d'Erreur Disponibles:**
- `VALIDATION_ERROR` - Erreur de validation des données
- `SESSION_NOT_FOUND` - Session introuvable
- `SESSION_EXPIRED` - Session expirée
- `QUESTION_NOT_FOUND` - Question introuvable
- `AUDIO_GENERATION_FAILED` - Échec génération audio
- `SPEECH_RECOGNITION_FAILED` - Échec reconnaissance vocale
- `EXPORT_FAILED` - Échec export
- `RATE_LIMIT_EXCEEDED` - Limite de taux dépassée
- `AUTHENTICATION_REQUIRED` - Authentification requise
- `INSUFFICIENT_PERMISSIONS` - Permissions insuffisantes

---

## 🔄 Rate Limiting

### Limites par Endpoint
- **Sessions** : 100 requêtes/heure
- **Questions** : 1000 requêtes/heure
- **Réponses** : 500 requêtes/heure
- **Audio** : 200 requêtes/heure
- **Speech** : 100 requêtes/heure
- **Export** : 10 requêtes/heure

### Headers de Rate Limiting
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

## 📝 Exemples d'Intégration

### JavaScript/TypeScript
```typescript
class QuestionnaireAPI {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl: string, token: string) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async createSession(data: CreateSessionRequest): Promise<CreateSessionResponse> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  async saveResponse(data: SaveResponseRequest): Promise<SaveResponseResponse> {
    const response = await fetch(`${this.baseUrl}/responses`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    return await response.json();
  }
}

// Utilisation
const api = new QuestionnaireAPI('https://api.questionnaire-eortc.com/v1', 'your-token');

const session = await api.createSession({
  initials: 'A B',
  birthDate: '1970-01-01',
  todayDate: '2024-01-15',
  audioEnabled: true,
  mode: 'continuous'
});

const response = await api.saveResponse({
  sessionId: session.sessionId,
  questionNum: 1,
  score: 3,
  responseType: 'voice',
  transcript: 'plutôt',
  confidence: 0.95
});
```

### Python
```python
import requests
import json

class QuestionnaireAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def create_session(self, data: dict) -> dict:
        response = requests.post(
            f'{self.base_url}/sessions',
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def save_response(self, data: dict) -> dict:
        response = requests.post(
            f'{self.base_url}/responses',
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

# Utilisation
api = QuestionnaireAPI('https://api.questionnaire-eortc.com/v1', 'your-token')

session = api.create_session({
    'initials': 'A B',
    'birthDate': '1970-01-01',
    'todayDate': '2024-01-15',
    'audioEnabled': True,
    'mode': 'continuous'
})

response = api.save_response({
    'sessionId': session['sessionId'],
    'questionNum': 1,
    'score': 3,
    'responseType': 'voice',
    'transcript': 'plutôt',
    'confidence': 0.95
})
```

### cURL
```bash
# Créer une session
curl -X POST "https://api.questionnaire-eortc.com/v1/sessions" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "initials": "A B",
    "birthDate": "1970-01-01",
    "todayDate": "2024-01-15",
    "audioEnabled": true,
    "mode": "continuous"
  }'

# Sauvegarder une réponse
curl -X POST "https://api.questionnaire-eortc.com/v1/responses" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "550e8400-e29b-41d4-a716-446655440000",
    "questionNum": 1,
    "score": 3,
    "responseType": "voice",
    "transcript": "plutôt",
    "confidence": 0.95
  }'
```

---

## 🔧 Configuration et Déploiement

### Variables d'Environnement
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

# Rate Limiting
RATE_LIMIT_WINDOW_MS=3600000
RATE_LIMIT_MAX_REQUESTS=1000
```

### Docker
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

### Kubernetes
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
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 📞 Support

### Contact
- **Email** : api-support@questionnaire-eortc.com
- **Documentation** : https://docs.questionnaire-eortc.com
- **Status Page** : https://status.questionnaire-eortc.com

### SLA
- **Disponibilité** : 99.9%
- **Temps de réponse** : < 200ms (P95)
- **Support** : 24/7 pour les incidents critiques

### Changelog
- **v1.0.0** (2024-01-15) : Version initiale
- **v1.1.0** (2024-02-01) : Ajout des statistiques globales
- **v1.2.0** (2024-02-15) : Amélioration de la reconnaissance vocale

---

*Cette documentation est maintenue à jour avec les dernières versions de l'API. Pour toute question, contactez l'équipe de développement.*
