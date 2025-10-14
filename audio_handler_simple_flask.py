"""
Gestionnaire audio simplifié pour le web (sans pygame ni speech_recognition)
Version optimisée avec reconnaissance vocale STRICTE
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
    """Gestionnaire audio simplifié pour le web (sans pygame ni speech_recognition)"""

    def __init__(
        self,
        api_key: str = None,
        use_gemini_tts: bool = False,
        use_pro_model: bool = True,
    ):
        """
        Initialise le gestionnaire audio pour le web
        """
        # Clé API
        self.api_key = api_key or os.environ.get("GOOGLE_CLOUD_API_KEY")
        if not self.api_key:
            print("ATTENTION: Cle API Google Cloud non configuree!")
            print("Definissez GOOGLE_CLOUD_API_KEY dans vos variables d'environnement")

        self.use_gemini_tts = use_gemini_tts

        # Configuration selon l'API choisie
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

        # État
        self.is_speaking = False
        self.current_thread = None
        self.stop_flag = threading.Event()
        self._lock = threading.Lock()

        # CACHE PERMANENT dans le dossier du projet
        cache_type = (
            f"{self.model if use_gemini_tts else 'cloud_tts'}_{self.voice_name}"
        )

        # Dossier de cache permanent
        project_dir = Path(__file__).parent
        self.cache_dir = project_dir / "static" / "audio_cache" / cache_type
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        print(f"Cache permanent : {self.cache_dir}")

    def _get_cache_path(self, text: str, use_style_prompt: bool = True) -> Path:
        """Génère le chemin de cache pour un texte donné"""
        cache_key = f"{self.voice_name}_{text}"
        text_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{text_hash}.wav"

    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 24000) -> bytes:
        """Convertit des données PCM brutes en WAV"""
        import io

        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)

        return wav_buffer.getvalue()

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
    """Gestionnaire de reconnaissance vocale simplifié (Web Speech API uniquement)"""

    def __init__(self):
        self.recognition_enabled = False
        print("INFO Reconnaissance vocale configurée pour Web Speech API uniquement")
        print("INFO Utilisation de JavaScript Web Speech API (client-side)")

    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour la comparaison"""
        # Supprimer ponctuation, mettre en minuscule, supprimer espaces multiples
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)  # Remplacer ponctuation par espace
        text = re.sub(r"\s+", " ", text)  # Supprimer espaces multiples
        return text

    def _is_exact_word_match(self, text: str, keywords: list) -> bool:
        """
        Vérifie si UN mot exact de la liste est présent (pas juste une sous-chaîne)
        """
        text_normalized = self._normalize_text(text)
        words = text_normalized.split()

        for keyword in keywords:
            keyword_normalized = self._normalize_text(keyword)
            # Vérifier mot exact
            if keyword_normalized in words:
                return True
            # OU vérifier expression exacte (pour "pas du tout", "un peu", etc.)
            if keyword_normalized in text_normalized:
                # S'assurer que c'est bien l'expression complète
                # avec des délimiteurs (début, fin, ou espaces)
                pattern = r"\b" + re.escape(keyword_normalized) + r"\b"
                if re.search(pattern, text_normalized):
                    return True

        return False

    def interpret_response(self, text: str, scale: str) -> Optional[int]:
        """Interprète une réponse vocale et retourne le score"""
        if not text:
            return None

        text = text.lower().strip()
        print(f"DEBUG - Texte reconnu: '{text}' (echelle: {scale})")
        print(f"DEBUG - Longueur du texte: {len(text)} caracteres")

        # ✅ CORRECTION : Rejeter les phrases trop longues (> 30 caractères)
        if len(text) > 30:
            print("ERREUR - Phrase trop longue, probablement pas une réponse valide")
            return None

        # Rejeter explicitement les mots non-valides
        invalid_words = [
            "passer",
            "passé",
            "pass",
            "suivant",
            "suivante",
            "next",
            "skip",
            "ignorer",
            "je",
            "pense",
            "que",
        ]
        if any(word in text.split() for word in invalid_words):
            print("ERREUR - Mot non-valide detecte, rejete")
            return None

        if scale == "1-4":
            # ✅ Ordre de priorité : expressions complètes PUIS mots individuels

            # 1. Expressions multi-mots (priorité maximale)
            if self._is_exact_word_match(text, ["pas du tout", "jamais"]):
                print("OK - Reconnu comme: 1 (pas du tout)")
                return 1

            if self._is_exact_word_match(text, ["un peu", "legerement"]):
                print("OK - Reconnu comme: 2 (un peu)")
                return 2

            if self._is_exact_word_match(text, ["assez", "moyennement", "moderement"]):
                print("OK - Reconnu comme: 3 (assez)")
                return 3

            if self._is_exact_word_match(
                text, ["beaucoup", "tres", "enormement", "completement", "tout a fait"]
            ):
                print("OK - Reconnu comme: 4 (beaucoup)")
                return 4

            # 2. Chiffres en français (mots exacts seulement)
            words = text.split()

            if "un" in words or "une" in words:
                print("OK - Reconnu comme: 1 (chiffre 'un')")
                return 1

            if "deux" in words:
                print("OK - Reconnu comme: 2 (chiffre 'deux')")
                return 2

            if "trois" in words or "troi" in words:
                print("OK - Reconnu comme: 3 (chiffre 'trois')")
                return 3

            if "quatre" in words or "quatr" in words:
                print("OK - Reconnu comme: 4 (chiffre 'quatre')")
                return 4

            # 3. Chiffres arabes (si présents seuls)
            if text in ["1", "2", "3", "4"]:
                score = int(text)
                print(f"OK - Reconnu comme: {score} (chiffre)")
                return score

        elif scale == "1-7":
            # Expressions qualitatives
            if self._is_exact_word_match(
                text, ["tres mauvais", "horrible", "terrible"]
            ):
                print("OK - Reconnu comme: 1 (tres mauvais)")
                return 1

            if self._is_exact_word_match(text, ["mauvais", "mal"]):
                print("OK - Reconnu comme: 2 (mauvais)")
                return 2

            if self._is_exact_word_match(text, ["plutot mauvais", "pas bien"]):
                print("OK - Reconnu comme: 3 (plutot mauvais)")
                return 3

            if self._is_exact_word_match(text, ["moyen", "neutre", "correct"]):
                print("OK - Reconnu comme: 4 (moyen)")
                return 4

            if self._is_exact_word_match(
                text, ["plutot bon", "plutot bien", "assez bien"]
            ):
                print("OK - Reconnu comme: 5 (plutot bon)")
                return 5

            if self._is_exact_word_match(text, ["bon", "bien"]):
                print("OK - Reconnu comme: 6 (bon)")
                return 6

            if self._is_exact_word_match(
                text, ["tres bon", "excellent", "parfait", "super"]
            ):
                print("OK - Reconnu comme: 7 (excellent)")
                return 7

            # Chiffres en français (mots exacts)
            words = text.split()
            number_words = {
                "un": 1,
                "une": 1,
                "deux": 2,
                "deu": 2,
                "trois": 3,
                "troi": 3,
                "quatre": 4,
                "quatr": 4,
                "cinq": 5,
                "saink": 5,
                "six": 6,
                "si": 6,
                "sept": 7,
                "set": 7,
            }

            for word in words:
                if word in number_words:
                    score = number_words[word]
                    print(f"OK - Reconnu comme: {score} (mot: '{word}')")
                    return score

            # Chiffres arabes
            if text in ["1", "2", "3", "4", "5", "6", "7"]:
                score = int(text)
                print(f"OK - Reconnu comme: {score} (chiffre)")
                return score

        print(f"ERREUR - Aucune correspondance trouvee pour: '{text}'")
        return None
