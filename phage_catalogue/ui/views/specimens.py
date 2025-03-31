from phage_catalogue.model.specimens import Bacterium, Phage, Specimen
from phage_catalogue.services.lookups import get_bacterial_species_choices, get_box_number_datalist_choices, get_medium_datalist_choices, get_phage_identifier_datalist_choices, get_plasmid_datalist_choices, get_project_datalist_choices, get_resistance_marker_datalist_choices, get_staff_member_datalist_choices, get_storage_method_datalist_choices, get_strain_datalist_choices
from phage_catalogue.services.specimens import get_type_choices, specimen_bacterium_save, specimen_phage_save, specimen_search_query
from .. import blueprint
from flask import render_template, render_template_string, request, url_for
from lbrc_flask.forms import SearchForm
from lbrc_flask.database import db
from wtforms import DateField, HiddenField, IntegerField, SelectField, StringField, TextAreaField
from lbrc_flask.forms import FlashingForm, DataListField
from lbrc_flask.response import refresh_response
from wtforms.validators import Length, DataRequired
from sqlalchemy.orm import selectinload


class SpecimenSearchForm(SearchForm):
    type = SelectField('Type', choices=get_type_choices())
    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    freezer = IntegerField('Freezer')
    drawer = IntegerField('Drawer')
    position = StringField('Position', validators=[Length(max=20)], render_kw={'autocomplete': 'off'})
    box_number = StringField('Project', validators=[Length(max=100)], render_kw={'list': 'box_number_datalist', 'autocomplete': 'off'})
    box_number_datalist = DataListField()
    project = StringField('Project', validators=[Length(max=100)], render_kw={'list': 'project_datalist', 'autocomplete': 'off'})
    project_datalist = DataListField()
    storage_method = StringField('Storage Method', validators=[Length(max=100)], render_kw={'list': 'storage_method_datalist', 'autocomplete': 'off'})
    storage_method_datalist = DataListField()
    staff_member = StringField('Staff Member', validators=[Length(max=100)], render_kw={'list': 'staff_member_datalist', 'autocomplete': 'off'})
    staff_member_datalist = DataListField()
    species_id = SelectField('Bacterial Species', coerce=int, render_kw={'class':' select2'})
    strain = StringField('Strain', validators=[Length(max=100)], render_kw={'list': 'strain_datalist', 'autocomplete': 'off'})
    strain_datalist = DataListField()
    medium = StringField('Medium', validators=[Length(max=100)], render_kw={'list': 'medium_datalist', 'autocomplete': 'off'})
    medium_datalist = DataListField()
    plasmid = StringField('Plasmid', validators=[Length(max=100)], render_kw={'list': 'plasmid_datalist', 'autocomplete': 'off'})
    plasmid_datalist = DataListField()
    resistance_marker = StringField('Resistance Marker', validators=[Length(max=100)], render_kw={'list': 'resistance_marker_datalist', 'autocomplete': 'off'})
    resistance_marker_datalist = DataListField()
    phage_identifier = StringField('Phage Identifier', validators=[Length(max=100)], render_kw={'list': 'phage_identifier_datalist', 'autocomplete': 'off'})
    phage_identifier_datalist = DataListField()
    host_id = SelectField('Phage Host', coerce=int, render_kw={'class':' select2'}, validators=[DataRequired()])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.box_number_datalist.choices = get_box_number_datalist_choices()
        self.project_datalist.choices = get_project_datalist_choices()
        self.storage_method_datalist.choices = get_storage_method_datalist_choices()
        self.staff_member_datalist.choices = get_staff_member_datalist_choices()
        self.species_id.choices = get_bacterial_species_choices()
        self.strain_datalist.choices = get_strain_datalist_choices()
        self.medium_datalist.choices = get_medium_datalist_choices()
        self.plasmid_datalist.choices = get_plasmid_datalist_choices()
        self.resistance_marker_datalist.choices = get_resistance_marker_datalist_choices()
        self.host_id.choices = get_bacterial_species_choices()
        self.phage_identifier_datalist.choices = get_phage_identifier_datalist_choices()



class EditSpecimenForm(FlashingForm):
    id = HiddenField('id')
    name = StringField('Name', validators=[Length(max=100), DataRequired()])
    sample_date = DateField('Sample Date', validators=[DataRequired()])
    freezer = IntegerField('Freezer', validators=[DataRequired()])
    drawer = IntegerField('Drawer', validators=[DataRequired()])
    position = StringField('Position', validators=[Length(max=20), DataRequired()], render_kw={'autocomplete': 'off'})
    description = TextAreaField('Description', validators=[DataRequired()])
    box_number = StringField('Box Number', validators=[Length(max=100), DataRequired()], render_kw={'list': 'box_number_datalist', 'autocomplete': 'off'})
    box_number_datalist = DataListField()
    project = StringField('Project', validators=[Length(max=100), DataRequired()], render_kw={'list': 'project_datalist', 'autocomplete': 'off'})
    project_datalist = DataListField()
    storage_method = StringField('Storage Method', validators=[Length(max=100), DataRequired()], render_kw={'list': 'storage_method_datalist', 'autocomplete': 'off'})
    storage_method_datalist = DataListField()
    staff_member = StringField('Staff Member', validators=[Length(max=100), DataRequired()], render_kw={'list': 'staff_member_datalist', 'autocomplete': 'off'})
    staff_member_datalist = DataListField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.box_number_datalist.choices = get_box_number_datalist_choices()
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
    search_form = SpecimenSearchForm(formdata=request.args, search_placeholder='Search specimens')

    q = specimen_search_query(search_form.data)

    q = q.options(selectinload(Specimen.project))
    q = q.options(selectinload(Specimen.storage_method))
    q = q.options(selectinload(Specimen.staff_member))
    q = q.options(selectinload(Bacterium.species))
    q = q.options(selectinload(Bacterium.strain))
    q = q.options(selectinload(Bacterium.medium))
    q = q.options(selectinload(Bacterium.plasmid))
    q = q.options(selectinload(Bacterium.resistance_marker))
    q = q.options(selectinload(Phage.phage_identifier))
    q = q.options(selectinload(Phage.host))

    specimens = db.paginate(select=q)

    return render_template(
        "ui/specimens/index.html",
        specimens=specimens,
        search_form=search_form,
    )


@blueprint.route("/specimen/<int:id>/details/<string:detail_selector>")
def specimen_details(id, detail_selector):
    specimen = db.get_or_404(Specimen, id)

    template = '''
        {% from "ui/specimens/details.html" import render_specimen %}
        {{ render_specimen(specimen, detail_selector) }}
    '''

    return render_template_string(
        template,
        specimen=specimen,
        detail_selector=detail_selector,
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
