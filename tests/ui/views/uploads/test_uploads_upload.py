import copy
from io import BytesIO
from pprint import pp
import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__input_file, assert__refresh_response
from lbrc_flask.database import db
from sqlalchemy import select
from phage_catalogue.model.specimens import Specimen
from phage_catalogue.model.uploads import UploadColumnDefinition, Upload
from tests.requests import phage_catalogue_modal_get


def _url(external=True, **kwargs):
    return url_for('ui.uploads_upload', _external=external, **kwargs)


def _get(client, url, loggedin_user, has_form):
    resp = phage_catalogue_modal_get(client, url, loggedin_user, has_form)

    assert__input_file(resp.soup, 'sample_file')

    return resp


def _post(client, url, file, filename):
    data={
        'sample_file': (
            BytesIO(file),
            filename,
        ),
    }

    return client.post(url, data=data)


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


@pytest.mark.app_crsf(True)
def test__get__has_form(client, loggedin_user):
    _get(client, _url(external=False), loggedin_user, has_form=True)


def test__post__valid_file(client, faker, loggedin_user, standard_lookups):
    data = faker.specimen_data()
    file = faker.xlsx(headers=UploadColumnDefinition().column_names, data=data)

    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()

    assert out.filename == file.filename
    assert out.errors == ''
    assert out.status == Upload.STATUS__AWAITING_PROCESSING

    actual = list(db.session.execute(select(Specimen)).scalars())

    # print('Expected:')
    # print(data)

    # print('\n')
    # print('-' * 100)
    # print('\n')

    # print('Actual:')
    # print(actual)

    # assert len(data) == len(actual)


@pytest.mark.parametrize(
    "missing_column_name", UploadColumnDefinition().column_names,
)
def test__post__missing_column(client, faker, loggedin_user, standard_lookups, missing_column_name):
    columns_to_include = set(UploadColumnDefinition().column_names) - set([missing_column_name])

    data = faker.specimen_data()

    file = faker.xlsx(headers=columns_to_include, data=data)
    
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert f"Missing column '{missing_column_name}'" in out.errors


@pytest.mark.parametrize(
    "invalid_column", ['freezer', 'drawer', 'date'],
)
def test__post__invalid_column_type(client, faker, loggedin_user, standard_lookups, invalid_column):
    data = faker.specimen_data(rows=1)
    data[0][invalid_column] = faker.pystr()
    file = faker.xlsx(headers=UploadColumnDefinition().column_names, data=data)

    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert out.errors == f"Row 1: {invalid_column}: Invalid value"


@pytest.mark.parametrize(
    "invalid_column", ['position', 'box_number', 'bacterial species', 'strain', 'media', 'plasmid name', 'resistance marker', 'project', 'storage method'],
)
def test__post__invalid_column_length_bacterium(client, faker, loggedin_user, standard_lookups, invalid_column):
    max_length = UploadColumnDefinition().definition_for_column_name(invalid_column)['max_length']

    data = faker.bacteria_data(rows=1)
    data[0][invalid_column] = faker.pystr(min_chars=max_length+1, max_chars=max_length*2)

    file = faker.xlsx(headers=UploadColumnDefinition().column_names, data=data)
    
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert out.errors == f"Row 1: {invalid_column}: Text is longer than {max_length} characters"


@pytest.mark.parametrize(
    "invalid_column", ['position', 'box_number', 'phage id', 'host species', 'project', 'storage method'],
)
def test__post__invalid_column_length_phage(client, faker, loggedin_user, standard_lookups, invalid_column):
    max_length = UploadColumnDefinition().definition_for_column_name(invalid_column)['max_length']

    data = faker.phage_data(rows=1)
    data[0][invalid_column] = faker.pystr(min_chars=max_length+1, max_chars=max_length*2)

    file = faker.xlsx(headers=UploadColumnDefinition().column_names, data=data)
    
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert out.errors == f"Row 1: {invalid_column}: Text is longer than {max_length} characters"
