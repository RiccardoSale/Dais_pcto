from flask import Blueprint, render_template
from flask_login import login_required, current_user

blueprint = Blueprint('BaseRoute', __name__)


@blueprint.route('/')
def index():
    return render_template('index.html')


# ->passo al render il nome dell'utente in modo da poterlo usare come dato all'interno del template
@blueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)
