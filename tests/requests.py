import re
from lbrc_flask.pytest.asserts import get_and_assert_standards, get_and_assert_standards_modal
from flask import url_for


def phage_catalogue_get(client, url, user, has_form=False):
    resp = get_and_assert_standards(client, url, user, has_form)

    assert resp.soup.nav is not None
    assert resp.soup.nav.find("a", href=url_for('ui.index'), string=re.compile("Specimens")) is not None
    assert resp.soup.nav.find("a", href=url_for('ui.uploads_index'), string=re.compile("Uploads")) is not None

    return resp


def phage_catalogue_modal_get(client, url, user, has_form=False):
    resp = get_and_assert_standards_modal(client, url, user, has_form)

    return resp
