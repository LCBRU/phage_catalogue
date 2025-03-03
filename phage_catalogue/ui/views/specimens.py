from phage_catalogue.model import Bacterium, Phage, Specimen
from phage_catalogue.services.specimens import specimen_bacterium_save, specimen_phage_save, specimen_search_query
from .. import blueprint
from flask import render_template, request, url_for
from lbrc_flask.forms import SearchForm
from lbrc_flask.database import db
from wtforms import DateField, HiddenField, IntegerField, StringField, TextAreaField
from wtforms.validators import Length
from lbrc_flask.forms import FlashingForm
from lbrc_flask.response import refresh_response


class EditBacteriumForm(FlashingForm):
    id = HiddenField('id')
    sample_date = DateField('Sample Date')
    freezer = IntegerField('Freezer')
    draw = IntegerField('Draw')
    position = StringField('Position', validators=[Length(max=20)])
    description = TextAreaField('Description')
    project = StringField('Project', validators=[Length(max=100)])
    storage_method = StringField('Storage Method', validators=[Length(max=100)])
    staff_member = StringField('Staff Member', validators=[Length(max=100)])
    species = StringField('Species', validators=[Length(max=100)])
    strain = StringField('Strain', validators=[Length(max=100)])
    medium = StringField('Medium', validators=[Length(max=100)])
    plasmid = StringField('Plasmid', validators=[Length(max=100)])
    resistance_marker = StringField('Resistance Marker', validators=[Length(max=100)])
    notes = TextAreaField('Notes')


class EditPhageForm(FlashingForm):
    id = HiddenField('id')
    sample_date = DateField('Sample Date')
    freezer = IntegerField('Freezer')
    draw = IntegerField('Draw')
    position = StringField('Position', validators=[Length(max=20)])
    description = TextAreaField('Description')
    project = StringField('Project', validators=[Length(max=100)])
    storage_method = StringField('Storage Method', validators=[Length(max=100)])
    staff_member = StringField('Staff Member', validators=[Length(max=100)])
    phage_identifier = StringField('Phage Identifier', validators=[Length(max=100)])
    host = StringField('Host', validators=[Length(max=100)])
    notes = TextAreaField('Notes')


@blueprint.route("/")
def index():
    search_form = SearchForm(formdata=request.args, search_placeholder='Search specimens')

    q = specimen_search_query(search_form.data)

    specimens = db.paginate(select=q)

    return render_template(
        "ui/specimens/index.html",
        specimens=specimens,
        search_form=search_form,
    )


@blueprint.route("/specimen/bacterium/add/", methods=['GET', 'POST'])
@blueprint.route("/specimen/bacterium/edit/<int:id>", methods=['GET', 'POST'])
def specimen_bacterium_edit(id=None):
    if id:
        object = db.get_or_404(Bacterium, id)
        form = EditBacteriumForm(obj=object)
        title = f"Edit Bacterium #{object.id}"
    else:
        object = Bacterium()
        form = EditBacteriumForm()
        title = f"Add Bacterium"

    if form.validate_on_submit():
        specimen_bacterium_save(object, form.data)
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=title,
        form=form,
        url=url_for('ui.specimen_bacterium_edit', id=id),
    )


@blueprint.route("/specimen/phage/add/", methods=['GET', 'POST'])
@blueprint.route("/specimen/phage/edit/<int:id>", methods=['GET', 'POST'])
def specimen_phage_edit(id=None):
    if id:
        object = db.get_or_404(Phage, id)
        form = EditPhageForm(obj=object)
        title = f"Edit Phage #{object.id}"
    else:
        object = Phage()
        form = EditPhageForm()
        title = f"Add Phage"

    if form.validate_on_submit():
        specimen_phage_save(object, form.data)
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=title,
        form=form,
        url=url_for('ui.specimen_phage_edit', id=id),
    )


@blueprint.route("/specimen/delete/<int:id>", methods=['POST'])
def specimen_delete(id):
    specimen = db.get_or_404(Specimen, id)
    db.session.delete(specimen)
    db.session.commit()

    return refresh_response()
