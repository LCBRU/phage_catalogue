from datetime import date
import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__refresh_response, assert__requires_role
from lbrc_flask.database import db
from sqlalchemy import func, select
from phage_catalogue.model.specimens import BacterialSpecies, Bacterium, BoxNumber, Medium, Plasmid, Project, ResistanceMarker, StaffMember, StorageMethod, Strain
from tests import bacterium_form_lookup_names, convert_specimen_to_form_data
from tests.requests import phage_catalogue_modal_get
from tests.ui.views.specimens import assert_actual_equals_expected_bacterium, assert_bacterium_form


def updater_bacterium(faker, standard_lookups):
    expected: Bacterium = faker.bacterium().get(
        species=standard_lookups['bacterial_species'][1],
        strain=standard_lookups['strain'][1],
        medium=standard_lookups['medium'][1],
        plasmid=standard_lookups['plasmid'][1],
        resistance_marker=standard_lookups['resistance_marker'][1],
        project=standard_lookups['project'][1],
        box_number=standard_lookups['box_number'][1],
        storage_method=standard_lookups['storage_method'][1],
        staff_member=standard_lookups['staff_member'][1],
        sample_date=date(2024, 3, 4),
        freezer=3,
        drawer=4,
        position='B',
        description='Suttin else',
    )
    
    return expected


def original_bacterium(faker, standard_lookups):
    original: Bacterium = faker.bacterium().get_in_db(
        species=standard_lookups['bacterial_species'][0],
        strain=standard_lookups['strain'][0],
        medium=standard_lookups['medium'][0],
        plasmid=standard_lookups['plasmid'][0],
        resistance_marker=standard_lookups['resistance_marker'][0],
        project=standard_lookups['project'][0],
        box_number=standard_lookups['box_number'][0],
        storage_method=standard_lookups['storage_method'][0],
        staff_member=standard_lookups['staff_member'][0],
        sample_date=date(2025, 1, 2),
        freezer=1,
        drawer=2,
        position='A',
        description='Lorem ipsum',
    )
    
    return original


def _url(external=True, **kwargs):
    return url_for('ui.specimen_bacterium_edit', _external=external, **kwargs)


def _get(client, url, loggedin_user, has_form):
    resp = phage_catalogue_modal_get(client, url, has_form)

    assert_bacterium_form(resp)

    return resp


def _post(client, url, data):
    return client.post(
        url,
        data=data,
    )


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


def test__get__requires_editor_login__not(client, loggedin_user):
    assert__requires_role(client, _url(external=False))


@pytest.mark.app_crsf(True)
def test__get__has_form(client, loggedin_user_editor, standard_lookups):
    _get(client, _url(external=False), loggedin_user_editor, has_form=True)


def test__post__valid_bacterium(client, faker, loggedin_user_editor, standard_lookups):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    
    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=convert_specimen_to_form_data(expected),
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1
    actual = db.session.execute(select(Bacterium)).scalar()

    assert_actual_equals_expected_bacterium(expected, actual)


@pytest.mark.parametrize(
    "missing_column_name", bacterium_form_lookup_names() + ['species_id', 'freezer', 'drawer', 'position', 'name', 'description', 'sample_date'],
)
def test__post__missing_column(client, faker, loggedin_user_editor, standard_lookups, missing_column_name):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    data = convert_specimen_to_form_data(expected)
    data[missing_column_name] = ''

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert_bacterium_form(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1


@pytest.mark.parametrize(
    "invalid_column_name", ['freezer', 'drawer'],
)
def test__post__invalid_column__integer(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'Blob'

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert_bacterium_form(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1


@pytest.mark.parametrize(
    "invalid_column_name", ['sample_date'],
)
def test__post__invalid_column__date(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'Blob'

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert_bacterium_form(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1


@pytest.mark.parametrize(
    "invalid_column_name", ['species_id'],
)
def test__post__invalid_column__select_value(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'Blob'

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert_bacterium_form(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1


@pytest.mark.parametrize(
    "invalid_column_name", ['species_id'],
)
def test__post__invalid_column__select_non_existent(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 1000

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert_bacterium_form(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1


@pytest.mark.parametrize(
    "invalid_column_name", bacterium_form_lookup_names() + ['name', 'position'],
)
def test__post__invalid_column__string_length(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    original = original_bacterium(faker, standard_lookups)
    expected = updater_bacterium(faker, standard_lookups)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'A'*1000

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert_bacterium_form(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1


def test__post__new_lookup_values(client, faker, loggedin_user_editor, standard_lookups):
    original = original_bacterium(faker, standard_lookups)

    expected: Bacterium = faker.bacterium().get(
        species=standard_lookups['bacterial_species'][1],
        strain=faker.strain_name(101),
        medium=faker.medium_name(101),
        plasmid=faker.plasmid_name(101),
        resistance_marker=faker.resistance_marker_name(101),
        project=faker.project_name(101),
        box_number=faker.box_number_name(101),
        storage_method=faker.storage_method_name(101),
        staff_member=faker.staff_member_name(101),
        sample_date=date(2024, 3, 4),
        freezer=3,
        drawer=4,
        position='B',
        description='Suttin else',
    )

    expected: Bacterium = faker.bacterium().get(
        species=faker.bacterial_species().get_in_db(),
        lookups_in_db=False,
        )
    data = convert_specimen_to_form_data(expected)

    resp = _post(
        client=client,
        url=_url(id=original.id),
        data=data,
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 1

    assert db.session.execute(select(func.count(BacterialSpecies.id)).where(BacterialSpecies.name == expected.species.name)).scalar() == 1
    assert db.session.execute(select(func.count(Strain.id)).where(Strain.name == expected.strain.name)).scalar() == 1
    assert db.session.execute(select(func.count(Medium.id)).where(Medium.name == expected.medium.name)).scalar() == 1
    assert db.session.execute(select(func.count(Plasmid.id)).where(Plasmid.name == expected.plasmid.name)).scalar() == 1
    assert db.session.execute(select(func.count(ResistanceMarker.id)).where(ResistanceMarker.name == expected.resistance_marker.name)).scalar() == 1
    assert db.session.execute(select(func.count(Project.id)).where(Project.name == expected.project.name)).scalar() == 1
    assert db.session.execute(select(func.count(StorageMethod.id)).where(StorageMethod.name == expected.storage_method.name)).scalar() == 1
    assert db.session.execute(select(func.count(StaffMember.id)).where(StaffMember.name == expected.staff_member.name)).scalar() == 1
    assert db.session.execute(select(func.count(BoxNumber.id)).where(BoxNumber.name == expected.box_number.name)).scalar() == 1
