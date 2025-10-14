#!/usr/bin/env python3
"""
Script de test complet pour le flux de reconnaissance vocale
"""

import requests
import json
import time

def test_complete_flow():
    """Tester le flux complet : session -> question -> voice"""
    print("TEST: Flux complet de reconnaissance vocale...")
    
    base_url = "https://questionnaire-c30.onrender.com"
    
    # 1. Créer une session
    print("\n1. Creation de session...")
    session_data = {
        "initials": "TEST",
        "birth_date": "01/01/1990",
        "today_date": "14/10/2025",
        "audio_enabled": True,
        "mode": "Continu (Web Speech)"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/start_session",
            headers={"Content-Type": "application/json"},
            json=session_data,
            timeout=10
        )
        
        print(f"Session Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"Session ID: {session_id}")
            
            # 2. Tester l'API process_voice
            print("\n2. Test process_voice...")
            voice_data = {
                "session_id": session_id,
                "question_num": 1,
                "transcript": "beaucoup"
            }
            
            response = requests.post(
                f"{base_url}/api/process_voice",
                headers={"Content-Type": "application/json"},
                json=voice_data,
                timeout=10
            )
            
            print(f"Voice Status: {response.status_code}")
            print(f"Voice Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Voice Result: {json.dumps(result, indent=2)}")
            else:
                print(f"Voice ERROR: {response.status_code} - {response.text}")
                
        else:
            print(f"Session ERROR: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERREUR: {e}")

if __name__ == "__main__":
    test_complete_flow()
