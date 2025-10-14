"""
Routes API pour l'application Flask
Gestion AJAX : sessions, questions, reconnaissance vocale, audio
"""

from flask import Blueprint, request, jsonify, current_app
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
    """Servir le fichier audio d'une question"""
    try:
        if not current_app.audio_handler:
            return jsonify({'error': 'Audio non disponible'}), 503
        
        # Récupérer la question
        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({'error': 'Question introuvable'}), 404
        
        # Générer le texte de synthèse
        speech_text = current_app.questionnaire.get_speech_text(question_num)
        
        # Récupérer le chemin du fichier audio
        audio_path = current_app.audio_handler.get_audio_path(speech_text)
        
        if not audio_path or not audio_path.exists():
            return jsonify({'error': 'Audio non disponible'}), 404
        
        # Servir le fichier audio
        from flask import send_file
        return send_file(
            str(audio_path),
            mimetype='audio/wav',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur audio: {str(e)}'}), 500

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
