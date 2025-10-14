#!/usr/bin/env python3
"""
Script pour vérifier les audios préenregistrés
"""

import os
from pathlib import Path

def check_audios():
    """Vérifier les audios préenregistrés"""
    print("=== VÉRIFICATION DES AUDIOS PRÉENREGISTRÉS ===")
    
    # Dossier des audios
    audio_dir = Path('static/audio_cache')
    
    if not audio_dir.exists():
        print("ERREUR: Dossier static/audio_cache n'existe pas")
        return
    
    print(f"OK: Dossier trouve: {audio_dir}")
    
    # Verifier les audios des questions
    print("\nAudios des questions:")
    for i in range(1, 31):
        audio_file = audio_dir / f"question_{i}.wav"
        if audio_file.exists():
            size = audio_file.stat().st_size
            print(f"  Q{i:2d}: OK ({size:,} bytes)")
        else:
            print(f"  Q{i:2d}: MANQUANT")
    
    # Verifier l'audio de test
    print("\nAudio de test:")
    test_audio = audio_dir / "test_audio.wav"
    if test_audio.exists():
        size = test_audio.stat().st_size
        print(f"  test_audio.wav: OK ({size:,} bytes)")
    else:
        print("  test_audio.wav: MANQUANT")
    
    # Lister tous les fichiers audio
    print("\nTous les fichiers audio:")
    audio_files = list(audio_dir.glob('*.wav'))
    if audio_files:
        for file in sorted(audio_files):
            size = file.stat().st_size
            print(f"  {file.name}: {size:,} bytes")
    else:
        print("  Aucun fichier audio trouve")
    
    print(f"\nTotal: {len(audio_files)} fichiers audio")

if __name__ == "__main__":
    check_audios()
