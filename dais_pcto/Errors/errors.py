from flask import Blueprint, render_template
from dais_pcto.app import db
from flask import request

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@errors.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
