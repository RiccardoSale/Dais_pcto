from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_required
from werkzeug.routing import BuildError

from dais_pcto.app import db
from .forms import SchoolForm, DeleteSchoolForm
from .models import Hschool, school_with_code, all_schools
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )

from ..Auth.route import admin
from ..module_extensions import CRUDMixin

blueprint = Blueprint('Hschool', __name__)


@blueprint.route('/schools', methods=("GET", "POST"))
@admin.require(http_exception=404)
@login_required
# Funzione per inserire o rimuovere una scuola
def schools():
    # Recupero dei dati richiesti
    form = SchoolForm()
    # Inserimento di una scuola
    if form.submit1.data and form.validate_on_submit():
        Hschool(form.code.data, form.name.data, form.region.data, form.city.data, form.street.data, form.number.data,
                form.phone.data).save()
        flash("La scuola è stata inserita con successo!", "success")
        # Ritorno della pagina delle scuole
        return redirect(url_for('Hschool.schools'))

    # q = tutte le scuole registrate
    q = all_schools()
    form2 = DeleteSchoolForm()
    # Rimozione di una scuola
    if form2.submit2.data and form2.validate_on_submit():
        rhschool = school_with_code(form2.id.data).first()
        rhschool.delete()
        # Ritorno della pagina delle scuole
        return redirect(url_for('Hschool.schools'))
    # Indirizzamento alla pagina delle scuole
    return render_template('schools.html', form=form, form2=form2, schools=q)
