from lbrc_flask.pytest.asserts import assert__input_text, assert__input_date, assert__input_number, assert__input_textarea, assert__select
from lbrc_flask.database import db
from sqlalchemy import select
from phage_catalogue.model.specimens import BacterialSpecies


def assert_bacterium_form(resp):
    assert__input_text(resp.soup, 'name')
    assert__input_date(resp.soup, 'sample_date')
    assert__input_number(resp.soup, 'freezer')
    assert__input_number(resp.soup, 'drawer')
    assert__input_text(resp.soup, 'position')
    assert__input_textarea(resp.soup, 'description')
    assert__input_text(resp.soup, 'box_number')
    assert__input_text(resp.soup, 'project')
    assert__input_text(resp.soup, 'storage_method')
    assert__input_text(resp.soup, 'staff_member')
    assert__select(resp.soup, 'species_id', [('0', '')] + [(str(bs.id), bs.name) for bs in db.session.execute(select(BacterialSpecies).order_by(BacterialSpecies.name)).scalars()])
    assert__input_text(resp.soup, 'strain')
    assert__input_text(resp.soup, 'medium')
    assert__input_text(resp.soup, 'plasmid')
    assert__input_text(resp.soup, 'resistance_marker')
    assert__input_textarea(resp.soup, 'notes')


def assert_phage_form(resp):
    assert__input_text(resp.soup, 'name')
    assert__input_date(resp.soup, 'sample_date')
    assert__input_number(resp.soup, 'freezer')
    assert__input_number(resp.soup, 'drawer')
    assert__input_text(resp.soup, 'position')
    assert__input_textarea(resp.soup, 'description')
    assert__input_text(resp.soup, 'box_number')
    assert__input_text(resp.soup, 'project')
    assert__input_text(resp.soup, 'storage_method')
    assert__input_text(resp.soup, 'staff_member')
    assert__select(resp.soup, 'host_id', [('0', '')] + [(str(bs.id), bs.name) for bs in db.session.execute(select(BacterialSpecies).order_by(BacterialSpecies.name)).scalars()])
    assert__input_text(resp.soup, 'phage_identifier')


def assert_actual_equals_expected_specimen(expected, actual):
    assert actual is not None
    assert actual.name == expected.name
    assert actual.sample_date == expected.sample_date
    assert actual.freezer == expected.freezer
    assert actual.drawer == expected.drawer
    assert actual.position == expected.position.upper()
    assert actual.description == expected.description
    assert actual.box_number_id == expected.box_number.id
    assert actual.project_id == expected.project.id
    assert actual.storage_method_id == expected.storage_method.id
    assert actual.staff_member_id == expected.staff_member.id
    assert actual.notes == expected.notes


def assert_actual_equals_expected_bacterium(expected, actual):
    assert_actual_equals_expected_specimen(expected, actual)

    assert int(actual.species_id) == expected.species.id
    assert actual.strain_id == expected.strain.id
    assert actual.medium_id == expected.medium.id
    assert actual.plasmid_id == expected.plasmid.id
    assert actual.resistance_marker_id == expected.resistance_marker.id


def assert_actual_equals_expected_phage(expected, actual):
    assert_actual_equals_expected_specimen(expected, actual)

    assert int(actual.host_id) == expected.host.id
    assert actual.phage_identifier_id == expected.phage_identifier.id
