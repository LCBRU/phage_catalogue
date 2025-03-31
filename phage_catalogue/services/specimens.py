from sqlalchemy import or_, select
from lbrc_flask.database import db
from phage_catalogue.model.specimens import Bacterium, Phage, Project, Specimen, StaffMember, StorageMethod
from phage_catalogue.services.lookups import get_bacterial_species, get_box_number, get_medium, get_phage_identifier, get_plasmid, get_project, get_resistance_marker, get_staff_member, get_storage_method, get_strain


def specimen_search_query(search_data=None):
    q = select(Specimen)

    search_data = search_data or []

    if x := search_data.get('search'):
        for word in x.split():
            q = q.where(or_(
                Specimen.description.like(f"%{word}%"),
                Specimen.notes.like(f"%{word}%"),
                Specimen.name.like(f"%{word}%"),
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


def specimen_bacteria_save(data):
    for d in data:
        if d['key']:
            bacterium = db.session.get(Bacterium, d['key'])
        else:
            bacterium = Bacterium()
        specimen_bacterium_save(bacterium, d)


def specimen_bacterium_save(bacterium, data):
    if 'species_id' in data:
        bacterium.species_id = data['species_id']
    else:
        bacterium.species_id = get_bacterial_species(data['species']).id
    bacterium.strain = get_strain(data['strain'])
    bacterium.medium = get_medium(data['medium'])
    bacterium.plasmid = get_plasmid(data['plasmid'])
    bacterium.resistance_marker = get_resistance_marker(data['resistance_marker'])
    specimen_save(bacterium, data)


def specimen_phages_save(data):
    for d in data:
        if d['key']:
            phage = db.session.get(Phage, d['key'])
        else:
            phage = Phage()
        specimen_phage_save(phage, d)


def specimen_phage_save(phage, data):
    phage.phage_identifier = get_phage_identifier(data['phage_identifier'])
    if 'host_id' in data:
        phage.host_id = data['host_id']
    else:
        phage.host_id = get_bacterial_species(data['host']).id
    specimen_save(phage, data)


def specimen_save(specimen, data):
    specimen.name = data['name']
    specimen.sample_date = data['sample_date']
    specimen.freezer = data['freezer']
    specimen.drawer = data['drawer']
    specimen.position = (data['position'] or '').upper()
    specimen.description = data['description']
    specimen.box_number = get_box_number(data['box_number'])
    specimen.project = get_project(data['project'])
    specimen.storage_method = get_storage_method(data['storage_method'])
    specimen.staff_member = get_staff_member(data['staff_member'])
    specimen.notes = data['notes']

    db.session.add(specimen)


def get_type_choices():
    return [('', ''), ('Bacterium', 'Bacterium'), ('Phage', 'Phage')]