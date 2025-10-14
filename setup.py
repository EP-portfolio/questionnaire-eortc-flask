# Setup minimal pour éviter les problèmes de build
from setuptools import setup, find_packages

setup(
    name="questionnaire-eortc-flask",
    version="1.0.0",
    description="Questionnaire EORTC QLQ-C30 avec reconnaissance vocale",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "pandas>=2.2.0",
        "numpy>=1.24.0",
        "requests==2.31.0",
        "google-cloud-texttospeech==2.16.0",
        "SpeechRecognition==3.10.0",
        "pygame==2.5.2",
        "openpyxl==3.1.2",
        "python-dotenv==1.0.0",
        "Werkzeug==3.0.1",
    ],
)
