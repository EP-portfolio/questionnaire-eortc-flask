#!/usr/bin/env python3
"""
Script de génération des fichiers audio pour le questionnaire EORTC QLQ-C30
Génère tous les fichiers audio nécessaires pour le questionnaire
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from questionnaire_logic import EORTCQuestionnaire
from audio_handler_simple_flask import AudioHandlerSimple

def generate_all_audio():
    """Génère tous les fichiers audio nécessaires"""
    print("🎵 Génération des fichiers audio pour le questionnaire EORTC QLQ-C30")
    print("=" * 70)
    
    # Vérifier la clé API
    api_key = os.environ.get('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("❌ ERREUR: Clé API Google Cloud non configurée")
        print("📝 Définissez GOOGLE_CLOUD_API_KEY dans vos variables d'environnement")
        print("🔗 Obtenez votre clé sur: https://console.cloud.google.com/apis/credentials")
        return False
    
    # Initialiser le questionnaire
    questionnaire = EORTCQuestionnaire()
    
    # Initialiser le gestionnaire audio
    audio_handler = AudioHandlerSimple(
        api_key=api_key,
        use_gemini_tts=True,
        use_pro_model=True
    )
    
    # Collecter tous les textes à synthétiser
    texts_to_synthesize = []
    
    print("📋 Collecte des textes à synthétiser...")
    
    # Questions 1-30
    for question_num in range(1, 31):
        speech_text = questionnaire.get_speech_text(question_num)
        if speech_text:
            texts_to_synthesize.append(speech_text)
            print(f"  Q{question_num}: {speech_text[:50]}...")
    
    # Messages d'interface
    interface_messages = [
        "Bienvenue dans le questionnaire EORTC QLQ-C30",
        "Veuillez répondre à la question suivante",
        "Réponse reconnue",
        "Réponse non reconnue, veuillez réessayer",
        "Questionnaire terminé",
        "Merci d'avoir participé au questionnaire"
    ]
    
    for message in interface_messages:
        texts_to_synthesize.append(message)
        print(f"  Interface: {message}")
    
    print(f"\n📊 Total: {len(texts_to_synthesize)} textes à synthétiser")
    
    # Générer les fichiers audio
    print("\n🎵 Génération des fichiers audio...")
    
    def progress_callback(current, total):
        percentage = (current / total) * 100
        print(f"  Progression: {current}/{total} ({percentage:.1f}%)")
    
    try:
        audio_handler.pregenerate_audio(texts_to_synthesize, progress_callback)
        
        # Vérifier le cache
        cache_info = audio_handler.get_cache_info()
        print(f"\n✅ Génération terminée !")
        print(f"📁 Fichiers générés: {cache_info['count']}")
        print(f"💾 Taille du cache: {cache_info['size_mb']:.2f} MB")
        print(f"📂 Dossier: {cache_info['path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False

def main():
    """Point d'entrée principal"""
    success = generate_all_audio()
    
    if success:
        print("\n🎉 Génération audio terminée avec succès !")
        print("🌐 Votre application est maintenant prête avec tous les fichiers audio")
    else:
        print("\n❌ Échec de la génération audio")
        print("🔧 Vérifiez votre clé API Google Cloud")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
