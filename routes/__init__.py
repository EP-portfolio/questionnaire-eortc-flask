"""
Routes pour l'application Flask
"""

from .main_flask import main_bp
from .api_flask import api_bp

__all__ = ['main_bp', 'api_bp']
