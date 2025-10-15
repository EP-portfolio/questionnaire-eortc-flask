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

    // ✅ NOUVEAU : Gestion intelligente de l'arrêt audio (Chrome uniquement)
    handleAudioStop() {
        console.log('🔇 Audio arrêté - Gestion Chrome (logique existante préservée)');

        // ✅ PRÉSERVER : Logique Chrome existante qui fonctionne
        if (this.recognition && !this.isPaused) {
            console.log('🌐 Chrome : Mise en pause simple (logique existante)');
            this.pauseRecognition();

            // Redémarrage automatique après 2 secondes (logique existante)
            setTimeout(() => {
                if (this.isPaused) {
                    console.log('🌐 Chrome : Reprise automatique (logique existante)');
                    this.resumeRecognition();
                }
            }, 2000);
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
        if (cleanTranscript.length > 20) {
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
// VERSION AMÉLIORÉE : Écoute continue via MediaRecorder + Whisper (backend)
class FallbackRecognitionManager {
    constructor() {
        this.mediaRecorder = null;
        this.audioStream = null;
        this.isListening = false;
        this.isPaused = false;
        this.processingResponse = false;
    }

    init() {
        console.log('✅ Mode fallback : Écoute continue Firefox (Whisper backend)');
    }

    // ✅ Pause/reprise (compatible avec l'API existante)
    pauseRecognition() {
        console.log('⏸️ Reconnaissance mise en pause (fallback)');
        this.isPaused = true;

        // ✅ FIREFOX : Log pour debug
        console.log('🦊 Firefox : État pause activé - isListening:', this.isListening);
    }

    resumeRecognition() {
        console.log('▶️ Reconnaissance reprise (fallback)');
        this.isPaused = false;

        // ✅ FIREFOX : Vérifier si on doit redémarrer l'écoute
        if (!this.isListening) {
            console.log('🦊 Firefox : Redémarrage nécessaire après reprise');
            this.startContinuousSpeech();
        } else {
            console.log('🦊 Firefox : Écoute déjà active, reprise simple');
        }
    }

    // ✅ NOUVEAU : Gestion intelligente de l'arrêt audio pour Firefox uniquement
    handleAudioStop() {
        console.log('🔇 Audio arrêté - Gestion Firefox (logique spécifique)');

        // ✅ FIREFOX : Gestion spéciale des états en pause
        if (this.isPaused) {
            console.log('🦊 Firefox : Reprise depuis pause (audio arrêté)');
            this.isPaused = false;
            // Si déjà en écoute, juste reprendre
            if (this.isListening) {
                console.log('🦊 Firefox : Écoute déjà active, reprise simple');
                return;
            }
        }

        // ✅ LOGIQUE FIREFOX : Arrêter et redémarrer proprement
        if (this.mediaRecorder && this.isListening) {
            console.log('🦊 Firefox : Arrêt pour audio (logique Firefox)');

            // Arrêter proprement
            this.stopContinuousSpeech();

            // ✅ FIREFOX : Redémarrage immédiat pour éviter la pause
            setTimeout(() => {
                console.log('🦊 Firefox : Redémarrage immédiat après arrêt audio');
                this.isPaused = false; // S'assurer qu'on n'est pas en pause
                this.startContinuousSpeech();
            }, 500); // Réduire à 0.5 seconde pour plus de réactivité
        } else if (!this.isListening) {
            console.log('🦊 Firefox : Redémarrage direct (pas d\'arrêt nécessaire)');
            this.isPaused = false;
            this.startContinuousSpeech();
        } else {
            console.log('🦊 Firefox : Pas de MediaRecorder actif');
        }
    }

    async startContinuousSpeech() {
        // ✅ FIREFOX : Logique simple sans interférer avec Chrome
        if (this.isListening) {
            console.log('⚠️ Firefox : Écoute déjà active');
            return;
        }

        // ✅ FIREFOX : Nettoyer l'état précédent si nécessaire
        if (this.mediaRecorder && this.mediaRecorder.state === 'inactive') {
            console.log('🦊 Firefox : Nettoyage état précédent');
            this.mediaRecorder = null;
        }

        try {
            console.log('🎤 Démarrage écoute continue (fallback - Whisper)');

            // ✅ Obtenir accès au microphone avec configuration optimisée
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 48000,  // ✅ CORRECTION : 48kHz pour WEBM OPUS
                    channelCount: 1,    // ✅ CORRECTION : Mono
                    sampleSize: 16,     // ✅ CORRECTION : 16-bit
                    latency: 0.01       // ✅ CORRECTION : Latence réduite
                }
            });

            // ✅ Créer MediaRecorder
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : 'audio/webm';

            this.mediaRecorder = new MediaRecorder(this.audioStream, { mimeType });

            // ✅ Traiter chaque chunk audio
            this.mediaRecorder.ondataavailable = async (event) => {
                if (event.data.size > 0 && this.isListening && !this.isPaused) {
                    await this.transcribeChunk(event.data);
                }
            };

            this.mediaRecorder.onerror = (error) => {
                console.error('❌ Erreur MediaRecorder:', error);
            };

            // ✅ AMÉLIORATION : Chunks de 3 secondes pour meilleure qualité
            this.mediaRecorder.start(3000);
            this.isListening = true;

            console.log('✅ Écoute continue démarrée (chunks de 3s)');

        } catch (error) {
            console.error('❌ Erreur accès microphone:', error);
            alert('Erreur : Impossible d\'accéder au microphone.\nVérifiez les permissions.');
        }
    }

    stopContinuousSpeech() {
        if (this.mediaRecorder && this.isListening) {
            console.log('🛑 Arrêt écoute continue (fallback)');
            this.mediaRecorder.stop();
            this.isListening = false;
        }

        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
    }

    async transcribeChunk(audioBlob) {
        if (this.processingResponse) {
            console.log('⏭️ Chunk ignoré (traitement en cours)');
            return;
        }

        // ✅ FILTRE : Ignorer les chunks trop petits (bruit de fond)
        if (audioBlob.size < 5000) {
            console.log('🔇 Chunk trop petit ignoré:', audioBlob.size, 'bytes');
            return;
        }

        // ✅ FILTRE : Vérifier si l'audio contient de la parole
        const hasSpeech = await this.detectSpeech(audioBlob);
        if (!hasSpeech) {
            console.log('🔇 Chunk silencieux ignoré');
            return;
        }

        try {
            console.log('🦊 Firefox : Transcription chunk audio avec parole détectée');
            console.log(`🔍 DEBUG: Taille chunk: ${audioBlob.size} bytes`);
            console.log(`🔍 DEBUG: Type chunk: ${audioBlob.type}`);

            // ✅ APPROCHE FIREFOX : Envoyer directement au serveur
            await this.transcribeWithServer(audioBlob);

        } catch (error) {
            console.error('❌ Erreur transcription chunk:', error);
        }
    }

    // ✅ NOUVELLE MÉTHODE : Détection de parole basique
    async detectSpeech(audioBlob) {
        try {
            // Créer un AudioContext pour analyser l'audio
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const arrayBuffer = await audioBlob.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

            // Analyser les données audio
            const channelData = audioBuffer.getChannelData(0);
            const length = channelData.length;

            // Calculer le volume RMS (Root Mean Square)
            let sum = 0;
            for (let i = 0; i < length; i++) {
                sum += channelData[i] * channelData[i];
            }
            const rms = Math.sqrt(sum / length);

            // ✅ AMÉLIORATION : Seuil plus sensible pour question 0
            const speechThreshold = 0.005; // Réduire de 0.01 à 0.005
            const hasSpeech = rms > speechThreshold;

            console.log(`🔍 DEBUG: RMS audio: ${rms.toFixed(4)}, Seuil: ${speechThreshold}, Parole: ${hasSpeech}`);

            audioContext.close();
            return hasSpeech;

        } catch (error) {
            console.warn('⚠️ Erreur détection parole:', error);
            // En cas d'erreur, considérer qu'il y a de la parole
            return true;
        }
    }

    // ✅ NOUVELLE MÉTHODE : Transcription avec Web Speech API (approche unmute.sh)
    async transcribeWithWebSpeech(audioBlob) {
        return new Promise((resolve, reject) => {
            try {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();

                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'fr-FR';
                recognition.maxAlternatives = 1;

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript.trim();
                    console.log('📝 Transcription Web Speech:', transcript);

                    if (transcript) {
                        this.handleSpeechResult(transcript);
                    }
                    resolve(transcript);
                };

                recognition.onerror = (error) => {
                    console.error('❌ Erreur Web Speech:', error);
                    reject(error);
                };

                recognition.onend = () => {
                    console.log('✅ Web Speech terminé');
                };

                // Démarrer la reconnaissance
                recognition.start();

            } catch (error) {
                console.error('❌ Erreur initialisation Web Speech:', error);
                reject(error);
            }
        });
    }

    // ✅ MÉTHODE FALLBACK : Transcription avec serveur
    // ✅ FEEDBACK VISUEL Firefox (corrigé)
    showVisualFeedback(transcript) {
        // Supprimer les anciens feedbacks
        const existingFeedback = document.querySelector('.firefox-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Créer un élément de feedback visuel
        const feedback = document.createElement('div');
        feedback.className = 'firefox-feedback';
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 12px 18px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
            word-wrap: break-word;
        `;

        feedback.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-microphone" style="color: #fff; font-size: 16px;"></i>
                <span><strong>Firefox:</strong> "${transcript}"</span>
            </div>
        `;

        // Ajouter l'animation CSS si pas déjà présente
        if (!document.querySelector('#firefox-feedback-styles')) {
            const style = document.createElement('style');
            style.id = 'firefox-feedback-styles';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(feedback);

        // Supprimer après 4 secondes avec animation
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => {
                    if (feedback.parentNode) {
                        feedback.parentNode.removeChild(feedback);
                    }
                }, 300);
            }
        }, 4000);
    }

    async transcribeWithServer(audioBlob) {
        try {
            console.log('📤 Envoi chunk audio vers serveur...');

            const formData = new FormData();
            formData.append('audio', audioBlob);
            formData.append('session_id', window.sessionId);
            formData.append('question_num', window.currentQuestion);

            const response = await fetch('/api/transcribe_chunk', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            console.log(`📡 Réponse serveur: ${response.status} `);

            if (!response.ok) {
                const errorText = await response.text();
                console.warn('⚠️ Erreur serveur transcription:', response.status, errorText);
                return;
            }

            // ✅ GESTION D'ERREUR : Vérifier le content-type
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const responseText = await response.text();
                console.warn('⚠️ Réponse non-JSON reçue:', responseText);
                return;
            }

            const result = await response.json();
            console.log('📝 Résultat serveur:', result);

            if (result.success && result.transcript && result.transcript.trim()) {
                const transcript = result.transcript.trim();
                console.log('📝 Transcription serveur:', transcript);

                // ✅ FILTRE : Ignorer les transcriptions trop courtes ou parasites
                if (transcript.length < 2) {
                    console.log('🔇 Transcription trop courte ignorée:', transcript);
                    return;
                }

                // ✅ FEEDBACK VISUEL Firefox
                this.showVisualFeedback(transcript);

                this.handleSpeechResult(transcript);
            } else if (result.success && result.fallback) {
                console.log('🦊 Firefox : Fallback activé - transcription vide ignorée');
                console.log('🦊 Firefox : Continue d\'écouter...');
                // ✅ IGNORER les transcriptions vides du fallback
                return;
            } else {
                console.log('📝 Aucune transcription valide reçue');
                console.log('📝 Résultat complet:', result);
            }

        } catch (error) {
            console.error('❌ Erreur transcription serveur:', error);
        }
    }

    handleSpeechResult(transcript) {
        // ✅ MÊME LOGIQUE que SpeechRecognitionManager
        const text = transcript.toLowerCase().trim();

        // Filtrage des résultats parasites
        if (text.length > 30) {
            console.log('⚠️ REJETÉ : Texte trop long');
            return;
        }

        if (/question\s+\d+/.test(text)) {
            console.log('⚠️ REJETÉ : Contient "question X"');
            return;
        }

        console.log('✅ ACCEPTÉ :', text);

        // Arrêter l'audio de la question si en cours
        if (window.stopAudioOnSpeech) {
            window.stopAudioOnSpeech();
        }

        // Traiter la réponse
        this.processVoiceResponse(text);
    }

    async processVoiceResponse(transcript) {
        if (this.processingResponse) {
            console.log('⏭️ Déjà en cours de traitement');
            return;
        }

        this.processingResponse = true;

        try {
            const response = await fetch('/api/process_voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: window.sessionId,
                    question_num: window.currentQuestion,
                    transcript: transcript
                })
            });

            const result = await response.json();

            if (result.valid) {
                console.log('✅ Réponse validée:', result.response_text);

                if (result.is_complete) {
                    setTimeout(() => {
                        window.location.href = `/ resultat / ${window.sessionId} `;
                    }, 1500);
                } else if (result.next_question && window.questionnaireManager) {
                    setTimeout(() => {
                        window.questionnaireManager.loadQuestion(result.next_question);
                    }, 1500);
                }
            } else {
                console.log('❌ Réponse non reconnue');
            }

        } catch (error) {
            console.error('❌ Erreur traitement réponse:', error);
        } finally {
            setTimeout(() => {
                this.processingResponse = false;
            }, 1000);
        }
    }

    // ✅ Méthodes de compatibilité (anciennes, pour ne pas casser l'UI existante)
    async startRecording() {
        // Rediriger vers écoute continue
        await this.startContinuousSpeech();
    }

    stopRecording() {
        // Rediriger vers arrêt écoute continue
        this.stopContinuousSpeech();
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
            < div class="notification-content" >
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div >
            `;

        notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear - gradient(135deg, #56ab2f 0 %, #a8e063 100 %);
        color: white;
        padding: 1rem 1.5rem;
        border - radius: 8px;
        box - shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z - index: 1000;
        animation: slideIn 0.3s ease - out;
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
            < div class="notification-content" >
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div >
            `;

        notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear - gradient(135deg, #eb3349 0 %, #f45c43 100 %);
        color: white;
        padding: 1rem 1.5rem;
        border - radius: 8px;
        box - shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z - index: 1000;
        animation: slideIn 0.3s ease - out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // ✅ SUPPRIMÉ : Indicateur visuel complexe non nécessaire
    // La logique Firefox est maintenant simple et directe
}

// Initialisation globale
let speechManager = null;
let fallbackManager = null;

// Fonctions globales pour l'interface
function startContinuousSpeech() {
    if (speechManager) {
        speechManager.startContinuousSpeech();
    } else if (fallbackManager) {
        // ✅ Firefox utilise aussi l'écoute continue maintenant
        fallbackManager.startContinuousSpeech();
    }
}

function stopContinuousSpeech() {
    if (speechManager) {
        speechManager.stopContinuousSpeech();
    } else if (fallbackManager) {
        // ✅ Firefox peut aussi arrêter l'écoute continue
        fallbackManager.stopContinuousSpeech();
    }
}

function startRecording() {
    if (fallbackManager) {
        // ✅ Compatibilité : rediriger vers écoute continue
        if (fallbackManager.isListening) {
            fallbackManager.stopContinuousSpeech();
        } else {
            fallbackManager.startContinuousSpeech();
        }
    }
}

// ✅ NOUVELLE FONCTION : Gestion intelligente de l'arrêt audio
function handleAudioStop() {
    console.log('🔇 Gestion globale de l\'arrêt audio');

    if (speechManager) {
        console.log('🌐 Chrome : Gestion arrêt audio');
        speechManager.handleAudioStop();
    } else if (fallbackManager) {
        console.log('🦊 Firefox : Gestion arrêt audio');
        fallbackManager.handleAudioStop();
    }
}

// ✅ DÉTECTION AMÉLIORÉE des navigateurs
const isWebSpeechSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
const userAgent = navigator.userAgent.toLowerCase();
const isFirefox = userAgent.includes('firefox');
const isChrome = userAgent.includes('chrome') && !userAgent.includes('edg');
const isSafari = userAgent.includes('safari') && !userAgent.includes('chrome');
const isEdge = userAgent.includes('edg');

console.log('🔍 Détection navigateur améliorée:');
console.log('  - User Agent:', userAgent);
console.log('  - Web Speech API supportée:', isWebSpeechSupported);
console.log('  - Détecté Firefox:', isFirefox);
console.log('  - Détecté Chrome:', isChrome);
console.log('  - Détecté Safari:', isSafari);
console.log('  - Détecté Edge:', isEdge);

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function () {
    console.log('📄 DOMContentLoaded - Initialisation des managers');

    // ✅ CRÉER les managers maintenant que le DOM est prêt
    managerType = createSpeechManagers();

    // ✅ ASSIGNER aux variables globales
    window.speechManager = speechManager;
    window.fallbackManager = fallbackManager;

    console.log('✅ Managers créés:', {
        speechManager: !!speechManager,
        fallbackManager: !!fallbackManager,
        type: managerType
    });

    window.loadQuestion = function (num) {
        if (window.questionnaireManager) {
            window.questionnaireManager.loadQuestion(num);
        }
    };
});

// ✅ CRÉATION INTELLIGENTE des managers
function createSpeechManagers() {
    // Priorité 1: Chrome/Edge avec Web Speech API
    if ((isChrome || isEdge) && isWebSpeechSupported) {
        console.log('🌐 Chrome/Edge avec Web Speech API → Mode Web Speech');
        speechManager = new SpeechRecognitionManager();
        fallbackManager = null;
        return 'web_speech';
    }

    // Priorité 2: Firefox/Safari ou navigateurs sans Web Speech API
    if (isFirefox || isSafari || !isWebSpeechSupported) {
        console.log('🦊 Firefox/Safari ou sans Web Speech → Mode Fallback');
        fallbackManager = new FallbackRecognitionManager();
        speechManager = null;
        return 'fallback';
    }

    // Fallback par défaut
    console.log('❓ Navigateur inconnu → Mode Fallback par défaut');
    fallbackManager = new FallbackRecognitionManager();
    speechManager = null;
    return 'fallback';
}

// ✅ CRÉATION DIFFÉRÉE des managers (après DOMContentLoaded)
let managerType = null;

// ✅ ASSIGNATION des variables globales
window.sessionId = new URLSearchParams(window.location.search).get('session_id');
window.currentQuestion = 1;

// ✅ EXPOSER les fonctions globales
window.handleAudioStop = handleAudioStop;

// ✅ FONCTION D'INITIALISATION AMÉLIORÉE
window.initSpeechRecognition = function () {
    console.log('🔧 initSpeechRecognition appelée');
    console.log('🔍 DEBUG: speechManager:', !!window.speechManager);
    console.log('🔍 DEBUG: fallbackManager:', !!window.fallbackManager);
    console.log('🔍 DEBUG: managerType:', managerType);

    if (window.speechManager) {
        console.log('🌐 Chrome : Initialisation SpeechRecognitionManager');
        window.speechManager.init();
    } else if (window.fallbackManager) {
        console.log('🦊 Firefox : Initialisation FallbackRecognitionManager');
        window.fallbackManager.init();
        console.log('🚀 Firefox : FallbackRecognitionManager initialisé');
    } else {
        console.error('❌ Aucun manager disponible !');
        console.error('❌ Vérifiez que DOMContentLoaded a été déclenché');
    }
};