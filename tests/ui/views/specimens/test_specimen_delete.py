from datetime import date
from random import choice
import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__refresh_response
from lbrc_flask.database import db
from sqlalchemy import func, select
from phage_catalogue.model.specimens import BacterialSpecies, Bacterium, BoxNumber, Phage, PhageIdentifier, Project, StaffMember, StorageMethod
from tests import convert_specimen_to_form_data, phage_form_lookup_names
from tests.requests import phage_catalogue_modal_get
from tests.ui.views.specimens import assert_actual_equals_expected_phage, assert_phage_form


def _url(external=True, **kwargs):
    return url_for('ui.specimen_delete', _external=external, **kwargs)


def _post(client, url):
    return client.post(url)


def test__get__requires_login(client, faker, standard_lookups):
    original = faker.phage().get_in_db()
    assert__requires_login(client, _url(id=original.id, external=False), post=True)


def test__post__valid_phage(client, faker, loggedin_user, standard_lookups):
    originals = [faker.phage().get_in_db() for _ in range(10)]

    original = choice(originals)

    resp = _post(
        client=client,
        url=_url(id=original.id),
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 9


def test__post__valid_bacterium(client, faker, loggedin_user, standard_lookups):
    originals = [faker.bacterium().get_in_db() for _ in range(10)]

    original = choice(originals)

    resp = _post(
        client=client,
        url=_url(id=original.id),
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 9
