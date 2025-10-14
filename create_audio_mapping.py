#!/usr/bin/env python3
"""
Script pour créer un mapping des fichiers audio
"""

import os
from pathlib import Path
import shutil

def create_audio_mapping():
    """Créer des liens symboliques ou copies des fichiers audio avec des noms simples"""
    
    # Dossier source (fichiers avec hash)
    source_dir = Path('static/audio_cache/gemini-2.5-pro-preview-tts_Achernar')
    
    # Dossier destination (noms simples)
    dest_dir = Path('static/audio_cache')
    
    if not source_dir.exists():
        print("ERREUR: Dossier source introuvable")
        return
    
    # Lister tous les fichiers .wav
    wav_files = list(source_dir.glob('*.wav'))
    print(f"Fichiers audio trouvés: {len(wav_files)}")
    
    # Créer des copies avec des noms simples
    for i, wav_file in enumerate(wav_files[:30], 1):  # Limiter à 30 questions
        dest_file = dest_dir / f"question_{i}.wav"
        
        try:
            # Copier le fichier
            shutil.copy2(wav_file, dest_file)
            print(f"OK Copie: {wav_file.name} -> question_{i}.wav")
        except Exception as e:
            print(f"ERREUR copie {i}: {e}")
    
    # Créer aussi un fichier de test
    if wav_files:
        test_file = dest_dir / "test_audio.wav"
        try:
            shutil.copy2(wav_files[0], test_file)
            print(f"OK Fichier de test cree: test_audio.wav")
        except Exception as e:
            print(f"ERREUR test audio: {e}")
    
    print(f"\nOK Mapping termine !")
    print(f"Fichiers créés dans: {dest_dir}")

if __name__ == "__main__":
    create_audio_mapping()
