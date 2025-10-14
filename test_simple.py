#!/usr/bin/env python3
"""
Test simple pour vérifier les problèmes
"""

import requests
import json

def test_simple():
    """Test simple des endpoints"""
    base_url = "https://questionnaire-c30.onrender.com"
    
    print("=== TEST SIMPLE ===")
    
    # 1. Test health
    print("\n1. Test /api/health")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # 2. Test diagnostic
    print("\n2. Test /api/diagnostic")
    try:
        response = requests.get(f"{base_url}/api/diagnostic", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Environment: {data.get('environment', {})}")
            print(f"Database: {data.get('database', {})}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # 3. Test audio
    print("\n3. Test /api/get_audio/1")
    try:
        response = requests.get(f"{base_url}/api/get_audio/1", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Audio trouvé! Taille: {len(response.content)} bytes")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_simple()
