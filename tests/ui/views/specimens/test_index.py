import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__requires_login, assert__select, assert__input_date, assert__input_number, assert__input_text
from phage_catalogue.services.lookups import get_bacterial_species_choices
from phage_catalogue.services.specimens import get_type_choices
from tests import phage_catalogue_get


def _url(external=True, **kwargs):
    return url_for('ui.index', _external=external, **kwargs)


def _get(client, url, loggedin_user, has_form):
    resp = phage_catalogue_get(client, url, loggedin_user, has_form)

    assert__search_html(resp.soup, clear_url=_url(external=False))

    assert__select(soup=resp.soup, id='type', options=get_type_choices())
    assert__input_date(soup=resp.soup, id='start_date')
    assert__input_date(soup=resp.soup, id='end_date')
    assert__input_number(soup=resp.soup, id='freezer')
    assert__input_number(soup=resp.soup, id='draw')
    assert__input_text(soup=resp.soup, id='position')
    assert__input_text(soup=resp.soup, id='project')
    assert__input_text(soup=resp.soup, id='storage_method')
    assert__input_text(soup=resp.soup, id='staff_member')
    assert__select(soup=resp.soup, id='species_id', options=get_bacterial_species_choices())
    assert__input_text(soup=resp.soup, id='strain')
    assert__input_text(soup=resp.soup, id='medium')
    assert__input_text(soup=resp.soup, id='plasmid')
    assert__input_text(soup=resp.soup, id='resistance_marker')
    assert__input_text(soup=resp.soup, id='phage_identifier')
    assert__select(soup=resp.soup, id='host_id', options=get_bacterial_species_choices())

    return resp


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


def test__get__one(client, faker, loggedin_user, standard_lookups):
    specimen = faker.get_phage()
    resp = _get(client, _url(), loggedin_user, has_form=False)
