#!/usr/bin/env python3
"""
Test local des fichiers audio
"""

import os
from pathlib import Path


def test_audio_files():
    """Tester les fichiers audio localement"""
    print("=== TEST AUDIO LOCAL ===")

    # Vérifier les fichiers audio
    audio_dir = Path("static/audio_cache")

    if not audio_dir.exists():
        print("ERREUR: Dossier static/audio_cache n'existe pas")
        return

    print(f"OK: Dossier trouve: {audio_dir}")

    # Vérifier les fichiers question_*.wav
    print("\nFichiers question_*.wav:")
    for i in range(1, 31):
        audio_file = audio_dir / f"question_{i}.wav"
        if audio_file.exists():
            size = audio_file.stat().st_size
            print(f"  Q{i:2d}: OK ({size:,} bytes)")
        else:
            print(f"  Q{i:2d}: MANQUANT")

    # Vérifier le fichier de test
    print("\nFichier de test:")
    test_audio = audio_dir / "test_audio.wav"
    if test_audio.exists():
        size = test_audio.stat().st_size
        print(f"  test_audio.wav: OK ({size:,} bytes)")
    else:
        print("  test_audio.wav: MANQUANT")

    # Lister tous les fichiers .wav
    print("\nTous les fichiers .wav:")
    wav_files = list(audio_dir.glob("*.wav"))
    if wav_files:
        for file in sorted(wav_files):
            size = file.stat().st_size
            print(f"  {file.name}: {size:,} bytes")
    else:
        print("  Aucun fichier .wav trouve")

    print(f"\nTotal: {len(wav_files)} fichiers audio")


if __name__ == "__main__":
    test_audio_files()
