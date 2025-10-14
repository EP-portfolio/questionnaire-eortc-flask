#!/usr/bin/env python3
"""
Générateur de clé secrète sécurisée pour Flask
"""

import secrets
import string


def generate_secret_key():
    """Génère une clé secrète sécurisée"""
    # Caractères autorisés pour une clé secrète
    characters = string.ascii_letters + string.digits + "!@#$%^&*"

    # Générer une clé de 64 caractères
    secret_key = "".join(secrets.choice(characters) for _ in range(64))

    return secret_key


def main():
    """Génère et affiche la clé secrète"""
    print("=== GÉNÉRATEUR DE CLÉ SECRÈTE FLASK ===")
    print()

    # Générer la clé
    secret_key = generate_secret_key()

    print("Clé secrète générée :")
    print(f"SECRET_KEY = {secret_key}")
    print()
    print("IMPORTANT :")
    print("1. Copiez cette cle")
    print("2. Collez-la dans Render comme variable d'environnement")
    print("3. NE PARTAGEZ JAMAIS cette cle")
    print("4. Gardez-la secrete")
    print()
    print("Configuration Render :")
    print("   Variable: SECRET_KEY")
    print(f"   Valeur: {secret_key}")


if __name__ == "__main__":
    main()
