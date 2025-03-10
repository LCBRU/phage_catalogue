import copy
from io import BytesIO
import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__input_file, assert__refresh_response
from lbrc_flask.database import db
from sqlalchemy import select
from phage_catalogue.model import Specimen, Upload
from tests import phage_catalogue_modal_get


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
    file = faker.xlsx(headers=Upload.COLUMNS.keys(), data=data)

    print(data)

    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()

    assert out.filename == file.filename
    assert out.status == Upload.STATUS__AWAITING_PROCESSING
    assert out.errors == ''

    # for d in file.iter_rows():
    #     s = db.session.get(Specimen, d['key'])
    #     assert s is not None


@pytest.mark.parametrize(
    "missing_column_name", Upload.COLUMN_NAMES,
)
def test__post__missing_column(client, faker, loggedin_user, standard_lookups, missing_column_name):
    col_def = copy.deepcopy(Upload.COLUMNS)
    del col_def[missing_column_name]

    data = faker.specimen_data()

    file = faker.xlsx(headers=col_def.keys(), data=data)
    
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert out.errors == f"Missing column '{missing_column_name}'"


@pytest.mark.parametrize(
    "invalid_column", ['freezer', 'drawer', 'box_number', 'date'],
)
def test__post__invalid_column_type(client, faker, loggedin_user, standard_lookups, invalid_column):
    col_def = copy.deepcopy(Upload.COLUMNS)
    col_def[invalid_column]['type'] = 'str'

    data = faker.specimen_data()
    file = faker.xlsx(headers=col_def.keys(), data=data)
    
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert out.errors == f"Invalid value in column '{invalid_column}'"


@pytest.mark.parametrize(
    "invalid_column", ['position', 'bacterial species', 'strain', 'media', 'plasmid name', 'resistance marker', 'phage id', 'host species', 'project', 'storage method'],
)
def test__post__invalid_column_length(client, faker, loggedin_user, standard_lookups, invalid_column):
    col_def = copy.deepcopy(Upload.COLUMNS)

    old_max_length = col_def[invalid_column]['max_length']
    col_def[invalid_column]['max_length'] = old_max_length * 2
    col_def[invalid_column]['min_length'] = old_max_length + 1

    data = faker.specimen_data()
    file = faker.xlsx(headers=col_def.keys(), data=data)
    
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    assert out.status == Upload.STATUS__ERROR
    assert out.errors == f"Text too long in column '{invalid_column}'"
