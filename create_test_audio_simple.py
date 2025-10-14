#!/usr/bin/env python3
"""
Créer un fichier audio de test simple et rapide
"""

import os
import sys
from pathlib import Path
import wave
import struct
import math

def create_simple_test_audio():
    """Créer un fichier audio de test simple"""
    
    # Chemin du fichier
    test_audio_path = Path('static/audio_cache/test_audio_simple.wav')
    test_audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Création du fichier audio de test: {test_audio_path}")
    
    # Paramètres audio
    sample_rate = 22050  # Plus bas pour un fichier plus petit
    duration = 0.5  # Très court
    frequency = 440  # La note A4
    
    # Créer le fichier WAV
    with wave.open(str(test_audio_path), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Générer l'onde sinusoïdale
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            sample = math.sin(2 * math.pi * frequency * t)
            pcm_sample = int(sample * 32767)
            wav_file.writeframes(struct.pack('<h', pcm_sample))
    
    # Vérifier la taille
    file_size = test_audio_path.stat().st_size
    print(f"✅ Fichier créé: {file_size} bytes")
    print(f"✅ Durée: {duration}s")
    print(f"✅ Fréquence: {frequency}Hz")
    
    return test_audio_path

if __name__ == "__main__":
    try:
        create_simple_test_audio()
        print("\n🎉 Fichier audio de test créé avec succès !")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
