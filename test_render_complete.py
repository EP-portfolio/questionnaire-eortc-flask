#!/usr/bin/env python3
"""
Test complet de l'application Flask pour Render
"""

import requests
import json
import time

def test_complete_application():
    """Test complet de l'application"""
    print("=== TEST COMPLET DE L'APPLICATION ===")
    
    base_url = "https://questionnaire-c30.onrender.com"
    
    # 1. Test de santé
    print("\n1. Test de santé...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"  Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Health Response: {response.json()}")
        else:
            print(f"  Health Error: {response.text}")
    except Exception as e:
        print(f"  Health Exception: {e}")
    
    # 2. Test diagnostic
    print("\n2. Test diagnostic...")
    try:
        response = requests.get(f"{base_url}/api/diagnostic", timeout=10)
        print(f"  Diagnostic Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Environment: {data.get('environment', {})}")
            print(f"  Folders: {data.get('folders', {})}")
            print(f"  Database: {data.get('database', {})}")
        else:
            print(f"  Diagnostic Error: {response.text}")
    except Exception as e:
        print(f"  Diagnostic Exception: {e}")
    
    # 3. Test session
    print("\n3. Test session...")
    try:
        session_data = {
            "initials": "TEST",
            "birth_date": "01/01/1990",
            "today_date": "14/10/2025",
            "audio_enabled": True,
            "mode": "Continu (Web Speech)"
        }
        
        response = requests.post(
            f"{base_url}/api/start_session",
            headers={"Content-Type": "application/json"},
            json=session_data,
            timeout=10
        )
        
        print(f"  Session Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"  Session ID: {session_id}")
            
            # 4. Test reconnaissance vocale
            print("\n4. Test reconnaissance vocale...")
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
            
            print(f"  Voice Status: {response.status_code}")
            print(f"  Voice Response: {response.text}")
            
        else:
            print(f"  Session Error: {response.text}")
            
    except Exception as e:
        print(f"  Session Exception: {e}")
    
    # 5. Test audio
    print("\n5. Test audio...")
    try:
        response = requests.get(f"{base_url}/api/test_audio", timeout=10)
        print(f"  Audio Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Audio Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  Audio Size: {len(response.content)} bytes")
        else:
            print(f"  Audio Error: {response.text}")
    except Exception as e:
        print(f"  Audio Exception: {e}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_complete_application()
