#!/usr/bin/env python3
"""
Script de test pour la reconnaissance vocale
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_handler_simple_flask import VoiceRecognitionHandler

def test_voice_recognition():
    """Tester la reconnaissance vocale avec différents inputs"""
    print("TEST: Reconnaissance vocale...")
    
    handler = VoiceRecognitionHandler()
    
    # Tests pour echelle 1-4
    test_cases_1_4 = [
        ("pas du tout", 1),
        ("un peu", 2),
        ("assez", 3),
        ("beaucoup", 4),
        ("peu", 2),
        ("pas", 1),
        ("tres", 4),
        ("completement", 4),
    ]
    
    print("\nTests echelle 1-4:")
    for text, expected in test_cases_1_4:
        result = handler.interpret_response(text, "1-4")
        status = "OK" if result == expected else "ERREUR"
        print(f"  {status} '{text}' -> {result} (attendu: {expected})")
    
    # Tests pour echelle 1-7
    test_cases_1_7 = [
        ("tres mauvais", 1),
        ("mauvais", 2),
        ("moyen", 4),
        ("bon", 6),
        ("excellent", 7),
        ("un", 1),
        ("deux", 2),
        ("trois", 3),
        ("quatre", 4),
        ("cinq", 5),
        ("six", 6),
        ("sept", 7),
    ]
    
    print("\nTests echelle 1-7:")
    for text, expected in test_cases_1_7:
        result = handler.interpret_response(text, "1-7")
        status = "OK" if result == expected else "ERREUR"
        print(f"  {status} '{text}' -> {result} (attendu: {expected})")

if __name__ == "__main__":
    test_voice_recognition()
