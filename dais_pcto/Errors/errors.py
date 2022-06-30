from flask import Blueprint, render_template
from dais_pcto.app import db
from flask import request

errors = Blueprint('errors', __name__)

# Errore 403 (accesso negato)
@errors.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# Errore 404 (la pagina web non è disponibile)
@errors.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
