"""
Gestionnaire audio simplifié pour le web (sans pygame ni speech_recognition)
Version optimisée avec reconnaissance vocale TRÈS améliorée
+ Remplacement "assez" → "plutôt"
+ Désactivation chiffres pour échelle 1-4 (Q1-28)
"""

import requests
import threading
import time
import tempfile
import os
import hashlib
import wave
import struct
from typing import Optional, List
from pathlib import Path
import re


class AudioHandlerSimple:
    """Gestionnaire audio simplifié pour le web"""

    def __init__(
        self,
        api_key: str = None,
        use_gemini_tts: bool = False,
        use_pro_model: bool = True,
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_CLOUD_API_KEY")
        if not self.api_key:
            print("ATTENTION: Cle API Google Cloud non configuree!")

        self.use_gemini_tts = use_gemini_tts

        if use_gemini_tts:
            if use_pro_model:
                self.model = "gemini-2.5-pro-preview-tts"
                print("Utilisation de Gemini Pro TTS (voix Achernar - qualite premium)")
            else:
                self.model = "gemini-2.5-flash-preview-tts"
                print("Utilisation de Gemini Flash TTS (voix Achernar - economique)")

            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            self.voice_name = "Achernar"
        else:
            self.api_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
            self.voice_name = "fr-FR-Neural2-A"
            self.language_code = "fr-FR"
            print("Utilisation de Cloud Text-to-Speech (voix Neural2)")

        self.is_speaking = False
        self.current_thread = None
        self.stop_flag = threading.Event()
        self._lock = threading.Lock()

        cache_type = (
            f"{self.model if use_gemini_tts else 'cloud_tts'}_{self.voice_name}"
        )

        project_dir = Path(__file__).parent
        self.cache_dir = project_dir / "static" / "audio_cache" / cache_type
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        print(f"Cache permanent : {self.cache_dir}")

    def _get_cache_path(self, text: str, use_style_prompt: bool = True) -> Path:
        """Génère le chemin de cache pour un texte donné"""
        cache_key = f"{self.voice_name}_{text}"
        text_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{text_hash}.wav"

    def get_audio_path(self, text: str) -> Optional[Path]:
        """Retourne le chemin du fichier audio (pour lecture web)"""
        cache_path = self._get_cache_path(text)
        if cache_path.exists():
            return cache_path
        return None

    def get_cache_info(self) -> dict:
        """Retourne des informations détaillées sur le cache"""
        try:
            files = list(self.cache_dir.glob("*.wav"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                "count": len(files),
                "size_bytes": total_size,
                "size_mb": total_size / (1024 * 1024),
                "path": str(self.cache_dir),
            }
        except:
            return {
                "count": 0,
                "size_bytes": 0,
                "size_mb": 0,
                "path": str(self.cache_dir),
            }


class VoiceRecognitionHandler:
    """Gestionnaire de reconnaissance vocale TRÈS amélioré"""

    def __init__(self):
        self.recognition_enabled = False
        print("INFO Reconnaissance vocale configurée pour Web Speech API uniquement")

    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour la comparaison"""
        text = text.lower().strip()
        # Supprimer accents
        text = text.replace("é", "e").replace("è", "e").replace("ê", "e")
        text = text.replace("à", "a").replace("â", "a")
        text = text.replace("ù", "u").replace("û", "u")
        text = text.replace("ô", "o")
        text = text.replace("ç", "c")
        # Supprimer ponctuation
        text = re.sub(r"[^\w\s]", " ", text)
        # Supprimer espaces multiples
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _contains_word(self, text: str, keywords: list) -> bool:
        """
        Vérifie si un mot de la liste est présent (mot entier ou expression)
        """
        text_normalized = self._normalize_text(text)

        for keyword in keywords:
            keyword_normalized = self._normalize_text(keyword)

            # Vérifier si le mot/expression est présent avec délimiteurs
            pattern = r"\b" + re.escape(keyword_normalized) + r"\b"
            if re.search(pattern, text_normalized):
                return True

            # Aussi vérifier sans délimiteurs pour les expressions multi-mots
            if " " in keyword_normalized and keyword_normalized in text_normalized:
                return True

        return False

    def interpret_response(self, text: str, scale: str) -> Optional[int]:
        """Interprète une réponse vocale et retourne le score"""
        if not text:
            return None

        text_original = text
        text = self._normalize_text(text)

        print(f"DEBUG - Texte original: '{text_original}'")
        print(f"DEBUG - Texte normalisé: '{text}' (echelle: {scale})")
        print(f"DEBUG - Longueur: {len(text)} caracteres")

        # Rejeter les phrases trop longues (> 40 caractères)
        if len(text) > 40:
            print("ERREUR - Phrase trop longue, probablement pas une reponse valide")
            return None

        # Rejeter les mots non-valides
        invalid_words = [
            "passer",
            "passe",
            "pass",
            "suivant",
            "suivante",
            "next",
            "skip",
            "ignorer",
            "attendre",
            "attends",
        ]
        if any(word in text.split() for word in invalid_words):
            print("ERREUR - Mot non-valide detecte")
            return None

        if scale == "1-4":
            # ============================================
            # 🚫 ÉCHELLE 1-4 : PAS DE CHIFFRES (Q1-28)
            # ============================================
            # ORDRE DE PRIORITÉ (du plus spécifique au plus général)

            # 1. Expressions multi-mots (PRIORITÉ MAXIMALE)
            if self._contains_word(
                text, ["pas du tout", "jamais", "aucunement", "nullement"]
            ):
                print("OK - Reconnu: 1 (pas du tout)")
                return 1

            if self._contains_word(text, ["un peu", "legerement", "peu"]):
                print("OK - Reconnu: 2 (un peu)")
                return 2

            # ============================================
            # 🔄 REMPLACEMENT "ASSEZ" → "PLUTÔT"
            # ============================================
            if self._contains_word(
                text,
                [
                    "plutot",  # 🆕 Remplacement principal
                    "moyennement",
                    "moderement",
                    # Anciennes variantes "assez" conservées pour compatibilité
                    "assez",
                    "ac",
                    "asset",
                    "ah c'est",
                    "ah cest",
                    "ah ses",
                    "ah set",
                ],
            ):
                print("OK - Reconnu: 3 (plutôt)")
                return 3

            # 2. "Beaucoup" et variantes (CRITIQUE - amélioration majeure)
            beaucoup_variants = [
                "beaucoup",
                "boucoup",
                "bocoup",
                "boku",
                "bocou",
                "beaucou",
                "beaukou",
                "bokoup",
                "bokou",
                "beacoup",
                "bocou",
                "bocoups",
                "tres",
                "enormement",
                "completement",
                "tout a fait",
                "vraiment",
            ]
            if self._contains_word(text, beaucoup_variants):
                print("OK - Reconnu: 4 (beaucoup)")
                return 4

            # ============================================
            # 🚫 CHIFFRES DÉSACTIVÉS POUR ÉCHELLE 1-4
            # ============================================
            # Les chiffres arabes et français ne sont PLUS acceptés
            # pour éviter la confusion sur les questions 1-28

            print(f"ERREUR - Aucune correspondance trouvee pour: '{text}'")
            print(
                f"DEBUG - Pour echelle 1-4, utilisez: 'pas du tout', 'un peu', 'plutot', 'beaucoup'"
            )
            return None

        elif scale == "1-7":
            # ============================================
            # ✅ ÉCHELLE 1-7 : CHIFFRES AUTORISÉS (Q29-30)
            # ============================================
            # ORDRE DE PRIORITÉ pour échelle 1-7

            # 1. Expressions qualitatives
            if self._contains_word(
                text, ["tres mauvais", "horrible", "terrible", "nul"]
            ):
                print("OK - Reconnu: 1 (tres mauvais)")
                return 1

            if self._contains_word(text, ["mauvais", "mal", "pas bon"]):
                print("OK - Reconnu: 2 (mauvais)")
                return 2

            if self._contains_word(
                text, ["plutot mauvais", "pas bien", "pas terrible"]
            ):
                print("OK - Reconnu: 3 (plutot mauvais)")
                return 3

            if self._contains_word(text, ["moyen", "neutre", "correct", "ca va"]):
                print("OK - Reconnu: 4 (moyen)")
                return 4

            if self._contains_word(text, ["plutot bon", "plutot bien", "assez bien"]):
                print("OK - Reconnu: 5 (plutot bon)")
                return 5

            if self._contains_word(text, ["bon", "bien"]):
                print("OK - Reconnu: 6 (bon)")
                return 6

            if self._contains_word(
                text, ["tres bon", "excellent", "parfait", "super", "genial"]
            ):
                print("OK - Reconnu: 7 (excellent)")
                return 7

            # 2. Chiffres en français (1-7) - UNIQUEMENT POUR Q29-30
            chiffres_francais_1_7 = {
                "un": 1,
                "une": 1,
                "ain": 1,
                "eun": 1,
                "deux": 2,
                "deu": 2,
                "de": 2,
                "trois": 3,
                "troi": 3,
                "troy": 3,
                "quatre": 4,
                "quatr": 4,
                "quat": 4,
                "cinq": 5,
                "saink": 5,
                "sink": 5,
                "sain": 5,
                "six": 6,
                "si": 6,
                "sis": 6,
                "cis": 6,
                "sept": 7,
                "set": 7,
                "cet": 7,
                "sete": 7,
            }

            words = text.split()
            for word in words:
                if word in chiffres_francais_1_7:
                    score = chiffres_francais_1_7[word]
                    if score <= 7:
                        print(f"OK - Reconnu: {score} (chiffre francais '{word}')")
                        return score

            # 3. Chiffres arabes - UNIQUEMENT POUR Q29-30
            if text in ["1", "2", "3", "4", "5", "6", "7"]:
                score = int(text)
                print(f"OK - Reconnu: {score} (chiffre arabe)")
                return score

            # 4. Recherche de chiffres dans le texte - UNIQUEMENT POUR Q29-30
            digit_match = re.search(r"\b([1-7])\b", text)
            if digit_match:
                score = int(digit_match.group(1))
                print(f"OK - Reconnu: {score} (chiffre trouve dans le texte)")
                return score

        print(f"ERREUR - Aucune correspondance trouvee pour: '{text}'")
        print(f"DEBUG - Mots detectes: {text.split()}")
        return None
