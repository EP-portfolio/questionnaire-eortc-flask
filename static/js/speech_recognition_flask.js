/**
 * Gestionnaire de reconnaissance vocale pour l'application Flask
 * Support Web Speech API (Chrome/Edge) et fallback (Firefox/Safari)
 */

class SpeechRecognitionManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isWebSpeechSupported = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.init();
    }
    
    init() {
        // Vérifier le support Web Speech API
        this.isWebSpeechSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        
        if (this.isWebSpeechSupported) {
            this.initWebSpeech();
        } else {
            console.log('Web Speech API non supportée, utilisation du mode fallback');
        }
    }
    
    initWebSpeech() {
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configuration
            this.recognition.continuous = false; // Un résultat à la fois
            this.recognition.interimResults = false;
            this.recognition.lang = 'fr-FR';
            this.recognition.maxAlternatives = 1;
            
            // Événements
            this.recognition.onstart = () => {
                console.log('Reconnaissance vocale démarrée');
                this.isListening = true;
                this.updateUI('listening');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                
                console.log('Résultat:', transcript, 'Confiance:', confidence);
                this.handleSpeechResult(transcript, confidence);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Erreur reconnaissance:', event.error);
                this.handleSpeechError(event.error);
            };
            
            this.recognition.onend = () => {
                console.log('Reconnaissance vocale terminée');
                this.isListening = false;
                this.updateUI('stopped');
            };
            
        } catch (error) {
            console.error('Erreur initialisation Web Speech:', error);
            this.isWebSpeechSupported = false;
        }
    }
    
    startContinuousSpeech() {
        if (!this.isWebSpeechSupported) {
            alert('Reconnaissance vocale continue non disponible sur ce navigateur');
            return;
        }
        
        if (this.isListening) {
            this.stopContinuousSpeech();
            return;
        }
        
        try {
            this.recognition.start();
            this.updateUI('active');
        } catch (error) {
            console.error('Erreur démarrage reconnaissance:', error);
            alert('Erreur : Impossible de démarrer la reconnaissance vocale');
        }
    }
    
    stopContinuousSpeech() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        this.isListening = false;
        this.updateUI('stopped');
    }
    
    handleSpeechResult(transcript, confidence) {
        // Afficher le transcript
        this.updateTranscript(transcript);
        
        // Envoyer au backend pour traitement
        this.processVoiceResponse(transcript);
    }
    
    handleSpeechError(error) {
        let message = '';
        
        switch (error) {
            case 'no-speech':
                message = 'Aucune parole détectée. Veuillez réessayer.';
                // Redémarrer automatiquement
                setTimeout(() => {
                    if (this.isListening) {
                        this.recognition.start();
                    }
                }, 1000);
                break;
            case 'audio-capture':
                message = 'Erreur : Microphone non disponible';
                break;
            case 'not-allowed':
                message = 'Erreur : Accès au microphone refusé';
                break;
            case 'network':
                message = 'Erreur : Problème de connexion réseau';
                break;
            case 'aborted':
                // Reconnaissance arrêtée par l'utilisateur, pas d'erreur
                return;
            default:
                message = `Erreur reconnaissance : ${error}`;
        }
        
        if (message) {
            this.showError(message);
        }
    }
    
    async processVoiceResponse(transcript) {
        try {
            // Vérifier que le transcript n'est pas vide
            if (!transcript || transcript.trim() === '') {
                this.showError('Aucune parole détectée. Veuillez parler plus fort.');
                return;
            }
            
            const response = await fetch('/api/process_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: window.sessionId,
                    question_num: window.currentQuestion,
                    transcript: transcript
                })
            });
            
            const result = await response.json();
            
            if (result.valid) {
                this.showSuccess(result.response_text);
                
                // Passer à la question suivante ou terminer
                if (result.is_complete) {
                    setTimeout(() => {
                        window.location.href = `/resultat/${window.sessionId}`;
                    }, 2000);
                } else {
                    setTimeout(() => {
                        window.loadQuestion(result.next_question);
                    }, 2000);
                }
            } else {
                this.showError(result.error || 'Réponse non reconnue');
                this.showSuggestions(result.suggestions || []);
            }
            
        } catch (error) {
            console.error('Erreur traitement vocal:', error);
            this.showError('Erreur : Impossible de traiter la réponse');
        }
    }
    
    updateUI(state) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const startBtn = document.getElementById('start-speech-btn');
        const stopBtn = document.getElementById('stop-speech-btn');
        
        if (!statusIndicator || !statusText) return;
        
        switch (state) {
            case 'active':
                statusIndicator.innerHTML = '<i class="fas fa-microphone"></i>';
                statusIndicator.style.background = 'rgba(255, 255, 255, 0.3)';
                statusText.textContent = '🎤 Micro actif - Parlez naturellement';
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-flex';
                break;
                
            case 'listening':
                statusIndicator.innerHTML = '<i class="fas fa-circle"></i>';
                statusIndicator.style.background = 'rgba(255, 0, 0, 0.3)';
                statusText.textContent = '🔴 Écoute en cours...';
                break;
                
            case 'stopped':
                statusIndicator.innerHTML = '<i class="fas fa-microphone"></i>';
                statusIndicator.style.background = 'rgba(255, 255, 255, 0.2)';
                statusText.textContent = 'Cliquez pour activer le micro continu';
                startBtn.style.display = 'inline-flex';
                stopBtn.style.display = 'none';
                break;
        }
    }
    
    updateTranscript(transcript) {
        const transcriptText = document.getElementById('transcript-text');
        if (transcriptText) {
            transcriptText.textContent = `Vous : "${transcript}"`;
        }
    }
    
    showSuccess(message) {
        // Créer une notification de succès
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    showError(message) {
        // Créer une notification d'erreur
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // Supprimer après 5 secondes
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    showSuggestions(suggestions) {
        if (suggestions && suggestions.length > 0) {
            const suggestionText = `Exemples valides : ${suggestions.join(', ')}`;
            this.showError(suggestionText);
        }
    }
}

// Mode Fallback pour Firefox/Safari
class FallbackRecognitionManager {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
    }
    
    async startRecording() {
        if (this.isRecording) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateUI('recording');
            
        } catch (error) {
            console.error('Erreur accès microphone:', error);
            alert('Erreur : Impossible d\'accéder au microphone');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateUI('stopped');
        }
    }
    
    async processRecording() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        
        // Envoyer l'audio au backend pour traitement
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('session_id', window.sessionId);
        formData.append('question_num', window.currentQuestion);
        
        try {
            const response = await fetch('/api/process_audio', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.valid) {
                this.showSuccess(result.response_text);
                
                if (result.is_complete) {
                    setTimeout(() => {
                        window.location.href = `/resultat/${window.sessionId}`;
                    }, 2000);
                } else {
                    setTimeout(() => {
                        window.loadQuestion(result.next_question);
                    }, 2000);
                }
            } else {
                this.showError(result.error || 'Réponse non reconnue');
            }
            
        } catch (error) {
            console.error('Erreur traitement audio:', error);
            this.showError('Erreur : Impossible de traiter l\'enregistrement');
        }
    }
    
    updateUI(state) {
        const recorderBtn = document.getElementById('recorder-btn');
        const recordingStatus = document.getElementById('recording-status');
        
        if (state === 'recording') {
            recorderBtn.innerHTML = '<i class="fas fa-stop"></i><span>🔴 Arrêter</span>';
            recorderBtn.classList.add('recording');
            if (recordingStatus) {
                recordingStatus.style.display = 'block';
            }
        } else {
            recorderBtn.innerHTML = '<i class="fas fa-microphone"></i><span>🎤 Cliquer pour parler</span>';
            recorderBtn.classList.remove('recording');
            if (recordingStatus) {
                recordingStatus.style.display = 'none';
            }
        }
    }
    
    showSuccess(message) {
        // Même implémentation que SpeechRecognitionManager
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    showError(message) {
        // Même implémentation que SpeechRecognitionManager
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialisation globale
let speechManager = null;
let fallbackManager = null;

// Fonctions globales pour l'interface
function startContinuousSpeech() {
    if (speechManager) {
        speechManager.startContinuousSpeech();
    }
}

function stopContinuousSpeech() {
    if (speechManager) {
        speechManager.stopContinuousSpeech();
    }
}

function startRecording() {
    if (fallbackManager) {
        if (fallbackManager.isRecording) {
            fallbackManager.stopRecording();
        } else {
            fallbackManager.startRecording();
        }
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier le mode navigateur
    const browserType = localStorage.getItem('browser_type');
    const isWebSpeechMode = browserType === 'chrome';
    
    if (isWebSpeechMode) {
        speechManager = new SpeechRecognitionManager();
    } else {
        fallbackManager = new FallbackRecognitionManager();
    }
    
    // Exposer les variables globales
    window.sessionId = new URLSearchParams(window.location.search).get('session_id');
    window.currentQuestion = 1;
    window.loadQuestion = loadQuestion;
});

// Animation CSS pour les notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
`;
document.head.appendChild(style);
