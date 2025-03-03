from sqlalchemy import select
from phage_catalogue.model import Host, Medium, PhageIdentifier, Plasmid, Project, ResistanceMarker, Species, StaffMember, StorageMethod, Strain
from lbrc_flask.database import db


def get_project(name):
    return get_lookup(Project, name)


def get_storage_method(name):
    return get_lookup(StorageMethod, name)


def get_staff_member(name):
    return get_lookup(StaffMember, name)


def get_species(name):
    return get_lookup(Species, name)


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


def get_host(name):
    return get_lookup(Host, name)


def get_lookup(cls, name):
    name = name.strip()

    if not name:
        return None

    q = select(cls).where(cls.name == name)
    result = db.session.execute(q).scalar_one_or_none()

    if not result:
        result = cls(name=name)
    
    return result

