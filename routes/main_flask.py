"""
Routes principales pour l'application Flask
Pages : permission, accueil, questionnaire, résultat
"""

from flask import Blueprint, render_template, request, redirect, url_for
import datetime

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def permission():
    """Page de permissions avec tests navigateur"""
    return render_template("permission_flask.html")


@main_bp.route("/accueil")
def accueil():
    """Page d'accueil avec informations personnelles"""
    return render_template("accueil_flask.html")


@main_bp.route("/questionnaire")
def questionnaire():
    """Page du questionnaire avec reconnaissance vocale continue"""
    session_id = request.args.get("session_id")
    if not session_id:
        print("DEBUG: Session ID manquant dans l'URL")
        # ✅ CORRECTION 2 : Redirection sans flash qui cause l'erreur
        return redirect(url_for("main.accueil"))

    # Valider que la session existe réellement en base
    from models.database_flask import DatabaseManager

    db = DatabaseManager()
    session_data = db.get_session(session_id)

    print(f"DEBUG: Validation session {session_id}")
    print(f"DEBUG: Session trouvée: {session_data is not None}")

    if not session_data:
        print(f"DEBUG: Session {session_id} introuvable en base")
        # ✅ Redirection directe sans message flash
        return redirect(url_for("main.accueil"))

    print(f"DEBUG: Session validée: {session_data.get('initials', 'N/A')}")

    return render_template("questionnaire_flask_simple.html", session_id=session_id)


@main_bp.route("/resultat/<session_id>")
def resultat(session_id):
    """Page des résultats avec statistiques et export"""
    return render_template("resultat_flask.html", session_id=session_id)


@main_bp.route("/admin")
def admin():
    """Page d'administration (optionnelle)"""
    from models.database_flask import DatabaseManager

    db = DatabaseManager()
    sessions = db.get_all_sessions()

    return render_template("admin.html", sessions=sessions)


@main_bp.errorhandler(404)
def not_found(error):
    """Gestion des erreurs 404"""
    return render_template("404.html"), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500"""
    return render_template("500.html"), 500
