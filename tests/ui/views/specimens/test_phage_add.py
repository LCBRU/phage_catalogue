import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__refresh_response, assert__requires_role
from lbrc_flask.database import db
from sqlalchemy import func, select
from phage_catalogue.model.specimens import BacterialSpecies, BoxNumber, Phage, PhageIdentifier, Project, StaffMember, StorageMethod
from tests import convert_specimen_to_form_data, phage_form_lookup_names
from tests.requests import phage_catalogue_modal_get
from tests.ui.views.specimens import assert_actual_equals_expected_phage, assert_phage_form


def _url(external=True, **kwargs):
    return url_for('ui.specimen_phage_edit', _external=external, **kwargs)


def _get(client, url, loggedin_user, has_form):
    resp = phage_catalogue_modal_get(client, url, has_form)

    assert_phage_form(resp)

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


def test__post__valid_phage(client, faker, loggedin_user_editor, standard_lookups):
    expected: Phage = faker.phage().get(save=False)
    resp = _post(
        client=client,
        url=_url(),
        data=convert_specimen_to_form_data(expected),
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 1
    actual = db.session.execute(select(Phage)).scalar()

    assert_actual_equals_expected_phage(expected, actual)


@pytest.mark.parametrize(
    "missing_column_name", phage_form_lookup_names() + ['host_id', 'freezer', 'drawer', 'position', 'name', 'description', 'sample_date'],
)
def test__post__missing_column(client, faker, loggedin_user_editor, standard_lookups, missing_column_name):
    expected: Phage = faker.phage().get(save=False)
    data = convert_specimen_to_form_data(expected)
    data[missing_column_name] = ''

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert_phage_form(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 0


@pytest.mark.parametrize(
    "invalid_column_name", ['freezer', 'drawer'],
)
def test__post__invalid_column__integer(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    expected: Phage = faker.phage().get(save=False)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'Blob'

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert_phage_form(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 0


@pytest.mark.parametrize(
    "invalid_column_name", ['sample_date'],
)
def test__post__invalid_column__date(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    expected: Phage = faker.phage().get(save=False)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'Blob'

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert_phage_form(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 0


@pytest.mark.parametrize(
    "invalid_column_name", ['host_id'],
)
def test__post__invalid_column__select_value(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    expected: Phage = faker.phage().get(save=False)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'Blob'

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert_phage_form(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 0


@pytest.mark.parametrize(
    "invalid_column_name", ['host_id'],
)
def test__post__invalid_column__select_non_existent(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    expected: Phage = faker.phage().get(save=False)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 1000

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert_phage_form(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 0


@pytest.mark.parametrize(
    "invalid_column_name", phage_form_lookup_names() + ['name', 'position'],
)
def test__post__invalid_column__string_length(client, faker, loggedin_user_editor, standard_lookups, invalid_column_name):
    expected: Phage = faker.phage().get(save=False)
    data = convert_specimen_to_form_data(expected)
    data[invalid_column_name] = 'A'*1000

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert_phage_form(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 0


def test__post__new_lookup_values(client, faker, loggedin_user_editor):
    expected: Phage = faker.phage().get(
        save=False,
        host=faker.bacterial_species().get_in_db(),
        lookups_in_db=False,
        )
    data = convert_specimen_to_form_data(expected)

    resp = _post(
        client=client,
        url=_url(),
        data=data,
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 1

    assert db.session.execute(select(func.count(BacterialSpecies.id)).where(BacterialSpecies.name == expected.host.name)).scalar() == 1
    assert db.session.execute(select(func.count(PhageIdentifier.id)).where(PhageIdentifier.name == expected.phage_identifier.name)).scalar() == 1
    assert db.session.execute(select(func.count(Project.id)).where(Project.name == expected.project.name)).scalar() == 1
    assert db.session.execute(select(func.count(StorageMethod.id)).where(StorageMethod.name == expected.storage_method.name)).scalar() == 1
    assert db.session.execute(select(func.count(StaffMember.id)).where(StaffMember.name == expected.staff_member.name)).scalar() == 1
    assert db.session.execute(select(func.count(BoxNumber.id)).where(BoxNumber.name == expected.box_number.name)).scalar() == 1
