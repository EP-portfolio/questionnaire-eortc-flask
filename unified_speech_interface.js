/**
 * Interface Unifiée de Reconnaissance Vocale
 * Masque les différences entre Chrome et Firefox
 * Fournit une expérience utilisateur identique
 */

class UnifiedSpeechInterface {
    constructor() {
        this.isChrome = this.detectChrome();
        this.isFirefox = this.detectFirefox();
        this.isListening = false;
        this.currentTranscript = '';
        this.callbacks = {
            onResult: null,
            onError: null,
            onStart: null,
            onStop: null
        };

        this.init();
    }

    detectChrome() {
        const userAgent = navigator.userAgent.toLowerCase();
        return userAgent.includes('chrome') && !userAgent.includes('edg');
    }

    detectFirefox() {
        const userAgent = navigator.userAgent.toLowerCase();
        return userAgent.includes('firefox');
    }

    init() {
        console.log('🔧 Interface unifiée initialisée');
        console.log(`🌐 Navigateur: ${this.isChrome ? 'Chrome' : this.isFirefox ? 'Firefox' : 'Autre'}`);

        // Initialiser le manager approprié
        if (this.isChrome && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            this.manager = new ChromeSpeechManager(this);
        } else {
            this.manager = new FirefoxSpeechManager(this);
        }
    }

    // ✅ API UNIFIÉE - Même interface pour tous les navigateurs
    startListening() {
        console.log('🎤 Démarrage écoute unifiée');
        this.isListening = true;
        this.manager.startListening();
        this.triggerCallback('onStart');
    }

    stopListening() {
        console.log('🛑 Arrêt écoute unifiée');
        this.isListening = false;
        this.manager.stopListening();
        this.triggerCallback('onStop');
    }

    // ✅ CALLBACKS UNIFIÉS
    onResult(callback) {
        this.callbacks.onResult = callback;
    }

    onError(callback) {
        this.callbacks.onError = callback;
    }

    onStart(callback) {
        this.callbacks.onStart = callback;
    }

    onStop(callback) {
        this.callbacks.onStop = callback;
    }

    // ✅ FEEDBACK UNIFIÉ - Même style pour tous
    showUnifiedFeedback(transcript, confidence = 1.0) {
        // Supprimer les anciens feedbacks
        const existing = document.querySelector('.unified-speech-feedback');
        if (existing) existing.remove();

        // Créer le feedback unifié
        const feedback = document.createElement('div');
        feedback.className = 'unified-speech-feedback';
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

        // Indicateur de confiance
        const confidenceColor = confidence > 0.7 ? '#4CAF50' : confidence > 0.4 ? '#FF9800' : '#F44336';
        const confidenceText = confidence > 0.7 ? 'Haute' : confidence > 0.4 ? 'Moyenne' : 'Faible';

        feedback.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-microphone" style="color: #fff; font-size: 16px;"></i>
                <div>
                    <div style="font-weight: bold;">"${transcript}"</div>
                    <div style="font-size: 12px; opacity: 0.8;">
                        Confiance: <span style="color: ${confidenceColor};">${confidenceText}</span>
                    </div>
                </div>
            </div>
        `;

        // Ajouter les styles CSS si nécessaire
        if (!document.querySelector('#unified-speech-styles')) {
            const style = document.createElement('style');
            style.id = 'unified-speech-styles';
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

        // Supprimer après 3 secondes
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => {
                    if (feedback.parentNode) {
                        feedback.parentNode.removeChild(feedback);
                    }
                }, 300);
            }
        }, 3000);
    }

    // ✅ GESTION UNIFIÉE DES RÉSULTATS
    handleResult(transcript, confidence = 1.0) {
        this.currentTranscript = transcript;

        // Afficher le feedback unifié (même style pour tous)
        this.showUnifiedFeedback(transcript, confidence);

        // Déclencher le callback
        this.triggerCallback('onResult', { transcript, confidence });
    }

    handleError(error) {
        console.error('❌ Erreur reconnaissance unifiée:', error);
        this.triggerCallback('onError', error);
    }

    triggerCallback(type, data = null) {
        if (this.callbacks[type]) {
            this.callbacks[type](data);
        }
    }

    // ✅ MÉTHODES DE CONTRÔLE UNIFIÉES
    isActive() {
        return this.isListening;
    }

    getCurrentTranscript() {
        return this.currentTranscript;
    }

    // ✅ CONFIGURATION UNIFIÉE
    setLanguage(lang = 'fr-FR') {
        this.manager.setLanguage(lang);
    }

    setConfidenceThreshold(threshold = 0.3) {
        this.manager.setConfidenceThreshold(threshold);
    }
}

// ✅ MANAGER CHROME - Wrapper autour de Web Speech API
class ChromeSpeechManager {
    constructor(unifiedInterface) {
        this.unified = unifiedInterface;
        this.recognition = null;
        this.init();
    }

    init() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'fr-FR';
        this.recognition.maxAlternatives = 1;

        this.recognition.onstart = () => {
            console.log('🌐 Chrome: Reconnaissance démarrée');
        };

        this.recognition.onresult = (event) => {
            const last = event.results.length - 1;
            const result = event.results[last];
            const transcript = result[0].transcript.trim();
            const confidence = result[0].confidence;
            const isFinal = result.isFinal;

            if (isFinal || (confidence > 0.7 && transcript.length <= 20)) {
                this.unified.handleResult(transcript, confidence);
            }
        };

        this.recognition.onerror = (event) => {
            this.unified.handleError(event.error);
        };

        this.recognition.onend = () => {
            if (this.unified.isActive()) {
                // Redémarrer automatiquement
                setTimeout(() => this.startListening(), 100);
            }
        };
    }

    startListening() {
        if (this.recognition) {
            this.recognition.start();
        }
    }

    stopListening() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    setLanguage(lang) {
        if (this.recognition) {
            this.recognition.lang = lang;
        }
    }

    setConfidenceThreshold(threshold) {
        // Chrome gère la confiance automatiquement
        console.log('🌐 Chrome: Seuil de confiance ignoré (géré automatiquement)');
    }
}

// ✅ MANAGER FIREFOX - Wrapper autour de FallbackRecognitionManager
class FirefoxSpeechManager {
    constructor(unifiedInterface) {
        this.unified = unifiedInterface;
        this.fallbackManager = null;
        this.init();
    }

    init() {
        // Utiliser le FallbackRecognitionManager existant
        if (window.fallbackManager) {
            this.fallbackManager = window.fallbackManager;
            this.setupCallbacks();
        } else {
            console.error('❌ FallbackRecognitionManager non disponible');
        }
    }

    setupCallbacks() {
        // Intercepter les résultats du fallback manager
        const originalProcessVoiceResponse = this.fallbackManager.processVoiceResponse;
        this.fallbackManager.processVoiceResponse = (transcript) => {
            // Simuler une confiance élevée pour Firefox
            this.unified.handleResult(transcript, 0.8);

            // Appeler la fonction originale
            if (originalProcessVoiceResponse) {
                originalProcessVoiceResponse.call(this.fallbackManager, transcript);
            }
        };
    }

    startListening() {
        if (this.fallbackManager) {
            this.fallbackManager.startContinuousSpeech();
        }
    }

    stopListening() {
        if (this.fallbackManager) {
            this.fallbackManager.stopContinuousSpeech();
        }
    }

    setLanguage(lang) {
        // Firefox utilise la configuration serveur
        console.log('🦊 Firefox: Langue configurée côté serveur');
    }

    setConfidenceThreshold(threshold) {
        // Firefox utilise la configuration serveur
        console.log('🦊 Firefox: Seuil de confiance configuré côté serveur');
    }
}

// ✅ EXPORT GLOBAL
window.UnifiedSpeechInterface = UnifiedSpeechInterface;

