"""
Gestionnaire audio simplifié pour le web (sans pygame ni speech_recognition)
Version optimisée pour le déploiement sur Render avec Python 3.13
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

        Args:
            api_key: Clé API Google Cloud
            use_gemini_tts: True pour Gemini TTS (Achernar), False pour Cloud TTS (Neural2)
            use_pro_model: True pour Gemini Pro TTS, False pour Flash TTS
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

    def _synthesize_speech_gemini(
        self, text: str, add_style_prompt: bool = True
    ) -> Optional[bytes]:
        """Appelle Gemini TTS API avec instructions de style"""
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}

        if add_style_prompt:
            styled_text = f"En français de France standard, avec une diction claire et neutre : {text}"
        else:
            styled_text = text

        payload = {
            "contents": [{"parts": [{"text": styled_text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": self.voice_name}
                    }
                },
            },
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                import base64

                pcm_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                pcm_data = base64.b64decode(pcm_b64)
                wav_data = self._pcm_to_wav(pcm_data)
                return wav_data
            else:
                print(f"ERROR Erreur Gemini TTS: {response.status_code}")
                return None

        except Exception as e:
            print(f"ERROR Erreur Gemini TTS: {e}")
            return None

    def _synthesize_speech_cloud(self, text: str) -> Optional[bytes]:
        """Appelle Cloud Text-to-Speech API"""
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": self.api_key}

        payload = {
            "audioConfig": {
                "audioEncoding": "LINEAR16",
                "pitch": 0,
                "speakingRate": 1,
                "sampleRateHertz": 24000,
            },
            "input": {"text": text},
            "voice": {"languageCode": self.language_code, "name": self.voice_name},
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                import base64

                pcm_data = base64.b64decode(data["audioContent"])
                wav_data = self._pcm_to_wav(pcm_data)
                return wav_data
            else:
                print(f"ERROR Erreur Cloud TTS: {response.status_code}")
                return None

        except Exception as e:
            print(f"ERROR Erreur Cloud TTS: {e}")
            return None

    def _synthesize_speech(self, text: str) -> Optional[bytes]:
        """Synthétise la parole (dispatch vers la bonne API)"""
        if not self.api_key:
            print("ERROR Impossible de synthétiser: clé API manquante")
            return None

        if self.use_gemini_tts:
            return self._synthesize_speech_gemini(text, add_style_prompt=True)
        else:
            return self._synthesize_speech_cloud(text)

    def _get_or_create_audio(self, text: str) -> Optional[Path]:
        """Récupère l'audio depuis le cache ou le génère"""
        cache_path = self._get_cache_path(text, use_style_prompt=True)

        # Vérifier si déjà en cache
        if cache_path.exists():
            if cache_path.stat().st_size > 0:
                return cache_path
            else:
                print(f"WARNING Fichier cache corrompu, régénération...")
                cache_path.unlink()

        # Générer le nouveau fichier audio
        api_name = f"{self.model}" if self.use_gemini_tts else "Cloud TTS"
        print(f"Audio Génération audio via {api_name}...")

        audio_data = self._synthesize_speech(text)

        if audio_data:
            try:
                cache_path.write_bytes(audio_data)
                print(f"OK Audio généré et mis en cache ({len(audio_data)} bytes)")
                return cache_path
            except Exception as e:
                print(f"ERROR Erreur sauvegarde cache: {e}")
                return None

        return None

    def get_audio_path(self, text: str) -> Optional[Path]:
        """Retourne le chemin du fichier audio (pour lecture web)"""
        return self._get_or_create_audio(text)

    def pregenerate_audio(self, texts: List[str], progress_callback=None):
        """Pré-génère tous les audios pour une liste de textes"""
        if not texts:
            return

        print(f"\nAudio Pré-génération de {len(texts)} audios...")
        print(f"Cache Cache : {self.cache_dir}")

        total = len(texts)
        generated = 0
        cached = 0

        for idx, text in enumerate(texts, 1):
            cache_path = self._get_cache_path(text)

            if cache_path.exists() and cache_path.stat().st_size > 0:
                cached += 1
                status = "OK Deja en cache"
            else:
                audio_path = self._get_or_create_audio(text)
                if audio_path:
                    generated += 1
                    status = "OK Genere"
                else:
                    status = "ERREUR"

            print(f"  [{idx}/{total}] {status}")

            if progress_callback:
                progress_callback(idx, total)

            if generated > 0:
                time.sleep(0.5)

        print(f"\nOK Pre-generation terminee !")
        print(f"   • {cached} deja en cache")
        print(f"   • {generated} nouvellement generes")
        print(f"   • Total : {cached + generated}/{total}")

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

    def interpret_response(self, text: str, scale: str) -> Optional[int]:
        """Interprète une réponse vocale et retourne le score"""
        if not text:
            return None

        text = text.lower().strip()
        print(f"🔍 DEBUG - Texte reconnu: '{text}' (échelle: {scale})")

        # Rejeter explicitement les mots non-valides
        invalid_words = [
            "passer", "passé", "pass", "suivant", "suivante", "next", "skip", "ignorer"
        ]
        if any(word in text for word in invalid_words):
            print("❌ Mot non-valide détecté, rejeté")
            return None

        if scale == "1-4":
            if any(word in text for word in ["pas du tout", "pas", "jamais", "aucun"]):
                print("✅ Reconnu comme: 1 (pas du tout)")
                return 1
            elif any(word in text for word in ["peu", "un petit peu", "légèrement"]):
                print("✅ Reconnu comme: 2 (un peu)")
                return 2
            elif any(word in text for word in [
                "assez", "moyennement", "modérément", "aise", "aisez", "aisee", 
                "aisees", "ase", "asez", "asé", "asée", "acer", "acez", 
                "asser", "assey", "passer"
            ]):
                print("✅ Reconnu comme: 3 (assez)")
                return 3
            elif any(word in text for word in [
                "beaucoup", "très", "tout à fait", "complètement", "énormément",
                "boucoup", "bocou", "boku", "bocoup", "beaukou", "beaucou", "bokoup"
            ]):
                print("✅ Reconnu comme: 4 (beaucoup)")
                return 4

        elif scale == "1-7":
            if any(word in text for word in ["très mauvais", "horrible", "terrible"]):
                print("✅ Reconnu comme: 1 (très mauvais)")
                return 1
            elif any(word in text for word in ["mauvais", "mal"]):
                print("✅ Reconnu comme: 2 (mauvais)")
                return 2
            elif any(word in text for word in ["plutôt mauvais", "pas bien"]):
                print("✅ Reconnu comme: 3 (plutôt mauvais)")
                return 3
            elif any(word in text for word in ["moyen", "neutre", "correct"]):
                print("✅ Reconnu comme: 4 (moyen)")
                return 4
            elif any(word in text for word in ["plutôt bon", "plutôt bien", "assez bien"]):
                print("✅ Reconnu comme: 5 (plutôt bon)")
                return 5
            elif any(word in text for word in ["bon", "bien"]):
                print("✅ Reconnu comme: 6 (bon)")
                return 6
            elif any(word in text for word in ["très bon", "excellent", "parfait", "super"]):
                print("✅ Reconnu comme: 7 (excellent)")
                return 7

        # Dictionnaire étendu avec variantes phonétiques
        numbers = {
            # Chiffres en français
            "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7,
            # Chiffres arabes
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
            # Variantes phonétiques pour "1"
            "ain": 1, "eun": 1, "hun": 1, "in": 1, "eune": 1, "eunne": 1,
            # Variantes pour "2"
            "deu": 2, "de": 2,
            # Variantes pour "3"
            "troi": 3, "troy": 3,
            # Variantes pour "4"
            "quatr": 4, "quat": 4,
            # Variantes pour "5"
            "saink": 5, "sink": 5,
            # Variantes pour "6"
            "si": 6, "sis": 6,
            # Variantes pour "7"
            "set": 7, "cet": 7,
        }

        for word, value in numbers.items():
            if word in text:
                if scale == "1-4" and value <= 4:
                    print(f"✅ Reconnu comme: {value} (mot: '{word}')")
                    return value
                elif scale == "1-7" and value <= 7:
                    print(f"✅ Reconnu comme: {value} (mot: '{word}')")
                    return value

        print(f"❌ Aucune correspondance trouvée pour: '{text}'")
        return None
