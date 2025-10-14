"""
Routes principales pour l'application Flask
Pages : permission, accueil, questionnaire, résultat
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def permission():
    """Page de permissions avec tests navigateur"""
    return render_template('permission.html')

@main_bp.route('/accueil')
def accueil():
    """Page d'accueil avec informations personnelles"""
    return render_template('accueil.html')

@main_bp.route('/questionnaire')
def questionnaire():
    """Page du questionnaire avec reconnaissance vocale continue"""
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Session invalide', 'error')
        return redirect(url_for('main.permission'))
    
    return render_template('questionnaire.html', session_id=session_id)

@main_bp.route('/resultat/<session_id>')
def resultat(session_id):
    """Page des résultats avec statistiques et export"""
    return render_template('resultat.html', session_id=session_id)

@main_bp.route('/admin')
def admin():
    """Page d'administration (optionnelle)"""
    from models.database_flask import DatabaseManager
    
    db = DatabaseManager()
    sessions = db.get_all_sessions()
    
    return render_template('admin.html', sessions=sessions)

@main_bp.errorhandler(404)
def not_found(error):
    """Gestion des erreurs 404"""
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500"""
    return render_template('500.html'), 500
