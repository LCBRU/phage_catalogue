from sqlalchemy import select
from phage_catalogue.model import Specimen
from lbrc_flask.database import db
from phage_catalogue.services.lookups import get_medium, get_phage_identifier, get_plasmid, get_project, get_resistance_marker, get_bacterial_species, get_staff_member, get_storage_method, get_strain


def specimen_search_query(search_data):
    return select(Specimen)


def specimen_bacterium_save(bacterium, data):
    bacterium.species = get_bacterial_species(data['species'])
    bacterium.strain = get_strain(data['strain'])
    bacterium.medium = get_medium(data['medium'])
    bacterium.plasmid = get_plasmid(data['plasmid'])
    bacterium.resistance_marker = get_resistance_marker(data['resistance_marker'])
    specimen_save(bacterium, data)


def specimen_phage_save(bacterium, data):
    bacterium.phage_identifier = get_phage_identifier(data['phage_identifier'])
    bacterium.host = get_bacterial_species(data['host'])
    specimen_save(bacterium, data)


def specimen_save(specimen, data):
    specimen.sample_date = data['sample_date']
    specimen.freezer = data['freezer']
    specimen.draw = data['draw']
    specimen.position = data['position']
    specimen.description = data['description']
    specimen.project = get_project(data['project'])
    specimen.storage_method = get_storage_method(data['storage_method'])
    specimen.staff_member = get_staff_member(data['staff_member'])
    specimen.notes = data['notes']

    db.session.add(specimen)
    db.session.commit()
