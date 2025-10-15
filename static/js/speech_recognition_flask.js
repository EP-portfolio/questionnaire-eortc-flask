/**
 * Gestionnaire de reconnaissance vocale pour l'application Flask
 * Support Web Speech API (Chrome/Edge) et fallback (Firefox/Safari)
 * Version optimisée avec :
 * - Arrêt automatique de l'audio quand l'utilisateur parle
 * - Filtrage des résultats parasites
 * - Pause/reprise automatique pendant lecture audio
 * - Amélioration de la reconnaissance (moins de répétitions)
 */

class SpeechRecognitionManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isWebSpeechSupported = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.shouldRestart = false;
        this.processingResponse = false;
        this.isPaused = false; // ✅ Pour pause/reprise

        this.init();
    }

    // ✅ NOUVEAU : Mettre en pause la reconnaissance
    pauseRecognition() {
        if (this.recognition && !this.isPaused) {
            console.log('⏸️ Reconnaissance vocale mise en pause');
            this.isPaused = true;
            // On ne stop pas, juste on ignore les résultats pendant la pause
        }
    }

    // ✅ NOUVEAU : Reprendre la reconnaissance
    resumeRecognition() {
        if (this.recognition && this.isPaused) {
            console.log('▶️ Reconnaissance vocale reprise');
            this.isPaused = false;
        }
    }

    init() {
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

            // ✅ PARAMÈTRES OPTIMISÉS
            this.recognition.continuous = true;
            this.recognition.interimResults = true; // ✅ Activé pour meilleure réactivité
            this.recognition.lang = 'fr-FR';
            this.recognition.maxAlternatives = 1;

            this.recognition.onstart = () => {
                console.log('Reconnaissance vocale démarrée');
                this.isListening = true;
                this.updateUI('listening');
            };

            this.recognition.onresult = (event) => {
                // ✅ VÉRIFIER isPaused IMMÉDIATEMENT
                if (this.isPaused) {
                    console.log('⏸️ Reconnaissance en pause - Résultat ignoré (onresult)');
                    return; // Ignorer TOUS les résultats pendant la pause
                }

                console.log('DEBUG: onresult déclenché', event);

                const last = event.results.length - 1;
                const result = event.results[last];
                const transcript = result[0].transcript.trim();
                const confidence = result[0].confidence;
                const isFinal = result.isFinal;

                console.log('DEBUG: Résultat', isFinal ? 'FINAL' : 'INTERIM', ':', transcript, 'Confiance:', confidence);

                // ✅ AMÉLIORATION : Accepter résultats finaux OU intermédiaires avec haute confiance
                if (isFinal || (confidence > 0.7 && transcript.length <= 20)) {
                    this.handleSpeechResult(transcript, confidence);
                }
            };

            this.recognition.onerror = (event) => {
                // ✅ Ne pas logger l'erreur "network" (timeout normal)
                if (event.error !== 'network') {
                    console.error('Erreur reconnaissance:', event.error);
                }
                this.handleSpeechError(event.error);
            };

            this.recognition.onend = () => {
                console.log('Reconnaissance vocale terminée');
                this.isListening = false;
                this.updateUI('stopped');

                if (this.shouldRestart && !this.isListening) {
                    console.log('Redémarrage automatique de l\'écoute...');
                    setTimeout(() => {
                        if (this.shouldRestart && !this.isListening) {
                            this.startContinuousSpeech();
                        }
                    }, 1000);
                }
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

        this.shouldRestart = true;

        try {
            this.recognition.start();
            this.updateUI('active');
            console.log('Écoute continue démarrée');
        } catch (error) {
            console.error('Erreur démarrage reconnaissance:', error);
            alert('Erreur : Impossible de démarrer la reconnaissance vocale');
        }
    }

    stopContinuousSpeech() {
        this.shouldRestart = false;

        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        this.isListening = false;
        this.updateUI('stopped');
        console.log('Écoute continue arrêtée');
    }

    handleSpeechResult(transcript, confidence) {
        console.log('DEBUG: handleSpeechResult appelé avec:', transcript);

        // ============================================
        // 🛡️ FILTRAGE DES RÉSULTATS PARASITES
        // ============================================

        // Nettoyer le transcript
        const cleanTranscript = transcript.trim();

        // 1️⃣ FILTRE : Rejeter si le texte contient "question" suivi d'un chiffre
        const questionPattern = /question\s+\d+/i;
        if (questionPattern.test(cleanTranscript)) {
            console.log('⚠️ REJETÉ : Texte contient "question X" - probablement l\'audio de la question');
            console.log(`   Texte rejeté : "${cleanTranscript}"`);
            return;
        }

        // 2️⃣ FILTRE : Rejeter si le texte est trop long (> 12 caractères)
        // ✅ AMÉLIORATION : Limite augmentée à 15 pour accepter plus facilement
        if (cleanTranscript.length > 15) {
            console.log(`⚠️ REJETÉ : Texte trop long (${cleanTranscript.length} caractères)`);
            console.log(`   Texte rejeté : "${cleanTranscript.substring(0, 50)}..."`);
            return;
        }

        // 3️⃣ FILTRE : Rejeter si le texte est vide
        if (cleanTranscript.length === 0) {
            console.log('⚠️ REJETÉ : Texte vide');
            return;
        }

        // ✅ Le texte a passé tous les filtres
        console.log(`✅ ACCEPTÉ : "${cleanTranscript}" (${cleanTranscript.length} caractères)`);

        // ============================================
        // FIN FILTRAGE
        // ============================================

        // ✅ Arrêter l'audio de la question dès que l'utilisateur parle
        if (window.stopAudioOnSpeech) {
            console.log('🔇 Détection de parole - Arrêt de l\'audio de la question');
            window.stopAudioOnSpeech();
        }

        // Afficher le transcript
        this.updateTranscript(cleanTranscript);

        // ✅ AMÉLIORATION : Délai réduit de 500ms à 200ms
        setTimeout(() => {
            this.processVoiceResponse(cleanTranscript);
        }, 200);
    }

    handleSpeechError(error) {
        let message = '';

        switch (error) {
            case 'no-speech':
                message = 'Aucune parole détectée. Veuillez réessayer.';
                break;
            case 'audio-capture':
                message = 'Erreur : Microphone non disponible';
                break;
            case 'not-allowed':
                message = 'Erreur : Accès au microphone refusé';
                break;
            case 'network':
                // NE PAS afficher de message - redémarrage auto
                console.log('⚠️ Timeout réseau - redémarrage auto');
                return; // Ne pas afficher d'erreur à l'utilisateur
            case 'aborted':
                return;
            default:
                message = `Erreur reconnaissance : ${error}`;
        }

        if (message) {
            this.showError(message);
        }
    }

    async processVoiceResponse(transcript) {
        console.log('DEBUG: processVoiceResponse appelé avec:', transcript);

        if (this.processingResponse) {
            console.log('DEBUG: Déjà en cours de traitement, ignoré');
            return;
        }

        this.processingResponse = true;

        try {
            if (!transcript || transcript.trim() === '') {
                console.log('DEBUG: Transcript vide, arrêt');
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
        } finally {
            setTimeout(() => {
                this.processingResponse = false;
            }, 500);
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
                if (startBtn) startBtn.style.display = 'none';
                if (stopBtn) stopBtn.style.display = 'inline-flex';
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
                if (startBtn) startBtn.style.display = 'inline-flex';
                if (stopBtn) stopBtn.style.display = 'none';
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

        // ✅ Arrêter l'audio quand l'utilisateur commence à enregistrer
        if (window.stopAudioOnSpeech) {
            console.log('🔇 Début d\'enregistrement - Arrêt de l\'audio de la question');
            window.stopAudioOnSpeech();
        }

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
            if (recorderBtn) {
                recorderBtn.innerHTML = '<i class="fas fa-stop"></i><span>🔴 Arrêter</span>';
                recorderBtn.classList.add('recording');
            }
            if (recordingStatus) {
                recordingStatus.style.display = 'block';
            }
        } else {
            if (recorderBtn) {
                recorderBtn.innerHTML = '<i class="fas fa-microphone"></i><span>🎤 Cliquer pour parler</span>';
                recorderBtn.classList.remove('recording');
            }
            if (recordingStatus) {
                recordingStatus.style.display = 'none';
            }
        }
    }

    showSuccess(message) {
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
document.addEventListener('DOMContentLoaded', function () {
    const browserType = localStorage.getItem('browser_type');
    const isWebSpeechMode = browserType === 'chrome';

    if (isWebSpeechMode) {
        speechManager = new SpeechRecognitionManager();
    } else {
        fallbackManager = new FallbackRecognitionManager();
    }

    window.sessionId = new URLSearchParams(window.location.search).get('session_id');
    window.speechManager = speechManager;
    window.fallbackManager = fallbackManager;
    window.currentQuestion = 1;

    window.loadQuestion = function (num) {
        if (window.questionnaireManager) {
            window.questionnaireManager.loadQuestion(num);
        }
    };

    // ✅ Fonction d'initialisation simplifiée
    window.initSpeechRecognition = function () {
        console.log('initSpeechRecognition appelée');
        if (speechManager) {
            speechManager.init();
        } else if (fallbackManager) {
            fallbackManager.init();
        }
    };
});