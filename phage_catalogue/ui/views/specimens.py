from phage_catalogue.model import Bacterium, Phage, Specimen
from phage_catalogue.services.lookups import get_bacterial_species_choices, get_medium_datalist_choices, get_phage_identifier_datalist_choices, get_plasmid_datalist_choices, get_project_datalist_choices, get_resistance_marker_datalist_choices, get_staff_member_datalist_choices, get_storage_method_datalist_choices, get_strain_datalist_choices
from phage_catalogue.services.specimens import specimen_bacterium_save, specimen_phage_save, specimen_search_query
from .. import blueprint
from flask import render_template, request, url_for
from lbrc_flask.forms import SearchForm
from lbrc_flask.database import db
from wtforms import DateField, HiddenField, IntegerField, SelectField, StringField, TextAreaField
from lbrc_flask.forms import FlashingForm, DataListField
from lbrc_flask.response import refresh_response
from wtforms.validators import Length, DataRequired


class EditSpecimenForm(FlashingForm):
    id = HiddenField('id')
    sample_date = DateField('Sample Date', validators=[DataRequired()])
    freezer = IntegerField('Freezer', validators=[DataRequired()])
    draw = IntegerField('Draw', validators=[DataRequired()])
    position = StringField('Position', validators=[Length(max=20), DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    project = StringField('Project', validators=[Length(max=100), DataRequired()], render_kw={'list': 'project_datalist', 'autocomplete': 'off'})
    project_datalist = DataListField()
    storage_method = StringField('Storage Method', validators=[Length(max=100), DataRequired()], render_kw={'list': 'storage_method_datalist', 'autocomplete': 'off'})
    storage_method_datalist = DataListField()
    staff_member = StringField('Staff Member', validators=[Length(max=100), DataRequired()], render_kw={'list': 'staff_member_datalist', 'autocomplete': 'off'})
    staff_member_datalist = DataListField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.project_datalist.choices = get_project_datalist_choices()
        self.storage_method_datalist.choices = get_storage_method_datalist_choices()
        self.staff_member_datalist.choices = get_staff_member_datalist_choices()


class EditBacteriumForm(EditSpecimenForm):
    species_id = SelectField('Species', default=0, render_kw={'class':' select2'}, validators=[DataRequired()])
    strain = StringField('Strain', validators=[Length(max=100), DataRequired()], render_kw={'list': 'strain_datalist', 'autocomplete': 'off'})
    strain_datalist = DataListField()
    medium = StringField('Medium', validators=[Length(max=100), DataRequired()], render_kw={'list': 'medium_datalist', 'autocomplete': 'off'})
    medium_datalist = DataListField()
    plasmid = StringField('Plasmid', validators=[Length(max=100), DataRequired()], render_kw={'list': 'plasmid_datalist', 'autocomplete': 'off'})
    plasmid_datalist = DataListField()
    resistance_marker = StringField('Resistance Marker', validators=[Length(max=100), DataRequired()], render_kw={'list': 'resistance_marker_datalist', 'autocomplete': 'off'})
    resistance_marker_datalist = DataListField()
    notes = TextAreaField('Notes')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.species_id.choices = get_bacterial_species_choices()
        self.strain_datalist.choices = get_strain_datalist_choices()
        self.medium_datalist.choices = get_medium_datalist_choices()
        self.plasmid_datalist.choices = get_plasmid_datalist_choices()
        self.resistance_marker_datalist.choices = get_resistance_marker_datalist_choices()


class EditPhageForm(EditSpecimenForm):
    phage_identifier = StringField('Phage Identifier', validators=[Length(max=100), DataRequired()], render_kw={'list': 'phage_identifier_datalist', 'autocomplete': 'off'})
    phage_identifier_datalist = DataListField()
    host_id = SelectField('Host', default=0, render_kw={'class':' select2'}, validators=[DataRequired()])
    notes = TextAreaField('Notes')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.host_id.choices = get_bacterial_species_choices()
        self.phage_identifier_datalist.choices = get_phage_identifier_datalist_choices()


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
