#!/usr/bin/env python3
"""
Script pour créer un fichier audio de test simple
"""

import wave
import struct
import math
import os

def create_test_audio():
    """Crée un fichier audio de test simple"""
    
    # Paramètres audio
    sample_rate = 44100
    duration = 2  # 2 secondes
    frequency = 440  # La note A4
    
    # Créer le dossier audio_cache s'il n'existe pas
    os.makedirs('static/audio_cache', exist_ok=True)
    
    # Générer un signal sinusoïdal
    samples = []
    for i in range(int(sample_rate * duration)):
        # Signal sinusoïdal avec enveloppe
        t = i / sample_rate
        envelope = math.exp(-t * 2)  # Enveloppe exponentielle
        sample = envelope * math.sin(2 * math.pi * frequency * t)
        samples.append(sample)
    
    # Convertir en format 16-bit PCM
    pcm_data = []
    for sample in samples:
        # Limiter l'amplitude et convertir en 16-bit
        pcm_sample = max(-1, min(1, sample))
        pcm_data.append(int(pcm_sample * 32767))
    
    # Créer le fichier WAV
    with wave.open('static/audio_cache/test_audio.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Écrire les données PCM
        for sample in pcm_data:
            wav_file.writeframes(struct.pack('<h', sample))
    
    print("✅ Fichier audio de test créé: static/audio_cache/test_audio.wav")
    return True

if __name__ == "__main__":
    create_test_audio()
