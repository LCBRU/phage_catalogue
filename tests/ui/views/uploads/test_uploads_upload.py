import copy
from io import BytesIO
from pprint import pp
from random import choice
import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__input_file, assert__refresh_response
from lbrc_flask.database import db
from lbrc_flask.python_helpers import dictlist_remove_key
from sqlalchemy import func, select
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


def _post_upload_data(client, faker, data, expected_status, expected_errors, expected_specimens):
    file = faker.xlsx(headers=UploadColumnDefinition().column_names, data=data)
    _post_upload_file(client, expected_status, expected_errors, expected_specimens, file)


def _post_upload_file(client, expected_status, expected_errors, expected_specimens, file):
    resp = _post(client, _url(external=False), file.get_iostream(), file.filename)
    assert__refresh_response(resp)

    out = db.session.execute(select(Upload)).scalar()
    assert out.filename == file.filename
    if expected_errors:
        assert expected_errors in out.errors
    else:
        assert len(out.errors) == 0
    assert out.status == expected_status
    assert db.session.execute(select(func.count(Specimen.id))).scalar() == expected_specimens


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


@pytest.mark.app_crsf(True)
def test__get__has_form(client, loggedin_user):
    _get(client, _url(external=False), loggedin_user, has_form=True)


@pytest.mark.parametrize(
    "data_source", ["bacteria", "phages", "specimens"],
)
def test__post__valid_file__insert(client, faker, loggedin_user, standard_lookups, data_source):
    match data_source:
        case 'bacteria':
            data = faker.bacteria_data()
        case 'phages':
            data = faker.phage_data()
        case 'specimens':
            data = faker.specimen_data()

    _post_upload_data(
        client,
        faker,
        data,
        expected_status=Upload.STATUS__AWAITING_PROCESSING,
        expected_errors="",
        expected_specimens=len(data),
        )

    # Remove Keys as the data has no keys, but they will be
    # given one when they are saved
    actual = dictlist_remove_key([s.data() for s in db.session.execute(select(Specimen)).scalars()], 'key')
    expected = dictlist_remove_key(data, 'key')
    assert expected == actual


@pytest.mark.parametrize(
    "data_source", ["bacteria", "phages", "specimens"],
)
def test__post__valid_file__update(client, faker, loggedin_user, standard_lookups, data_source):
    rows = 10
    match data_source:
        case 'bacteria':
            existing = [faker.bacterium().get_in_db() for _ in range(rows)]
            data = faker.bacteria_data(rows=rows)
        case 'phages':
            existing = [faker.phage().get_in_db() for _ in range(rows)]
            data = faker.phage_data(rows=rows)
        case 'specimens':
            existing = []
            data = []
            for _ in range(rows):
                if choice([True, False]):
                    existing.append(faker.bacterium().get_in_db())
                    data.extend(faker.bacteria_data(rows=1))
                else:
                    existing.append(faker.phage().get_in_db())
                    data.extend(faker.phage_data(rows=1))

    for d, e in zip(data, existing):
        d['key'] = e.id

    _post_upload_data(
        client,
        faker,
        data,
        expected_status=Upload.STATUS__AWAITING_PROCESSING,
        expected_errors="",
        expected_specimens=len(data),
        )

    # Remove Keys as the data has no keys, but they will be
    # given one when they are saved
    actual = [s.data() for s in db.session.execute(select(Specimen)).scalars()]
    expected = data

    assert expected == actual


@pytest.mark.parametrize(
    "missing_column_name", UploadColumnDefinition().column_names,
)
def test__post__missing_column(client, faker, loggedin_user, standard_lookups, missing_column_name):
    columns_to_include = set(UploadColumnDefinition().column_names) - set([missing_column_name])

    data = faker.specimen_data()

    file = faker.xlsx(headers=columns_to_include, data=data)

    _post_upload_file(
        client=client,
        expected_status=Upload.STATUS__ERROR,
        expected_errors=f"Missing column '{missing_column_name}'",
        expected_specimens=0,
        file=file,
    )


@pytest.mark.parametrize(
    "casing", ['lower', 'upper', 'title'],
)
def test__post__case_insenstive_column_names(client, faker, loggedin_user, standard_lookups, casing):
    match casing:
        case 'lower':
            columns_to_include = [cn.lower() for cn in UploadColumnDefinition().column_names]
        case 'upper':
            columns_to_include = [cn.upper() for cn in UploadColumnDefinition().column_names]
        case 'title':
            columns_to_include = [cn.title() for cn in UploadColumnDefinition().column_names]

    data = faker.specimen_data()
    file = faker.xlsx(headers=columns_to_include, data=data)

    _post_upload_file(
        client,
        expected_status=Upload.STATUS__AWAITING_PROCESSING,
        expected_errors="",
        expected_specimens=len(data),
        file=file,
        )

    # Remove Keys as the data has no keys, but they will be
    # given one when they are saved
    actual = dictlist_remove_key([s.data() for s in db.session.execute(select(Specimen)).scalars()], 'key')
    expected = dictlist_remove_key(data, 'key')
    assert expected == actual


@pytest.mark.parametrize(
    "invalid_column", ['freezer', 'drawer', 'date'],
)
def test__post__invalid_column_type(client, faker, loggedin_user, standard_lookups, invalid_column):
    data = faker.specimen_data(rows=1)
    data[0][invalid_column] = faker.pystr()

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors=f"Row 1: {invalid_column}: Invalid value",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "invalid_column", ['position', 'box_number', 'bacterial species', 'strain', 'media', 'plasmid name', 'resistance marker', 'project', 'storage method'],
)
def test__post__invalid_column_length_bacterium(client, faker, loggedin_user, standard_lookups, invalid_column):
    max_length = UploadColumnDefinition().definition_for_column_name(invalid_column).max_length

    data = faker.bacteria_data(rows=1)
    data[0][invalid_column] = faker.pystr(min_chars=max_length+1, max_chars=max_length*2)

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors=f"Row 1: {invalid_column}: Text is longer than {max_length} characters",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "invalid_column", ['position', 'box_number', 'phage id', 'host species', 'project', 'storage method'],
)
def test__post__invalid_column_length_phage(client, faker, loggedin_user, standard_lookups, invalid_column):
    max_length = UploadColumnDefinition().definition_for_column_name(invalid_column).max_length

    data = faker.phage_data(rows=1)
    data[0][invalid_column] = faker.pystr(min_chars=max_length+1, max_chars=max_length*2)

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors=f"Row 1: {invalid_column}: Text is longer than {max_length} characters",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "added_column", ['bacterial species', 'strain', 'media', 'plasmid name', 'resistance marker'],
)
def test__post__phage_with_bacteria_data(client, faker, loggedin_user, standard_lookups, added_column):
    data = faker.phage_data(rows=1)
    data[0][added_column] = faker.pystr(min_chars=1, max_chars=5)

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: contains columns for both bacteria and phages",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "added_column", ['phage id', 'host species'],
)
def test__post__bacterium_with_phage_data(client, faker, loggedin_user, standard_lookups, added_column):
    data = faker.bacteria_data(rows=1)
    data[0][added_column] = faker.pystr(min_chars=1, max_chars=5)

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: contains columns for both bacteria and phages",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "missing_data", ['phage id', 'host species'],
)
@pytest.mark.parametrize(
    "value", ['', None, ' '],
)
def test__post__phage_with_missing_data(client, faker, loggedin_user, standard_lookups, missing_data, value):
    data = faker.phage_data(rows=1)
    data[0][missing_data] = value

    _post_upload_data(
        client,
        faker,
        data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: does not contain enough information",
        expected_specimens=0,
        )


@pytest.mark.parametrize(
    "missing_data", ['bacterial species', 'strain', 'media', 'plasmid name', 'resistance marker'],
)
@pytest.mark.parametrize(
    "value", ['', None, ' '],
)
def test__post__bacterium_with_missing_data(client, faker, loggedin_user, standard_lookups, missing_data, value):
    data = faker.bacteria_data(rows=1)
    data[0][missing_data] = value

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: does not contain enough information",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "data_source", ["bacteria", "phages"],
)
def test__post__specimen__key_does_not_exist(client, faker, loggedin_user, standard_lookups, data_source):
    match data_source:
        case 'bacteria':
            data = faker.bacteria_data(rows=1)
        case 'phages':
            data = faker.phage_data(rows=1)

    data[0]['key'] = 673

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: Key does not exist",
        expected_specimens=0,
    )


@pytest.mark.parametrize(
    "data_source", ["bacteria", "phages"],
)
def test__post__specimen__key_for_wrong_type_of_specimen(client, faker, loggedin_user, standard_lookups, data_source):
    match data_source:
        case 'bacteria':
            existing = faker.phage().get_in_db()
            data = faker.bacteria_data(rows=1)
        case 'phages':
            existing = faker.bacterium().get_in_db()
            data = faker.phage_data(rows=1)

    data[0]['key'] = existing.id

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: Key is for the wrong type of specimen",
        expected_specimens=1,
    )


def test__post__bacterium__invalid_species(client, faker, loggedin_user, standard_lookups):
    data = faker.bacteria_data(rows=1)
    data[0]['bacterial species'] = 'This doesnt exist'

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: Bacterial Species does not exist",
        expected_specimens=0,
    )


def test__post__phage__invalid_host(client, faker, loggedin_user, standard_lookups):
    data = faker.phage_data(rows=1)
    data[0]['host species'] = 'This doesnt exist'

    _post_upload_data(
        client=client,
        faker=faker,
        data=data,
        expected_status=Upload.STATUS__ERROR,
        expected_errors="Row 1: Host Species does not exist",
        expected_specimens=0,
    )
