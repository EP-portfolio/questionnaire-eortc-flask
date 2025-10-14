/**
 * Logique principale du questionnaire Flask
 * Gestion de l'interface utilisateur et communication avec le backend
 */

class QuestionnaireManager {
    constructor() {
        this.currentQuestion = 1;
        this.sessionId = null;
        this.questionData = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        // Récupérer l'ID de session depuis l'URL
        this.sessionId = new URLSearchParams(window.location.search).get('session_id');
        
        if (!this.sessionId) {
            console.error('Session ID manquant');
            alert('Erreur : Session invalide');
            return;
        }
        
        // Récupérer le numéro de question depuis l'URL (optionnel)
        const questionParam = new URLSearchParams(window.location.search).get('question');
        if (questionParam) {
            this.currentQuestion = parseInt(questionParam);
        }
        
        // Exposer les variables globales
        window.sessionId = this.sessionId;
        window.currentQuestion = this.currentQuestion;
        window.loadQuestion = (num) => this.loadQuestion(num);
        
        // Charger la question actuelle
        this.loadQuestion(this.currentQuestion);
    }
    
    async loadQuestion(questionNum) {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.currentQuestion = questionNum;
            window.currentQuestion = questionNum;
            
            // Mettre à jour l'interface
            this.updateProgress();
            this.updateNavigationButtons();
            
            // Charger les données de la question
            const response = await fetch(`/api/get_question/${questionNum}`);
            const result = await response.json();
            
            if (result.success) {
                this.questionData = result.question;
                this.displayQuestion(this.questionData);
                this.createResponseButtons(this.questionData);
                
                // Afficher le message spécial pour Q29-30
                this.toggleSpecialMessage(questionNum >= 29);
                
                // Lecture automatique si audio activé
                if (localStorage.getItem('audio_enabled') === 'true') {
                    setTimeout(() => this.playQuestionAudio(), 1000);
                }
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('Erreur chargement question:', error);
            this.showError('Erreur : ' + error.message);
        } finally {
            this.isLoading = false;
        }
    }
    
    displayQuestion(question) {
        const questionNumber = document.getElementById('question-number');
        const questionText = document.getElementById('question-text');
        
        if (questionNumber) {
            questionNumber.textContent = `Question ${this.currentQuestion}`;
        }
        
        if (questionText) {
            questionText.textContent = question.text;
        }
    }
    
    createResponseButtons(question) {
        const container = document.getElementById('response-buttons');
        if (!container) return;
        
        container.innerHTML = '';
        
        const scale = question.scale;
        const options = question.options;
        const numButtons = scale === '1-4' ? 4 : 7;
        
        for (let i = 0; i < numButtons; i++) {
            const button = document.createElement('button');
            button.className = 'response-btn';
            button.innerHTML = `${i + 1}. ${options[i]}`;
            button.onclick = () => this.selectManualResponse(i + 1);
            container.appendChild(button);
        }
    }
    
    toggleSpecialMessage(show) {
        const specialMessage = document.getElementById('special-message');
        if (specialMessage) {
            specialMessage.style.display = show ? 'block' : 'none';
        }
    }
    
    updateProgress() {
        const progress = (this.currentQuestion - 1) / 30 * 100;
        const progressFill = document.getElementById('progress-fill');
        const currentQuestionEl = document.getElementById('current-question');
        const progressPercent = document.getElementById('progress-percent');
        
        if (progressFill) {
            progressFill.style.width = progress + '%';
        }
        
        if (currentQuestionEl) {
            currentQuestionEl.textContent = this.currentQuestion;
        }
        
        if (progressPercent) {
            progressPercent.textContent = Math.round(progress);
        }
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentQuestion <= 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentQuestion >= 30;
        }
    }
    
    async selectManualResponse(score) {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            
            const response = await fetch('/api/save_manual_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    question_num: this.currentQuestion,
                    score: score
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showResponseConfirmation(result.response_text, 'Manuel');
                
                if (result.is_complete) {
                    // Questionnaire terminé
                    setTimeout(() => {
                        window.location.href = `/resultat/${this.sessionId}`;
                    }, 2000);
                } else {
                    // Question suivante
                    setTimeout(() => {
                        this.loadQuestion(result.next_question);
                    }, 2000);
                }
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('Erreur sauvegarde manuelle:', error);
            this.showError('Erreur : ' + error.message);
        } finally {
            this.isLoading = false;
        }
    }
    
    showResponseConfirmation(responseText, type) {
        const responseBox = document.getElementById('current-response');
        const responseTextEl = document.getElementById('response-text');
        
        if (responseBox && responseTextEl) {
            responseTextEl.textContent = `${type}: ${responseText}`;
            responseBox.style.display = 'block';
            
            // Masquer après 3 secondes
            setTimeout(() => {
                responseBox.style.display = 'none';
            }, 3000);
        }
    }
    
    async playQuestionAudio() {
        try {
            const response = await fetch(`/api/get_audio/${this.currentQuestion}`);
            
            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Arrêter l'audio précédent
                this.stopAudio();
                
                // Créer et jouer le nouvel audio
                this.currentAudio = new Audio(audioUrl);
                this.currentAudio.play();
                
                // Afficher le bouton stop
                this.toggleAudioButtons(true);
                
                this.currentAudio.onended = () => {
                    this.toggleAudioButtons(false);
                };
                
            } else {
                throw new Error('Audio non disponible');
            }
        } catch (error) {
            console.error('Erreur lecture audio:', error);
            this.showError('Erreur : Impossible de lire l\'audio');
        }
    }
    
    stopAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        this.toggleAudioButtons(false);
    }
    
    toggleAudioButtons(playing) {
        const playBtn = document.getElementById('play-audio-btn');
        const stopBtn = document.getElementById('stop-audio-btn');
        
        if (playBtn && stopBtn) {
            playBtn.style.display = playing ? 'none' : 'inline-block';
            stopBtn.style.display = playing ? 'inline-block' : 'none';
        }
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
}

// Fonctions globales pour l'interface
function previousQuestion() {
    if (window.questionnaireManager && window.questionnaireManager.currentQuestion > 1) {
        window.questionnaireManager.loadQuestion(window.questionnaireManager.currentQuestion - 1);
    }
}

function nextQuestion() {
    if (window.questionnaireManager && window.questionnaireManager.currentQuestion < 30) {
        window.questionnaireManager.loadQuestion(window.questionnaireManager.currentQuestion + 1);
    }
}

function playQuestionAudio() {
    if (window.questionnaireManager) {
        window.questionnaireManager.playQuestionAudio();
    }
}

function stopAudio() {
    if (window.questionnaireManager) {
        window.questionnaireManager.stopAudio();
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le gestionnaire de questionnaire
    window.questionnaireManager = new QuestionnaireManager();
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
