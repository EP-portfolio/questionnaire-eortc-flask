#!/usr/bin/env python3
"""
Script pour vérifier que tous les fichiers audio sont présents
et créer un mapping question → fichier audio
"""

from pathlib import Path
import hashlib
from questionnaire_logic import EORTCQuestionnaire


def get_audio_hash(text: str, voice_name: str = "Achernar") -> str:
    """Calcule le hash MD5 d'un texte (même logique que AudioHandler)"""
    cache_key = f"{voice_name}_{text}"
    return hashlib.md5(cache_key.encode("utf-8")).hexdigest()


def check_audio_files():
    """Vérifie tous les fichiers audio"""
    print("=" * 70)
    print("🎵 VÉRIFICATION DES FICHIERS AUDIO")
    print("=" * 70)
    print()

    questionnaire = EORTCQuestionnaire()
    audio_cache = Path("static/audio_cache")

    # Trouver tous les fichiers audio
    all_audio_files = {}
    if audio_cache.exists():
        for subdir in audio_cache.glob("*"):
            if subdir.is_dir():
                for wav_file in subdir.glob("*.wav"):
                    all_audio_files[wav_file.stem] = wav_file

    print(f"📁 Dossier cache: {audio_cache}")
    print(f"📊 Fichiers audio trouvés: {len(all_audio_files)}")
    print()

    # Vérifier pour chaque question
    print("🔍 Vérification par question:")
    print("-" * 70)

    missing = []
    found = []

    for q_num in range(1, 31):
        speech_text = questionnaire.get_speech_text(q_num)
        expected_hash = get_audio_hash(speech_text)

        if expected_hash in all_audio_files:
            file_path = all_audio_files[expected_hash]
            file_size = file_path.stat().st_size
            found.append(q_num)
            print(f"✅ Q{q_num:02d}: {file_path.name} ({file_size:,} bytes)")
        else:
            missing.append(q_num)
            print(f"❌ Q{q_num:02d}: MANQUANT (hash attendu: {expected_hash})")

    print()
    print("=" * 70)
    print(f"✅ Fichiers trouvés: {len(found)}/30")
    print(f"❌ Fichiers manquants: {len(missing)}/30")

    if missing:
        print()
        print("⚠️  Questions sans audio:")
        print(f"   {', '.join(map(str, missing))}")
        print()
        print("💡 Solution: Régénérer les audios avec pregenerate_audios.py")
    else:
        print()
        print("🎉 Tous les fichiers audio sont présents !")

    print()

    # Créer un fichier de mapping
    mapping_file = Path("audio_mapping.txt")
    with open(mapping_file, "w", encoding="utf-8") as f:
        f.write("# Mapping Question → Fichier Audio\n")
        f.write("# Format: Q<num> → <hash>.wav\n\n")
        for q_num in range(1, 31):
            speech_text = questionnaire.get_speech_text(q_num)
            expected_hash = get_audio_hash(speech_text)
            if expected_hash in all_audio_files:
                f.write(f"Q{q_num:02d} → {expected_hash}.wav ✓\n")
            else:
                f.write(f"Q{q_num:02d} → {expected_hash}.wav ✗ MANQUANT\n")

    print(f"📝 Fichier de mapping créé: {mapping_file}")
    print()

    return len(missing) == 0


if __name__ == "__main__":
    import sys

    success = check_audio_files()
    sys.exit(0 if success else 1)
