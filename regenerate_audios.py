#!/usr/bin/env python3
"""
Script pour régénérer tous les fichiers audio avec noms de hash
"""

import os
import hashlib
from pathlib import Path
from questionnaire_logic import EORTCQuestionnaire
from audio_handler_simple_flask import AudioHandlerSimple

def regenerate_all_audios():
    """Régénérer tous les fichiers audio"""
    print("=== REGENERATION DES FICHIERS AUDIO ===")
    
    # Vérifier la clé API
    api_key = os.environ.get('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("ERREUR: GOOGLE_CLOUD_API_KEY non définie")
        print("Utilisation du mode sans API (fichiers vides)")
        return
    
    # Initialiser les composants
    questionnaire = EORTCQuestionnaire()
    audio_handler = AudioHandlerSimple(
        api_key=api_key,
        use_gemini_tts=True,
        use_pro_model=True
    )
    
    # Créer le dossier de cache
    cache_dir = Path('static/audio_cache')
    cache_dir.mkdir(exist_ok=True)
    
    print(f"Cache: {cache_dir}")
    
    # Générer les audios pour toutes les questions
    texts_to_generate = []
    
    # Questions 1-30
    for i in range(1, 31):
        speech_text = questionnaire.get_speech_text(i)
        texts_to_generate.append(speech_text)
        print(f"Q{i:2d}: {speech_text[:50]}...")
    
    # Audio de test
    test_text = "Test audio. Si vous entendez ce message, l'audio fonctionne correctement."
    texts_to_generate.append(test_text)
    print(f"Test: {test_text}")
    
    # Générer tous les audios
    print(f"\nGénération de {len(texts_to_generate)} audios...")
    
    def progress_callback(current, total):
        percent = (current / total) * 100
        print(f"  Progression: {current}/{total} ({percent:.1f}%)")
    
    try:
        audio_handler.pregenerate_audio(texts_to_generate, progress_callback)
        print("\n✅ Génération terminée !")
        
        # Vérifier les fichiers générés
        wav_files = list(cache_dir.glob('*.wav'))
        print(f"Fichiers générés: {len(wav_files)}")
        
        for file in wav_files:
            size = file.stat().st_size
            print(f"  {file.name}: {size:,} bytes")
            
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    regenerate_all_audios()
