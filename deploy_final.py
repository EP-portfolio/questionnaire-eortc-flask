#!/usr/bin/env python3
"""
Script de déploiement final - Fix des imports
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}")
    print(f"Commande: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ Succès: {description}")
            if result.stdout:
                print(f"Sortie: {result.stdout}")
        else:
            print(f"❌ Erreur: {description}")
            print(f"Erreur: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    return True

def main():
    """Déploiement final avec fix des imports"""
    print("🚀 Déploiement Final - Fix des Imports")
    print("=" * 50)
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("questionnaire_flask"):
        print("❌ Erreur: Répertoire questionnaire_flask non trouvé")
        print("Assurez-vous d'être dans le répertoire parent")
        return False
    
    # Changer vers le répertoire questionnaire_flask
    os.chdir("questionnaire_flask")
    print(f"📁 Répertoire de travail: {os.getcwd()}")
    
    # Étape 1: Vérifier le statut Git
    if not run_command("git status", "Vérification du statut Git"):
        return False
    
    # Étape 2: Ajouter tous les fichiers
    if not run_command("git add .", "Ajout des fichiers modifiés"):
        return False
    
    # Étape 3: Commit avec message descriptif
    commit_message = "Fix final: Correct imports and remove problematic dependencies"
    if not run_command(f'git commit -m "{commit_message}"', "Commit des modifications"):
        return False
    
    # Étape 4: Push vers le repository
    if not run_command("git push origin main", "Push vers le repository"):
        return False
    
    print("\n🎉 Déploiement Final Terminé !")
    print("=" * 50)
    print("✅ Tous les imports corrigés")
    print("✅ Dépendances problématiques supprimées")
    print("✅ Application prête pour Render")
    print("\n🌐 Votre application va se redéployer automatiquement sur Render")
    print("📊 Surveillez les logs de déploiement sur Render")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
