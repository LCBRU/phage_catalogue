from sqlalchemy import select
from phage_catalogue.model import Medium, PhageIdentifier, Plasmid, Project, ResistanceMarker, BacterialSpecies, StaffMember, StorageMethod, Strain
from lbrc_flask.database import db


def get_project(name):
    return get_lookup(Project, name)


def get_storage_method(name):
    return get_lookup(StorageMethod, name)


def get_staff_member(name):
    return get_lookup(StaffMember, name)


def get_bacterial_species(name):
    return get_lookup(BacterialSpecies, name)


def get_strain(name):
    return get_lookup(Strain, name)


def get_medium(name):
    return get_lookup(Medium, name)


def get_plasmid(name):
    return get_lookup(Plasmid, name)


def get_resistance_marker(name):
    return get_lookup(ResistanceMarker, name)


def get_phage_identifier(name):
    return get_lookup(PhageIdentifier, name)


def get_lookup(cls, name):
    name = name.strip()

    if not name:
        return None

    q = select(cls).where(cls.name == name)
    result = db.session.execute(q).scalar_one_or_none()

    if not result:
        result = cls(name=name)
    
    return result


def get_bacterial_species_choices():
    l = db.session.execute(
        select(BacterialSpecies).order_by(BacterialSpecies.name)
    ).scalars()
    return [(0, '')] + [(x.id, x.name) for x in l]
