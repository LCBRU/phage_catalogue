from sqlalchemy import or_, select
from phage_catalogue.model import Bacterium, Phage, Project, Specimen, StaffMember, StorageMethod
from lbrc_flask.database import db
from phage_catalogue.services.lookups import get_medium, get_phage_identifier, get_plasmid, get_project, get_resistance_marker, get_staff_member, get_storage_method, get_strain


def specimen_search_query(search_data=None):
    q = select(Specimen)

    search_data = search_data or []

    if x := search_data.get('search'):
        for word in x.split():
            q = q.where(or_(
                Specimen.description.like(f"%{word}%"),
                Specimen.notes.like(f"%{word}%"),
            ))

    if x := search_data.get('type'):
        q = q.where(Specimen.type == x)

    if x := search_data.get('start_date'):
        q = q.where(Specimen.sample_date >= x)

    if x := search_data.get('end_date'):
        q = q.where(Specimen.sample_date <= x)

    if x := search_data.get('freezer'):
        q = q.where(Specimen.freezer == x)

    if x := search_data.get('draw'):
        q = q.where(Specimen.draw == x)

    if x := search_data.get('position'):
        q = q.where(Specimen.position == x)

    if x := search_data.get('project'):
        q = q.where(Specimen.project.has(Project.name.like(f"%{x}%")))

    if x := search_data.get('storage_method'):
        q = q.where(Specimen.storage_method.has(StorageMethod.name.like(f"%{x}%")))

    if x := search_data.get('staff_member'):
        q = q.where(Specimen.staff_member.has(StaffMember.name.like(f"%{x}%")))

    if x := search_data.get('species_id'):
        q = q.where(Bacterium.species_id == x)

    if x := search_data.get('strain'):
        q = q.where(Bacterium.strain.has(StaffMember.name.like(f"%{x}%")))

    if x := search_data.get('medium'):
        q = q.where(Bacterium.medium.has(StaffMember.name.like(f"%{x}%")))

    if x := search_data.get('plasmid'):
        q = q.where(Bacterium.plasmid.has(StaffMember.name.like(f"%{x}%")))

    if x := search_data.get('resistance_marker'):
        q = q.where(Bacterium.resistance_marker.has(StaffMember.name.like(f"%{x}%")))

    if x := search_data.get('phage_identifier'):
        q = q.where(Phage.phage_identifier.has(StaffMember.name.like(f"%{x}%")))

    if x := search_data.get('host_id'):
        q = q.where(Phage.host_id == x)

    return q


def specimen_bacterium_save(bacterium, data):
    bacterium.species_id = data['species_id']
    bacterium.strain = get_strain(data['strain'])
    bacterium.medium = get_medium(data['medium'])
    bacterium.plasmid = get_plasmid(data['plasmid'])
    bacterium.resistance_marker = get_resistance_marker(data['resistance_marker'])
    specimen_save(bacterium, data)


def specimen_phage_save(phage, data):
    phage.phage_identifier = get_phage_identifier(data['phage_identifier'])
    phage.host_id = data['host_id']
    specimen_save(phage, data)


def specimen_save(specimen, data):
    specimen.sample_date = data['sample_date']
    specimen.freezer = data['freezer']
    specimen.draw = data['draw']
    specimen.position = (data['position'] or '').upper()
    specimen.description = data['description']
    specimen.project = get_project(data['project'])
    specimen.storage_method = get_storage_method(data['storage_method'])
    specimen.staff_member = get_staff_member(data['staff_member'])
    specimen.notes = data['notes']

    db.session.add(specimen)
    db.session.commit()


def get_type_choices():
    return [('', ''), ('Bacterium', 'Bacterium'), ('Phage', 'Phage')]