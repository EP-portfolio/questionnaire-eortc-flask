"""
Routes API pour l'application Flask
Gestion AJAX : sessions, questions, reconnaissance vocale, audio
"""

from flask import Blueprint, request, jsonify, current_app, send_file
import datetime
import os
from pathlib import Path

api_bp = Blueprint('api', __name__)

@api_bp.route('/start_session', methods=['POST'])
def start_session():
    """Créer une nouvelle session questionnaire"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['initials', 'birth_date', 'today_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Créer la session en base
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        
        session_id = db.create_session({
            'initials': data['initials'],
            'birth_date': data['birth_date'],
            'today_date': data['today_date'],
            'mode': data.get('mode', 'Standard'),
            'audio_enabled': data.get('audio_enabled', True)
        })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session créée avec succès'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur création session: {str(e)}'}), 500

@api_bp.route('/validate_session/<session_id>', methods=['GET'])
def validate_session(session_id):
    """Valider qu'une session existe"""
    try:
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        session = db.get_session(session_id)
        
        if not session:
            # Retourner 200 avec valid: false au lieu de 400
            return jsonify({
                'valid': False, 
                'error': 'Session invalide',
                'message': 'Session non trouvée'
            })
        
        return jsonify({
            'valid': True,
            'session': {
                'id': session['id'],
                'initials': session['initials'],
                'created_at': session['created_at']
            }
        })
        
    except Exception as e:
        # Retourner 200 avec valid: false au lieu de 500
        return jsonify({
            'valid': False,
            'error': f'Erreur validation session: {str(e)}'
        })

@api_bp.route('/get_question/<int:question_num>', methods=['GET'])
def get_question(question_num):
    """Récupérer une question"""
    try:
        if not (1 <= question_num <= 30):
            return jsonify({'error': 'Numéro de question invalide'}), 400
        
        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({'error': 'Question introuvable'}), 404
        
        # Ajouter le texte de synthèse vocale
        speech_text = current_app.questionnaire.get_speech_text(question_num)
        question['speech_text'] = speech_text
        
        return jsonify({
            'success': True,
            'question': question,
            'question_num': question_num
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur récupération question: {str(e)}'}), 500

@api_bp.route('/process_voice', methods=['POST'])
def process_voice():
    """Traiter une réponse vocale"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['session_id', 'question_num', 'transcript']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        session_id = data['session_id']
        question_num = int(data['question_num'])
        transcript = data['transcript']
        
        # Vérifier que le transcript n'est pas vide
        if not transcript or transcript.strip() == "":
            return jsonify({
                'valid': False,
                'error': 'Aucune parole détectée',
                'message': 'Veuillez parler plus fort ou plus clairement'
            })
        
        # Vérifier que la session existe
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        session = db.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session invalide'}), 400
        
        # Récupérer la question
        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({'error': 'Question introuvable'}), 404
        
        # Interpréter la réponse vocale
        score = current_app.voice_handler.interpret_response(
            transcript, question['scale']
        )
        
        if not score:
            return jsonify({
                'valid': False,
                'error': 'Réponse non reconnue',
                'transcript': transcript,
                'suggestions': question['options']
            })
        
        # Valider la réponse
        if not current_app.questionnaire.validate_response(question_num, score):
            return jsonify({
                'valid': False,
                'error': 'Score invalide',
                'transcript': transcript,
                'score': score
            })
        
        # Sauvegarder en base de données
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        
        success = db.save_response(
            session_id=session_id,
            question_num=question_num,
            question_text=question['text'],
            score=score,
            response_text=f"Vocal: {transcript}",
            transcript=transcript,
            response_type='voice'
        )
        
        if not success:
            return jsonify({'error': 'Erreur sauvegarde'}), 500
        
        # Déterminer la question suivante
        next_question = question_num + 1 if question_num < 30 else None
        
        return jsonify({
            'valid': True,
            'score': score,
            'response_text': question['options'][score-1],
            'next_question': next_question,
            'is_complete': next_question is None
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur traitement vocal: {str(e)}'}), 500

@api_bp.route('/save_manual_response', methods=['POST'])
def save_manual_response():
    """Sauvegarder une réponse manuelle"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['session_id', 'question_num', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        session_id = data['session_id']
        question_num = int(data['question_num'])
        score = int(data['score'])
        
        # Récupérer la question
        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({'error': 'Question introuvable'}), 404
        
        # Valider la réponse
        if not current_app.questionnaire.validate_response(question_num, score):
            return jsonify({'error': 'Score invalide'}), 400
        
        # Sauvegarder en base de données
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        
        success = db.save_response(
            session_id=session_id,
            question_num=question_num,
            question_text=question['text'],
            score=score,
            response_text=f"Manuel: {question['options'][score-1]}",
            response_type='manual'
        )
        
        if not success:
            return jsonify({'error': 'Erreur sauvegarde'}), 500
        
        # Déterminer la question suivante
        next_question = question_num + 1 if question_num < 30 else None
        
        return jsonify({
            'success': True,
            'score': score,
            'response_text': question['options'][score-1],
            'next_question': next_question,
            'is_complete': next_question is None
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur sauvegarde manuelle: {str(e)}'}), 500

@api_bp.route('/get_audio/<int:question_num>')
def get_audio(question_num):
    """Servir fichier audio préenregistré pour une question"""
    try:
        # Chemin vers l'audio préenregistré
        audio_filename = f"question_{question_num}.wav"
        # Chercher dans le sous-dossier Gemini TTS
        audio_path = Path('static/audio_cache/gemini-2.5-pro-preview-tts_Achernar') / audio_filename
        
        print(f"DEBUG: Recherche audio {audio_filename} dans {audio_path}")
        print(f"DEBUG: Chemin absolu: {audio_path.absolute()}")
        print(f"DEBUG: Existe: {audio_path.exists()}")
        
        if audio_path.exists():
            print(f"DEBUG: Audio trouvé, envoi...")
            return send_file(
                str(audio_path),
                mimetype='audio/wav',
                as_attachment=False
            )
        
        # Vérifier s'il y a d'autres fichiers audio dans le cache
        cache_dir = Path('static/audio_cache')
        if cache_dir.exists():
            all_audios = list(cache_dir.glob('*.wav'))
            print(f"DEBUG: Fichiers audio disponibles: {[f.name for f in all_audios]}")
        
        # Fallback : audio de test simple
        return jsonify({'error': f'Audio préenregistré non trouvé: {audio_filename}'}), 404
        
    except Exception as e:
        print(f"DEBUG: Erreur audio: {e}")
        return jsonify({'error': f'Erreur audio: {str(e)}'}), 500

@api_bp.route('/test_audio')
def test_audio():
    """Servir un fichier audio de test pré-généré"""
    try:
        # Utiliser le fichier audio de test pré-généré (déjà créé)
        test_audio_path = Path('static/audio_cache/gemini-2.5-pro-preview-tts_Achernar')
        
        print(f"DEBUG: Recherche test audio dans {test_audio_path}")
        print(f"DEBUG: Existe: {test_audio_path.exists()}")
        
        # Chercher le fichier de test dans le cache
        if test_audio_path.exists():
            # Lister tous les fichiers .wav dans le cache
            wav_files = list(test_audio_path.glob('*.wav'))
            print(f"DEBUG: Fichiers trouvés: {len(wav_files)}")
            if wav_files:
                # Prendre le premier fichier (généralement le test audio)
                print(f"DEBUG: Utilisation du fichier: {wav_files[0]}")
                return send_file(
                    str(wav_files[0]),
                    mimetype='audio/wav',
                    as_attachment=False
                )
        
        # Fallback : créer un fichier audio très simple
        fallback_path = Path('static/audio_cache/test_simple.wav')
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not fallback_path.exists():
            import wave
            import struct
            import math
            
            # Fichier très court et simple
            sample_rate = 22050
            duration = 0.3  # Très court
            frequency = 440
            
            with wave.open(str(fallback_path), 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                
                for i in range(int(sample_rate * duration)):
                    t = i / sample_rate
                    sample = math.sin(2 * math.pi * frequency * t)
                    pcm_sample = int(sample * 32767)
                    wav_file.writeframes(struct.pack('<h', pcm_sample))
        
        return send_file(
            str(fallback_path),
            mimetype='audio/wav',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur test audio: {str(e)}'}), 500

@api_bp.route('/get_session_data/<session_id>')
def get_session_data(session_id):
    """Récupérer les données d'une session"""
    try:
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        
        session_data = db.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Session introuvable'}), 404
        
        responses = db.get_responses(session_id)
        statistics = db.get_session_statistics(session_id)
        
        return jsonify({
            'success': True,
            'session': session_data,
            'responses': responses,
            'statistics': statistics
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur récupération session: {str(e)}'}), 500

@api_bp.route('/complete_session/<session_id>', methods=['POST'])
def complete_session(session_id):
    """Marquer une session comme terminée"""
    try:
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        
        db.update_session_completion(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Session marquée comme terminée'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur finalisation session: {str(e)}'}), 500

@api_bp.route('/export_session/<session_id>')
def export_session(session_id):
    """Exporter les données d'une session"""
    try:
        from models.database_flask import DatabaseManager
        db = DatabaseManager()
        
        export_data = db.export_session_data(session_id)
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur export: {str(e)}'}), 500

@api_bp.route('/health')
def health():
    """Endpoint de santé pour monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'audio_available': current_app.audio_handler is not None
    })

@api_bp.route('/diagnostic')
def diagnostic():
    """Diagnostic complet de l'application"""
    import os
    from pathlib import Path
    
    # Variables d'environnement
    env_vars = {
        'SECRET_KEY': '✅' if os.environ.get('SECRET_KEY') else '❌',
        'GOOGLE_CLOUD_API_KEY': '✅' if os.environ.get('GOOGLE_CLOUD_API_KEY') else '❌',
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'NON DÉFINIE'),
        'AUDIO_ENABLED': os.environ.get('AUDIO_ENABLED', 'NON DÉFINIE'),
    }
    
    # Structure des dossiers
    folders = {
        'data': Path('data').exists(),
        'static': Path('static').exists(),
        'templates': Path('templates').exists(),
        'models': Path('models').exists(),
        'routes': Path('routes').exists(),
    }
    
    # Base de données
    db_path = Path('data/responses.db')
    db_status = {
        'exists': db_path.exists(),
        'size': db_path.stat().st_size if db_path.exists() else 0
    }
    
    if db_path.exists():
        try:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sessions")
                sessions_count = cursor.fetchone()[0]
                db_status['sessions'] = sessions_count
        except Exception as e:
            db_status['error'] = str(e)
    
    return jsonify({
        'environment': env_vars,
        'folders': folders,
        'database': db_status,
        'timestamp': datetime.datetime.now().isoformat()
    })
