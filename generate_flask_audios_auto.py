#!/usr/bin/env python3
"""
Script pour pré-générer tous les audios du questionnaire
Version automatique sans confirmation
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from questionnaire_logic import EORTCQuestionnaire
from audio_handler_simple_flask import AudioHandlerSimple

def pregenerate_all_audios():
    """Pré-génère tous les audios du questionnaire"""

    print("=" * 70)
    print("GENERATION DES AUDIOS DU QUESTIONNAIRE EORTC QLQ-C30")
    print("=" * 70)

    # Récupérer la clé API
    api_key = os.environ.get("GOOGLE_CLOUD_API_KEY")
    if not api_key:
        print("\nERREUR: Variable GOOGLE_CLOUD_API_KEY non definie")
        print("\nSolution:")
        print("  export GOOGLE_CLOUD_API_KEY='votre_cle_ici'")
        return

    print(f"Clé API detectee: {api_key[:15]}...{api_key[-10:]}")

    # Initialiser le questionnaire
    questionnaire = EORTCQuestionnaire()

    # Initialiser le gestionnaire audio avec Gemini Pro TTS
    print("\nInitialisation de Gemini Pro TTS (voix Achernar)...")
    audio_handler = AudioHandlerSimple(
        api_key=api_key, use_gemini_tts=True, use_pro_model=True
    )

    # Collecter tous les textes à générer
    texts_to_generate = []

    # 0. Message de test audio (NOUVEAU)
    test_audio_text = "Ceci est un test audio. Si vous entendez ce message, l'audio fonctionne correctement."
    texts_to_generate.append(("Test audio", test_audio_text))

    # 1. Message de bienvenue
    welcome_text = """Bienvenue sur le Questionnaire C30. 
        Ce questionnaire évalue votre qualité de vie. 
        Il comporte 30 questions.
        Vous avez la possibilité pour chaque question de répondre oralement en cliquant sur le bouton rouge avec un micro.
        Vous pouvez également répondre manuellement en cliquant sur la réponse correspondante.
        Veuillez saisir vos initiales, votre date de naissance, et confirmer la date d'aujourd'hui."""
    texts_to_generate.append(("Message de bienvenue", welcome_text))

    # 2. Les 30 questions avec leurs options
    for q_num in range(1, 31):
        question_data = questionnaire.get_question(q_num)
        if question_data:
            speech_text = questionnaire.get_speech_text(q_num)
            texts_to_generate.append((f"Question {q_num}", speech_text))

    # 3. Messages d'aide
    help_messages = {
        "Initiales": "Saisissez vos initiales. Par exemple, A B pour André Bernard.",
        "Naissance": "Sélectionnez votre date de naissance dans le calendrier.",
        "Audio": "Activez pour entendre les questions.",
        "Erreur réponse": "Réponse non reconnue. Veuillez réessayer ou utilisez les boutons.",
        "Aucune parole": "Aucune parole détectée. Veuillez réessayer.",
        "Parole non comprise": "Parole non comprise. Veuillez réessayer.",
        "Attention initiales": "Attention. Veuillez saisir vos initiales avant de continuer.",
        "Réponses 1-4": "Les réponses possibles sont : pas du tout, un peu, assez, beaucoup",
        "Réponses 1-7": "Les réponses possibles sont : un, deux, trois, quatre, cinq, six, sept",
    }

    for name, text in help_messages.items():
        texts_to_generate.append((f"Aide: {name}", text))

    # 4. Message de résultat (format général pour toutes les situations)
    result_texts = [
        """Félicitations, vous avez terminé le questionnaire. 
        Vous avez répondu à 30 questions sur 30. 
        Toutes les questions ont été répondues.
        Vous pouvez maintenant télécharger vos résultats ou recommencer un nouveau questionnaire.""",
        """Félicitations, vous avez terminé le questionnaire. 
        Vous avez répondu à 29 questions sur 30. 
        1 questions restent sans réponse.
        Vous pouvez maintenant télécharger vos résultats ou recommencer un nouveau questionnaire.""",
    ]

    for idx, text in enumerate(result_texts):
        texts_to_generate.append((f"Message de résultat {idx+1}", text))

    print(f"\nTotal de textes à pré-générer: {len(texts_to_generate)}")

    # Vérifier le cache actuel
    cache_info = audio_handler.get_cache_info()
    print(
        f"\nCache actuel: {cache_info['count']} fichiers ({cache_info['size_mb']:.2f} MB)"
    )
    print(f"Emplacement: {cache_info['path']}")

    print("\nATTENTION:")
    print("  • Cette opération peut prendre 5-10 minutes")
    print("  • Vous serez facturé pour la génération des nouveaux audios")
    print(
        f"  • Coût estimé: ~{len(texts_to_generate) * 500 / 1000000 * 21:.2f} € (si tous nouveaux)"
    )

    print("\n" + "=" * 70)
    print("DEBUT DE LA PRE-GENERATION")
    print("=" * 70 + "\n")

    # Pré-générer tous les audios
    only_texts = [text for name, text in texts_to_generate]

    def progress_callback(current, total):
        percent = (current / total) * 100
        bar_length = 50
        filled = int(bar_length * current / total)
        bar = "=" * filled + "-" * (bar_length - filled)
        print(
            f"\r  Progression: [{bar}] {percent:.1f}% ({current}/{total})",
            end="",
            flush=True,
        )

    audio_handler.pregenerate_audio(only_texts, progress_callback)

    print("\n")

    # Afficher les statistiques finales
    final_cache_info = audio_handler.get_cache_info()
    print("\n" + "=" * 70)
    print("PRE-GENERATION TERMINEE")
    print("=" * 70)
    print(f"\nStatistiques du cache:")
    print(f"   • Fichiers: {final_cache_info['count']}")
    print(f"   • Taille: {final_cache_info['size_mb']:.2f} MB")
    print(f"   • Emplacement: {final_cache_info['path']}")

    print(f"\nTous les audios sont maintenant en cache !")
    print(
        f"Vous pouvez lancer l'application, les questions seront lues instantanément."
    )
    print(f"\nConseil: Conservez le dossier .audio_cache pour ne pas régénérer")
    print(
        f"\nN'oubliez pas de pusher le dossier .audio_cache sur Git pour Streamlit Cloud"
    )


if __name__ == "__main__":
    try:
        pregenerate_all_audios()
    except KeyboardInterrupt:
        print("\n\nInterrompu par l'utilisateur")
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback

        traceback.print_exc()
