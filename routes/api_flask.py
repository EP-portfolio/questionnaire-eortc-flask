"""
Routes API pour l'application Flask
Gestion AJAX : sessions, questions, reconnaissance vocale, audio
Version corrigée avec système de hash MD5 pour les audios
"""

from flask import Blueprint, request, jsonify, current_app, send_file
import datetime
import os
import hashlib
from pathlib import Path

api_bp = Blueprint("api", __name__)


@api_bp.route("/start_session", methods=["POST"])
def start_session():
    """Créer une nouvelle session questionnaire"""
    try:
        data = request.get_json()

        # Validation des données
        required_fields = ["initials", "birth_date", "today_date"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400

        # Créer la session en base
        from models.database_flask import DatabaseManager

        db = DatabaseManager()

        session_id = db.create_session(
            {
                "initials": data["initials"],
                "birth_date": data["birth_date"],
                "today_date": data["today_date"],
                "mode": data.get("mode", "Standard"),
                "audio_enabled": data.get("audio_enabled", True),
            }
        )

        return jsonify(
            {
                "success": True,
                "session_id": session_id,
                "message": "Session créée avec succès",
            }
        )

    except Exception as e:
        return jsonify({"error": f"Erreur création session: {str(e)}"}), 500


@api_bp.route("/validate_session/<session_id>", methods=["GET"])
def validate_session(session_id):
    """Valider qu'une session existe"""
    try:
        from models.database_flask import DatabaseManager

        db = DatabaseManager()
        session = db.get_session(session_id)

        if not session:
            return jsonify(
                {
                    "valid": False,
                    "error": "Session invalide",
                    "message": "Session non trouvée",
                }
            )

        return jsonify(
            {
                "valid": True,
                "session": {
                    "id": session["id"],
                    "initials": session["initials"],
                    "created_at": session["created_at"],
                },
            }
        )

    except Exception as e:
        return jsonify(
            {"valid": False, "error": f"Erreur validation session: {str(e)}"}
        )


@api_bp.route("/get_question/<int:question_num>", methods=["GET"])
def get_question(question_num):
    """Récupérer une question (incluant Q0)"""
    try:
        # ✅ MODIFICATION : Accepter la question 0
        if not (0 <= question_num <= 30):
            return jsonify({"error": "Numéro de question invalide"}), 400

        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({"error": "Question introuvable"}), 404

        # Ajouter le texte de synthèse vocale
        speech_text = current_app.questionnaire.get_speech_text(question_num)
        question["speech_text"] = speech_text

        return jsonify(
            {"success": True, "question": question, "question_num": question_num}
        )

    except Exception as e:
        return jsonify({"error": f"Erreur récupération question: {str(e)}"}), 500


@api_bp.route("/process_voice", methods=["POST"])
def process_voice():
    """Traiter une réponse vocale"""
    try:
        data = request.get_json()

        # Validation des données
        required_fields = ["session_id", "question_num", "transcript"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400

        session_id = data["session_id"]
        question_num = int(data["question_num"])
        transcript = data["transcript"]

        # Vérifier que le transcript n'est pas vide
        if not transcript or transcript.strip() == "":
            return jsonify(
                {
                    "valid": False,
                    "error": "Aucune parole détectée",
                    "message": "Veuillez parler plus fort ou plus clairement",
                }
            )

        # Vérifier que la session existe
        from models.database_flask import DatabaseManager

        db = DatabaseManager()
        session = db.get_session(session_id)
        if not session:
            return jsonify({"error": "Session invalide"}), 400

        # Récupérer la question
        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({"error": "Question introuvable"}), 404

        # Interpréter la réponse vocale
        score = current_app.voice_handler.interpret_response(
            transcript, question["scale"]
        )

        if not score:
            return jsonify(
                {
                    "valid": False,
                    "error": "Réponse non reconnue",
                    "transcript": transcript,
                    "suggestions": question["options"],
                }
            )

        # Valider la réponse
        if not current_app.questionnaire.validate_response(question_num, score):
            return jsonify(
                {
                    "valid": False,
                    "error": "Score invalide",
                    "transcript": transcript,
                    "score": score,
                }
            )

        # Sauvegarder en base de données
        from models.database_flask import DatabaseManager

        db = DatabaseManager()

        success = db.save_response(
            session_id=session_id,
            question_num=question_num,
            question_text=question["text"],
            score=score,
            response_text=f"Vocal: {transcript}",
            transcript=transcript,
            response_type="voice",
        )

        if not success:
            return jsonify({"error": "Erreur sauvegarde"}), 500

        # Déterminer la question suivante
        next_question = question_num + 1 if question_num < 30 else None

        return jsonify(
            {
                "valid": True,
                "score": score,
                "response_text": question["options"][score - 1],
                "next_question": next_question,
                "is_complete": next_question is None,
            }
        )

    except Exception as e:
        return jsonify({"error": f"Erreur traitement vocal: {str(e)}"}), 500


@api_bp.route("/save_manual_response", methods=["POST"])
def save_manual_response():
    """Sauvegarder une réponse manuelle"""
    try:
        data = request.get_json()

        # Validation des données
        required_fields = ["session_id", "question_num", "score"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400

        session_id = data["session_id"]
        question_num = int(data["question_num"])
        score = int(data["score"])

        # Récupérer la question
        question = current_app.questionnaire.get_question(question_num)
        if not question:
            return jsonify({"error": "Question introuvable"}), 404

        # Valider la réponse
        if not current_app.questionnaire.validate_response(question_num, score):
            return jsonify({"error": "Score invalide"}), 400

        # Sauvegarder en base de données
        from models.database_flask import DatabaseManager

        db = DatabaseManager()

        success = db.save_response(
            session_id=session_id,
            question_num=question_num,
            question_text=question["text"],
            score=score,
            response_text=f"Manuel: {question['options'][score-1]}",
            response_type="manual",
        )

        if not success:
            return jsonify({"error": "Erreur sauvegarde"}), 500

        # Déterminer la question suivante
        next_question = question_num + 1 if question_num < 30 else None

        return jsonify(
            {
                "success": True,
                "score": score,
                "response_text": question["options"][score - 1],
                "next_question": next_question,
                "is_complete": next_question is None,
            }
        )

    except Exception as e:
        return jsonify({"error": f"Erreur sauvegarde manuelle: {str(e)}"}), 500


def _get_audio_cache_path(text: str) -> Path:
    """
    Calculer le chemin du fichier audio avec la même logique que audio_handler
    Utilise le hash MD5 pour retrouver le fichier
    """
    # Utiliser la même logique que dans AudioHandlerSimple._get_cache_path()
    voice_name = "Achernar"
    cache_key = f"{voice_name}_{text}"
    text_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()

    # Chercher dans tous les sous-dossiers de cache
    cache_base = Path("static/audio_cache")

    # Chercher le fichier dans tous les sous-dossiers
    for cache_dir in cache_base.glob("*"):
        if cache_dir.is_dir():
            audio_file = cache_dir / f"{text_hash}.wav"
            if audio_file.exists():
                return audio_file

    # Fallback : chercher directement dans le dossier de base
    audio_file = cache_base / f"{text_hash}.wav"
    if audio_file.exists():
        return audio_file

    return None


@api_bp.route("/get_audio/<int:question_num>")
def get_audio(question_num):
    """Servir fichier audio préenregistré pour une question (incluant Q0)"""
    try:
        # Générer le texte de la question (même logique que lors de la pré-génération)
        from questionnaire_logic import EORTCQuestionnaire

        questionnaire = EORTCQuestionnaire()

        # ✅ MODIFICATION : Accepter la question 0
        if not (0 <= question_num <= 30):
            return jsonify({"error": "Numéro de question invalide"}), 400

        speech_text = questionnaire.get_speech_text(question_num)

        print(f"DEBUG: Question {question_num}")
        print(f"DEBUG: Texte: {speech_text[:80]}...")

        # Utiliser le hash MD5 pour trouver le fichier
        audio_path = _get_audio_cache_path(speech_text)

        if audio_path and audio_path.exists():
            print(f"DEBUG: Fichier trouvé: {audio_path.name}")
            return send_file(str(audio_path), mimetype="audio/wav", as_attachment=False)
        else:
            print(f"DEBUG: Aucun fichier audio trouvé pour la question {question_num}")
            return (
                jsonify(
                    {
                        "error": f"Audio préenregistré non trouvé pour question {question_num}"
                    }
                ),
                404,
            )

    except Exception as e:
        print(f"DEBUG: Erreur audio: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Erreur audio: {str(e)}"}), 500


@api_bp.route("/test_audio")
def test_audio():
    """Servir un fichier audio de test"""
    try:
        cache_dir = Path("static/audio_cache")

        print(f"DEBUG: Recherche test audio dans {cache_dir}")

        # Chercher le fichier de test avec le hash
        test_text = "Ceci est un test audio. Si vous entendez ce message, l'audio fonctionne correctement."
        test_audio_path = _get_audio_cache_path(test_text)

        if test_audio_path and test_audio_path.exists():
            print(f"DEBUG: Fichier test trouvé: {test_audio_path.name}")
            return send_file(
                str(test_audio_path), mimetype="audio/wav", as_attachment=False
            )

        # Fallback : chercher n'importe quel fichier .wav
        if cache_dir.exists():
            for subdir in cache_dir.glob("*"):
                if subdir.is_dir():
                    wav_files = list(subdir.glob("*.wav"))
                    if wav_files:
                        print(
                            f"DEBUG: Utilisation du premier fichier trouvé: {wav_files[0].name}"
                        )
                        return send_file(
                            str(wav_files[0]), mimetype="audio/wav", as_attachment=False
                        )

        return jsonify({"error": "Aucun fichier audio de test trouvé"}), 404

    except Exception as e:
        print(f"DEBUG: Erreur test audio: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Erreur test audio: {str(e)}"}), 500


@api_bp.route("/get_session_data/<session_id>")
def get_session_data(session_id):
    """Récupérer les données d'une session"""
    try:
        from models.database_flask import DatabaseManager

        db = DatabaseManager()

        session_data = db.get_session(session_id)
        if not session_data:
            return jsonify({"error": "Session introuvable"}), 404

        responses = db.get_responses(session_id)
        statistics = db.get_session_statistics(session_id)

        return jsonify(
            {
                "success": True,
                "session": session_data,
                "responses": responses,
                "statistics": statistics,
            }
        )

    except Exception as e:
        return jsonify({"error": f"Erreur récupération session: {str(e)}"}), 500


@api_bp.route("/complete_session/<session_id>", methods=["POST"])
def complete_session(session_id):
    """Marquer une session comme terminée"""
    try:
        from models.database_flask import DatabaseManager

        db = DatabaseManager()

        db.update_session_completion(session_id)

        return jsonify({"success": True, "message": "Session marquée comme terminée"})

    except Exception as e:
        return jsonify({"error": f"Erreur finalisation session: {str(e)}"}), 500


@api_bp.route("/export_session/<session_id>")
def export_session(session_id):
    """Exporter les données d'une session"""
    try:
        from models.database_flask import DatabaseManager

        db = DatabaseManager()

        export_data = db.export_session_data(session_id)

        return jsonify({"success": True, "data": export_data})

    except Exception as e:
        return jsonify({"error": f"Erreur export: {str(e)}"}), 500


@api_bp.route("/health")
def health():
    """Endpoint de santé pour monitoring"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "audio_available": current_app.audio_handler is not None,
        }
    )


@api_bp.route("/diagnostic")
def diagnostic():
    """Diagnostic complet de l'application"""
    import os
    from pathlib import Path

    # Variables d'environnement
    env_vars = {
        "SECRET_KEY": "✅" if os.environ.get("SECRET_KEY") else "❌",
        "GOOGLE_CLOUD_API_KEY": (
            "✅" if os.environ.get("GOOGLE_CLOUD_API_KEY") else "❌"
        ),
        "FLASK_ENV": os.environ.get("FLASK_ENV", "NON DÉFINIE"),
        "AUDIO_ENABLED": os.environ.get("AUDIO_ENABLED", "NON DÉFINIE"),
    }

    # Structure des dossiers
    folders = {
        "data": Path("data").exists(),
        "static": Path("static").exists(),
        "templates": Path("templates").exists(),
        "models": Path("models").exists(),
        "routes": Path("routes").exists(),
    }

    # Fichiers audio détaillés
    audio_cache = Path("static/audio_cache")
    audio_files = []
    total_audio_size = 0

    if audio_cache.exists():
        for subdir in audio_cache.glob("*"):
            if subdir.is_dir():
                wav_files = list(subdir.glob("*.wav"))
                if len(wav_files) > 0:
                    folder_size = sum(f.stat().st_size for f in wav_files)
                    total_audio_size += folder_size
                    audio_files.append(
                        {
                            "folder": subdir.name,
                            "count": len(wav_files),
                            "size_mb": folder_size / (1024 * 1024),
                            "files": [
                                f.name for f in wav_files[:5]
                            ],  # Premiers 5 fichiers
                        }
                    )

    # Test de correspondance question → audio
    from questionnaire_logic import EORTCQuestionnaire
    import hashlib

    questionnaire = EORTCQuestionnaire()
    audio_mapping = []

    for q_num in range(1, min(6, 31)):  # Tester les 5 premières questions
        speech_text = questionnaire.get_speech_text(q_num)
        voice_name = "Achernar"
        cache_key = f"{voice_name}_{speech_text}"
        expected_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()

        # Chercher le fichier
        found = False
        if audio_cache.exists():
            for subdir in audio_cache.glob("*"):
                if subdir.is_dir():
                    audio_file = subdir / f"{expected_hash}.wav"
                    if audio_file.exists():
                        found = True
                        audio_mapping.append(
                            {
                                "question": q_num,
                                "hash": expected_hash,
                                "found": True,
                                "size": audio_file.stat().st_size,
                            }
                        )
                        break

        if not found:
            audio_mapping.append(
                {"question": q_num, "hash": expected_hash, "found": False}
            )

    # Base de données
    db_path = Path("data/responses.db")
    db_status = {
        "exists": db_path.exists(),
        "size": db_path.stat().st_size if db_path.exists() else 0,
    }

    if db_path.exists():
        try:
            import sqlite3

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sessions")
                sessions_count = cursor.fetchone()[0]
                db_status["sessions"] = sessions_count
        except Exception as e:
            db_status["error"] = str(e)

    return jsonify(
        {
            "environment": env_vars,
            "folders": folders,
            "audio_cache": {
                "folders": audio_files,
                "total_files": sum(f["count"] for f in audio_files),
                "total_size_mb": total_audio_size / (1024 * 1024),
            },
            "audio_mapping_test": audio_mapping,
            "database": db_status,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    )


@api_bp.route("/get_result_audio/<result_type>")
def get_result_audio(result_type):
    """Servir l'audio préenregistré pour la page de résultat"""
    try:
        print(f"DEBUG: Demande audio résultat - type: {result_type}")

        # Définir les textes selon le type de résultat
        # ✅ IMPORTANT : Ces textes doivent être EXACTEMENT identiques à ceux de pregenerate_audios.py
        if result_type == "complete":
            # Message pour questionnaire complet (30/30)
            audio_text = """Félicitations, vous avez terminé le questionnaire. 
        Vous avez répondu à 30 questions sur 30. 
        Toutes les questions ont été répondues.
        Vous pouvez maintenant télécharger vos résultats ou recommencer un nouveau questionnaire."""
        elif result_type == "incomplete":
            # Message pour questionnaire incomplet
            # Note: Ce texte est générique, l'audio réel peut avoir des variations
            audio_text = """Félicitations, vous avez terminé le questionnaire. 
        Vous avez répondu à 29 questions sur 30. 
        1 questions restent sans réponse.
        Vous pouvez maintenant télécharger vos résultats ou recommencer un nouveau questionnaire."""
        else:
            return jsonify({"error": "Type de résultat invalide"}), 400

        print(f"DEBUG: Texte audio: {audio_text[:50]}...")

        # Utiliser le hash MD5 pour trouver le fichier
        audio_path = _get_audio_cache_path(audio_text)

        if audio_path and audio_path.exists():
            print(f"DEBUG: Fichier audio trouvé: {audio_path.name}")
            return send_file(str(audio_path), mimetype="audio/wav", as_attachment=False)
        else:
            print(f"DEBUG: Aucun fichier audio trouvé pour type: {result_type}")
            return (
                jsonify(
                    {
                        "error": f"Audio préenregistré non trouvé pour résultat {result_type}",
                        "message": "Utilisez la synthèse vocale comme fallback",
                    }
                ),
                404,
            )

    except Exception as e:
        print(f"DEBUG: Erreur audio résultat: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Erreur audio: {str(e)}"}), 500


@api_bp.route("/get_result_audio_dynamic/<session_id>")
def get_result_audio_dynamic(session_id):
    """Servir l'audio préenregistré basé sur les statistiques réelles de la session"""
    try:
        from models.database_flask import DatabaseManager

        db = DatabaseManager()
        stats = db.get_session_statistics(session_id)

        print(f"DEBUG: Stats session {session_id}: {stats}")

        # Choisir le message selon le nombre de questions répondues
        # ✅ IMPORTANT : Ces textes doivent être EXACTEMENT identiques à ceux de pregenerate_audios.py
        if stats["answered"] == 30:
            # Message complet
            audio_text = """Félicitations, vous avez terminé le questionnaire. 
        Vous avez répondu à 30 questions sur 30. 
        Toutes les questions ont été répondues.
        Vous pouvez maintenant télécharger vos résultats ou recommencer un nouveau questionnaire."""
        else:
            # Message incomplet (utiliser le message générique pré-enregistré)
            # Note: L'audio pré-généré dit "29 questions" mais sera utilisé pour tous les cas incomplets
            audio_text = """Félicitations, vous avez terminé le questionnaire. 
        Vous avez répondu à 29 questions sur 30. 
        1 questions restent sans réponse.
        Vous pouvez maintenant télécharger vos résultats ou recommencer un nouveau questionnaire."""

        # Trouver l'audio correspondant
        audio_path = _get_audio_cache_path(audio_text)

        if audio_path and audio_path.exists():
            print(f"DEBUG: Fichier audio trouvé: {audio_path.name}")
            return send_file(str(audio_path), mimetype="audio/wav", as_attachment=False)
        else:
            print(f"DEBUG: Aucun fichier audio trouvé")
            return jsonify({"error": "Audio non trouvé", "fallback": "use_tts"}), 404

    except Exception as e:
        print(f"DEBUG: Erreur audio résultat dynamique: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/transcribe_chunk", methods=["POST"])
def transcribe_chunk():
    """
    Transcrit un chunk audio (pour Firefox/Safari)
    Utilise faster-whisper (version corrigée pour Python 3.13)
    """
    try:
        audio_file = request.files.get("audio")

        if not audio_file:
            return jsonify({"error": "No audio"}), 400

        # ✅ Utiliser faster-whisper (version corrigée)
        from faster_whisper import WhisperModel
        import tempfile
        import os

        # Charger le modèle (mettre en cache global pour ne charger qu'une fois)
        if not hasattr(current_app, "whisper_model"):
            print("📥 Chargement modèle faster-whisper 'tiny' (une seule fois)...")
            try:
                # ✅ CORRECTION : Désactiver tqdm pour éviter l'erreur _lock
                import faster_whisper

                faster_whisper.utils.tqdm = lambda *args, **kwargs: None

                current_app.whisper_model = WhisperModel(
                    "tiny",
                    device="cpu",
                    compute_type="int8",  # Plus léger en mémoire
                    cpu_threads=1,  # Limiter l'utilisation CPU
                )
                print("✅ Modèle faster-whisper chargé")
            except Exception as model_error:
                print(f"❌ Erreur chargement modèle: {model_error}")
                return jsonify({"error": "Model loading failed"}), 500

        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            audio_file.save(tmp.name)
            temp_path = tmp.name

        try:
            # Transcription avec faster-whisper (paramètres optimisés)
            segments, info = current_app.whisper_model.transcribe(
                temp_path,
                language="fr",
                beam_size=1,  # Plus rapide
                best_of=1,  # Plus rapide
                temperature=0.0,  # Plus déterministe
                vad_filter=True,  # Filtre de détection de voix
                vad_parameters=dict(min_silence_duration_ms=500),  # Éviter les silences
            )

            # Extraire le texte (faster-whisper retourne des segments)
            transcript = ""
            for segment in segments:
                transcript += segment.text

            transcript = transcript.strip()

            print(f"📝 Transcription faster-whisper: {transcript}")
            print(
                f"📊 Info: {info.language} (confiance: {info.language_probability:.2f})"
            )

            return jsonify({"success": True, "transcript": transcript})

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        print(f"❌ Erreur transcription: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
