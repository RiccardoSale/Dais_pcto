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
def schools():
    form = SchoolForm()
    if form.submit1.data and form.validate_on_submit():
        Hschool(form.code.data, form.name.data, form.region.data, form.city.data, form.street.data, form.number.data,
                form.phone.data).save()
        flash(f"Scuola inserita!", "success")
        return redirect(url_for('Hschool.schools'))

    q = all_schools()
    form2 = DeleteSchoolForm()
    if form2.submit2.data and form2.validate_on_submit():
        rhschool = school_with_code(form2.id.data).first()
        rhschool.delete()
        return redirect(url_for('Hschool.schools'))

    return render_template('schools.html', form=form, form2=form2, schools=q)
