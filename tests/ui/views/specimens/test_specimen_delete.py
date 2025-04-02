from random import choice
from flask import url_for
from lbrc_flask.pytest.asserts import assert__requires_login, assert__refresh_response, assert__requires_role
from lbrc_flask.database import db
from sqlalchemy import func, select
from phage_catalogue.model.specimens import Bacterium, Phage


def _url(external=True, **kwargs):
    return url_for('ui.specimen_delete', _external=external, **kwargs)


def _post(client, url):
    return client.post(url)


def test__get__requires_login(client, faker, standard_lookups):
    original = faker.phage().get_in_db()
    assert__requires_login(client, _url(id=original.id, external=False), post=True)


def test__get__requires_editor_login__not(client, faker, loggedin_user, standard_lookups):
    original = faker.phage().get_in_db()
    assert__requires_role(client, _url(id=original.id, external=False), post=True)


def test__post__valid_phage(client, faker, loggedin_user_editor, standard_lookups):
    originals = [faker.phage().get_in_db() for _ in range(10)]

    original = choice(originals)

    resp = _post(
        client=client,
        url=_url(id=original.id),
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Phage.id))).scalar() == 9


def test__post__valid_bacterium(client, faker, loggedin_user_editor, standard_lookups):
    originals = [faker.bacterium().get_in_db() for _ in range(10)]

    original = choice(originals)

    resp = _post(
        client=client,
        url=_url(id=original.id),
    )
    assert__refresh_response(resp)

    assert db.session.execute(select(func.count(Bacterium.id))).scalar() == 9
