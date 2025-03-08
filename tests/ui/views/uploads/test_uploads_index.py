from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__requires_login
from tests import phage_catalogue_get


def _url(external=True, **kwargs):
    return url_for('ui.uploads_index', _external=external, **kwargs)


def _get(client, url, loggedin_user, has_form):
    resp = phage_catalogue_get(client, url, loggedin_user, has_form)

    assert__search_html(resp.soup, clear_url=_url(external=False))

    return resp


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


def test__get__one(client, faker, loggedin_user, standard_lookups):
    upload = faker.get_upload()
    resp = _get(client, _url(), loggedin_user, has_form=False)
