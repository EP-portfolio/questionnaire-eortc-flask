/**
 * Logique principale du questionnaire Flask
 * Version corrigée avec audio automatique et logs détaillés
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
        // Vérifier qu'on est bien sur la page du questionnaire
        const isQuestionnairePage = window.location.pathname.includes('/questionnaire');

        if (!isQuestionnairePage) {
            console.log('DEBUG: Pas sur la page questionnaire, n\'initialise pas le manager');
            return;
        }

        // Récupérer l'ID de session depuis l'URL
        this.sessionId = new URLSearchParams(window.location.search).get('session_id');

        console.log('DEBUG: QuestionnaireManager.init() appelé');
        console.log('DEBUG: URL complète:', window.location.href);
        console.log('DEBUG: Session ID extrait:', this.sessionId);

        if (!this.sessionId) {
            console.error('Session ID manquant');
            window.location.href = '/accueil';
            return;
        }

        console.log('Session ID récupéré:', this.sessionId);

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

                // TOUJOURS lancer l'audio automatiquement
                console.log('🔊 Lancement automatique de l\'audio dans 1 seconde...');
                setTimeout(() => {
                    console.log('🔊 Appel de playQuestionAudio()');
                    this.playQuestionAudio();
                }, 1000);
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
        const questionSpeech = document.getElementById('question-speech');
        const questionSpeechText = document.getElementById('question-speech-text');

        if (questionNumber) {
            questionNumber.textContent = `Question ${this.currentQuestion}`;
        }

        // Afficher le texte COURT de la question
        if (questionText) {
            questionText.textContent = question.text;
        }

        // Afficher le texte COMPLET (avec options) dans une zone séparée
        if (questionSpeech && questionSpeechText && question.speech_text) {
            questionSpeechText.textContent = question.speech_text;
            questionSpeech.style.display = 'block';
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
                    setTimeout(() => {
                        window.location.href = `/resultat/${this.sessionId}`;
                    }, 2000);
                } else {
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

            setTimeout(() => {
                responseBox.style.display = 'none';
            }, 3000);
        }
    }

    async playQuestionAudio() {
        try {
            console.log(`🔊 DEBUG: Tentative de lecture audio pour question ${this.currentQuestion}`);

            const statusText = document.getElementById('audio-status-text');
            if (statusText) {
                statusText.textContent = '⏳ Chargement de l\'audio...';
                statusText.style.color = '#fff';
            }

            const response = await fetch(`/api/get_audio/${this.currentQuestion}`);

            console.log(`🔊 DEBUG: Réponse serveur - Status: ${response.status}`);

            if (response.ok) {
                console.log('🔊 DEBUG: Réponse OK, création du blob...');
                const audioBlob = await response.blob();
                console.log(`🔊 DEBUG: Blob créé - Taille: ${audioBlob.size} bytes`);

                const audioUrl = URL.createObjectURL(audioBlob);
                console.log(`🔊 DEBUG: URL créée: ${audioUrl}`);

                this.stopAudio();

                this.currentAudio = new Audio(audioUrl);

                this.currentAudio.onerror = (e) => {
                    console.error('❌ Erreur lecture audio:', e);
                    this.showError('Erreur : Impossible de lire l\'audio');
                    this.toggleAudioButtons(false);
                    if (statusText) {
                        statusText.textContent = '❌ Erreur de lecture audio';
                    }
                };

                this.currentAudio.play().then(() => {
                    console.log('✅ Audio lancé avec succès');
                    this.toggleAudioButtons(true);
                    if (statusText) {
                        statusText.textContent = '▶️ Lecture en cours...';
                    }
                }).catch(err => {
                    console.error('❌ Erreur play():', err);
                    this.showError('Erreur : Impossible de lire l\'audio');
                    this.toggleAudioButtons(false);
                    if (statusText) {
                        statusText.textContent = '❌ Erreur de lecture';
                    }
                });

                this.currentAudio.onended = () => {
                    console.log('✅ Audio terminé');
                    this.toggleAudioButtons(false);
                    if (statusText) {
                        statusText.textContent = '✅ Lecture terminée - Vous pouvez répondre';
                    }
                };

            } else {
                const errorData = await response.json();
                console.error('❌ Erreur serveur:', errorData);

                if (statusText) {
                    statusText.textContent = `⚠️ ${errorData.error || 'Audio non disponible'}`;
                }

                throw new Error(errorData.error || 'Audio non disponible');
            }
        } catch (error) {
            console.error('❌ Erreur lecture audio:', error);
            this.showError('Audio indisponible pour cette question');

            const statusText = document.getElementById('audio-status-text');
            if (statusText) {
                statusText.textContent = '⚠️ Audio non disponible pour cette question';
            }
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
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        window.questionnaireManager = new QuestionnaireManager();
        console.log('✅ QuestionnaireManager initialisé');
    }, 100);
});