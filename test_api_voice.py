#!/usr/bin/env python3
"""
Script de test pour l'API process_voice
"""

import requests
import json

def test_api_voice():
    """Tester l'API process_voice avec des données réelles"""
    print("TEST: API process_voice...")
    
    # URL de l'application (local ou production)
    base_url = "https://questionnaire-c30.onrender.com"
    
    # Données de test
    test_data = {
        "session_id": "test-session-123",
        "question_num": 1,
        "transcript": "beaucoup"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/process_voice",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERREUR: {e}")

if __name__ == "__main__":
    test_api_voice()
