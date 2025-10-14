#!/usr/bin/env python3
"""
Script de déploiement simplifié pour le questionnaire EORTC QLQ-C30
"""

import os
import sys
from pathlib import Path

def show_deployment_guide():
    print("=" * 60)
    print("DEPLOIEMENT EN LIGNE - Questionnaire EORTC QLQ-C30")
    print("=" * 60)
    print()
    print("Choisissez votre plateforme de déploiement :")
    print()
    print("1. Render (Recommandé - Gratuit, automatique)")
    print("2. Railway (Simple et rapide)")
    print("3. PythonAnywhere (Spécialisé Python)")
    print("4. Heroku (Classique mais payant)")
    print()
    print("0. Annuler")
    print()
    
    choice = input("Votre choix (1-4) : ").strip()
    return choice

def deploy_render():
    print("DEPLOIEMENT SUR RENDER")
    print("=" * 30)
    print()
    print("ETAPES :")
    print("1. Allez sur https://render.com")
    print("2. Créez un compte ou connectez-vous")
    print("3. Cliquez sur 'New +' -> 'Web Service'")
    print("4. Connectez votre repository Git")
    print("5. Configurez :")
    print("   - Name: questionnaire-eortc")
    print("   - Environment: Python")
    print("   - Build Command: pip install -r requirements_flask.txt")
    print("   - Start Command: python app_flask.py")
    print("6. Ajoutez les variables d'environnement :")
    print("   - SECRET_KEY: votre-cle-secrete")
    print("   - FLASK_DEBUG: False")
    print("   - AUDIO_ENABLED: True")
    print("7. Cliquez sur 'Create Web Service'")
    print()
    print("Le déploiement prendra 2-3 minutes")
    print("Votre app sera accessible sur : https://questionnaire-eortc.onrender.com")

def deploy_railway():
    print("DEPLOIEMENT SUR RAILWAY")
    print("=" * 30)
    print()
    print("ETAPES :")
    print("1. Allez sur https://railway.app")
    print("2. Créez un compte ou connectez-vous")
    print("3. Cliquez sur 'New Project'")
    print("4. Sélectionnez 'Deploy from GitHub repo'")
    print("5. Choisissez votre repository")
    print("6. Railway détectera automatiquement Python")
    print("7. Ajoutez les variables d'environnement :")
    print("   - SECRET_KEY: votre-cle-secrete")
    print("   - FLASK_DEBUG: False")
    print("   - AUDIO_ENABLED: True")
    print("8. Le déploiement se lance automatiquement")
    print()
    print("Le déploiement prendra 1-2 minutes")
    print("Votre app sera accessible sur : https://votre-projet.railway.app")

def deploy_pythonanywhere():
    print("DEPLOIEMENT SUR PYTHONANYWHERE")
    print("=" * 30)
    print()
    print("ETAPES :")
    print("1. Allez sur https://www.pythonanywhere.com")
    print("2. Créez un compte gratuit")
    print("3. Allez dans 'Files' -> 'Upload a file'")
    print("4. Uploadez tous les fichiers du projet")
    print("5. Allez dans 'Web' -> 'Add a new web app'")
    print("6. Choisissez 'Flask' et Python 3.10")
    print("7. Configurez le WSGI file :")
    print("   import sys")
    print("   path = '/home/votre-username/questionnaire_flask'")
    print("   if path not in sys.path:")
    print("       sys.path.append(path)")
    print("   from app_flask import app as application")
    print("8. Redémarrez l'application")
    print()
    print("Le déploiement prendra 5-10 minutes")
    print("Votre app sera accessible sur : https://votre-username.pythonanywhere.com")

def create_github_repo():
    print("CREATION D'UN REPOSITORY GITHUB")
    print("=" * 30)
    print()
    print("ETAPES :")
    print("1. Allez sur https://github.com")
    print("2. Cliquez sur 'New repository'")
    print("3. Nom : questionnaire-eortc-flask")
    print("4. Description : Questionnaire EORTC QLQ-C30 avec reconnaissance vocale")
    print("5. Public ou Private selon vos préférences")
    print("6. Ne cochez PAS 'Add README'")
    print("7. Cliquez sur 'Create repository'")
    print()
    print("Ensuite, dans votre terminal :")
    print("git init")
    print("git add .")
    print("git commit -m 'Initial commit'")
    print("git branch -M main")
    print("git remote add origin https://github.com/votre-username/questionnaire-eortc-flask.git")
    print("git push -u origin main")
    print()
    print("Repository créé et code uploadé !")

def main():
    print("Questionnaire EORTC QLQ-C30 - Déploiement en ligne")
    print("=" * 60)
    
    # Vérifier que tous les fichiers nécessaires existent
    required_files = [
        'app_flask.py',
        'requirements_flask.txt',
        'config_flask.py',
        'models/database_flask.py',
        'routes/main_flask.py',
        'routes/api_flask.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"Fichiers manquants : {', '.join(missing_files)}")
        return
    
    print("Tous les fichiers sont présents")
    print()
    
    # Créer un repository GitHub d'abord
    print("Vous devez d'abord créer un repository GitHub")
    input("Appuyez sur Entrée quand c'est fait...")
    
    # Afficher le menu
    choice = show_deployment_guide()
    
    if choice == '0':
        print("Déploiement annulé")
        return
    
    if choice == '1':
        deploy_render()
    elif choice == '2':
        deploy_railway()
    elif choice == '3':
        deploy_pythonanywhere()
    elif choice == '4':
        print("Heroku nécessite une configuration plus complexe")
        print("Consultez DEPLOYMENT_flask.md pour plus de détails")
    else:
        print("Choix invalide")
        return
    
    print()
    print("DEPLOIEMENT TERMINE !")
    print("=" * 30)
    print("Fonctionnalités déployées :")
    print("- Reconnaissance vocale continue")
    print("- Interface accessible")
    print("- Export des données")
    print("- Conformité RGPD")
    print()
    print("Configuration recommandée :")
    print("- SECRET_KEY : Changez la clé par défaut")
    print("- GOOGLE_CLOUD_API_KEY : Ajoutez votre clé pour l'audio")
    print("- FLASK_DEBUG : False en production")
    print()
    print("Documentation : README_flask.md")
    print("Guide de déploiement : DEPLOYMENT_flask.md")

if __name__ == "__main__":
    main()
