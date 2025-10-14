"""
Logique métier du questionnaire EORTC QLQ-C30
"""

import datetime
import re
from typing import Dict, Optional, Tuple


class EORTCQuestionnaire:
    """Classe gérant la logique du questionnaire EORTC QLQ-C30"""

    def __init__(self):
        self.questions = self._setup_questions()

    def _setup_questions(self) -> Dict:
        """Définit toutes les questions du questionnaire EORTC QLQ-C30"""
        return {
            # Questions 1-5 : Capacités physiques générales
            1: {
                "text": "Avez-vous des difficultés à faire certains efforts physiques pénibles comme porter un sac à provisions chargé ou une valise?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            2: {
                "text": "Avez-vous des difficultés à faire une longue promenade?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            3: {
                "text": "Avez-vous des difficultés à faire un petit tour dehors?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            4: {
                "text": "Êtes-vous obligé de rester au lit ou dans un fauteuil pendant la journée?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            5: {
                "text": "Avez-vous besoin d'aide pour manger, vous habiller, faire votre toilette ou aller aux toilettes?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            # Questions 6-28 : Au cours de la semaine passée
            6: {
                "text": "Au cours de la semaine passée : Avez-vous été gêné pour faire votre travail ou vos activités de tous les jours?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            7: {
                "text": "Au cours de la semaine passée : Avez-vous été gêné dans vos activités de loisirs?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            8: {
                "text": "Au cours de la semaine passée : Avez-vous eu le souffle court?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            9: {
                "text": "Au cours de la semaine passée : Avez-vous ressenti de la douleur?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            10: {
                "text": "Au cours de la semaine passée : Avez-vous eu besoin de repos?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            11: {
                "text": "Au cours de la semaine passée : Avez-vous eu des difficultés pour dormir?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            12: {
                "text": "Au cours de la semaine passée : Vous êtes-vous senti faible?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            13: {
                "text": "Au cours de la semaine passée : Avez-vous manqué d'appétit?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            14: {
                "text": "Au cours de la semaine passée : Avez-vous eu des nausées?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            15: {
                "text": "Au cours de la semaine passée : Avez-vous vomi?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            16: {
                "text": "Au cours de la semaine passée : Avez-vous été constipé?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            17: {
                "text": "Au cours de la semaine passée : Avez-vous eu de la diarrhée?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            18: {
                "text": "Au cours de la semaine passée : Étiez-vous fatigué?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            19: {
                "text": "Au cours de la semaine passée : Des douleurs ont-elles perturbé vos activités quotidiennes?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            20: {
                "text": "Au cours de la semaine passée : Avez-vous eu des difficultés à vous concentrer sur certaines choses?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            21: {
                "text": "Au cours de la semaine passée : Vous êtes-vous senti tendu?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            22: {
                "text": "Au cours de la semaine passée : Vous êtes-vous fait du souci?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            23: {
                "text": "Au cours de la semaine passée : Vous êtes-vous senti irritable?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            24: {
                "text": "Au cours de la semaine passée : Vous êtes-vous senti déprimé?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            25: {
                "text": "Au cours de la semaine passée : Avez-vous eu des difficultés pour vous souvenir de certaines choses?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            26: {
                "text": "Au cours de la semaine passée : Votre état physique ou votre traitement médical vous ont-ils gêné dans votre vie familiale?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            27: {
                "text": "Au cours de la semaine passée : Votre état physique ou votre traitement médical vous ont-ils gêné dans vos activités sociales?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            28: {
                "text": "Au cours de la semaine passée : Votre état physique ou votre traitement médical vous ont-ils causé des problèmes financiers?",
                "scale": "1-4",
                "options": ["Pas du tout", "Un peu", "Assez", "Beaucoup"],
            },
            # Questions 29-30 : Évaluation globale (échelle 1-7)
            29: {
                "text": """Comment évalueriez-vous votre état de santé au cours de la semaine passée?
                Sur une échelle de 1 à 7, où 1 signifie "très mauvais" et 7 "excellent".""",
                "scale": "1-7",
                "options": [
                    "Un",
                    "Deux",
                    "Trois",
                    "Quatre",
                    "Cinq",
                    "Six",
                    "Sept",
                ],
            },
            30: {
                "text": """Comment évalueriez-vous l'ensemble de votre qualité de vie au cours de la semaine passée?
                Sur une échelle de 1 à 7, où 1 signifie "très mauvaise" et 7 "excellente".""",
                "scale": "1-7",
                "options": [
                    "Un",
                    "Deux",
                    "Trois",
                    "Quatre",
                    "Cinq",
                    "Six",
                    "Sept",
                ],
            },
        }

    def get_question(self, question_num: int) -> Optional[Dict]:
        """Retourne les détails d'une question"""
        return self.questions.get(question_num)

    def should_read_options(self, question_num: int) -> bool:
        """Détermine si on doit lire les options pour cette question"""
        # Lire les options pour Q1 (première fois échelle 1-4)
        # et Q29 (changement d'échelle vers 1-7)
        return question_num in [1, 29]

    def get_speech_text(self, question_num: int) -> str:
        """Génère le texte à lire vocalement pour une question"""
        question = self.get_question(question_num)
        if not question:
            return ""

        speech_text = f"Question {question_num}. {question['text']}"

        # Ajouter les options si nécessaire
        if self.should_read_options(question_num):
            options = question["options"]
            options_text = f"Répondez par {options[0]}, {', '.join(options[1:-1])}, ou {options[-1]}"
            speech_text += f" {options_text}"

        return speech_text

    def validate_response(self, question_num: int, score: int) -> bool:
        """Valide qu'une réponse est dans la bonne plage"""
        question = self.get_question(question_num)
        if not question:
            return False

        if question["scale"] == "1-4":
            return 1 <= score <= 4
        elif question["scale"] == "1-7":
            return 1 <= score <= 7
        return False

    def parse_date(self, text: str) -> Optional[str]:
        """Parse une date depuis du texte"""
        text = text.lower().strip()

        # Dictionnaire des mois
        months = {
            "janvier": "01",
            "février": "02",
            "fevrier": "02",
            "mars": "03",
            "avril": "04",
            "mai": "05",
            "juin": "06",
            "juillet": "07",
            "août": "08",
            "aout": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "décembre": "12",
            "decembre": "12",
        }

        # Remplacer les noms de mois
        for month_name, month_num in months.items():
            if month_name in text:
                text = text.replace(month_name, month_num)

        # Extraire les nombres
        numbers = re.findall(r"\b\d{1,4}\b", text)

        if len(numbers) >= 3:
            day, month, year = numbers[0], numbers[1], numbers[2]

            try:
                d, m, y = int(day), int(month), int(year)

                # Ajuster l'année si nécessaire
                if y < 100:
                    y += 1900 if y > 30 else 2000

                # Validation
                if 1 <= d <= 31 and 1 <= m <= 12 and 1900 <= y <= 2030:
                    return f"{d:02d}/{m:02d}/{y}"
            except ValueError:
                pass

        return None

    def calculate_statistics(self, responses: Dict) -> Dict:
        """Calcule les statistiques des réponses"""
        valid_responses = [r for r in responses.values() if r.get("score") is not None]
        missed_responses = [r for r in responses.values() if r.get("score") is None]

        stats = {
            "total_questions": 30,
            "answered": len(valid_responses),
            "missed": len(missed_responses),
            "completion_rate": len(valid_responses) / 30 * 100,
        }

        if valid_responses:
            scores = [
                r["score"]
                for r in valid_responses
                if isinstance(r.get("score"), (int, float))
            ]
            if scores:
                stats["average_score"] = sum(scores) / len(scores)

        return stats

    def export_to_dict(self, personal_info: Dict, responses: Dict) -> Dict:
        """Exporte toutes les données en dictionnaire"""
        return {
            "personal_info": personal_info,
            "responses": responses,
            "metadata": {
                "questionnaire": "EORTC QLQ-C30",
                "version": "3.0",
                "completed_at": datetime.datetime.now().isoformat(),
                "statistics": self.calculate_statistics(responses),
            },
        }
