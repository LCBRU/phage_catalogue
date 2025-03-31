from dotenv import load_dotenv

from phage_catalogue.model.specimens import Bacterium

# Load environment variables from '.env' file.
load_dotenv()


def convert_specimens_to_spreadsheet_data(specimens):
    result = []

    for s in specimens:
        sd = {
            "key": s.id,
            "freezer": s.freezer,
            "drawer": s.drawer,
            "position": s.position.upper(),
            "box_number": s.box_number.name,
            "name": s.name,
            "description": s.description,
            "notes": s.notes,
            "date": s.sample_date,
            "project": s.project.name,
            "storage method": s.storage_method.name,
            "staff member": s.staff_member.name,
        }

        if isinstance(s, Bacterium):
            sd.update({
                'bacterial species': s.species.name,
                'strain': s.strain.name,
                'media': s.medium.name,
                'plasmid name': s.plasmid.name,
                'resistance marker': s.resistance_marker.name,
            })
        else:
            sd.update({
                'phage id': s.phage_identifier.name,
                'host species': s.host.name,
            })

        result.append(sd)

    return result


def convert_specimen_to_form_data(specimen):
    result = {
        "key": specimen.id,
        "freezer": specimen.freezer,
        "drawer": specimen.drawer,
        "position": specimen.position.upper(),
        "box_number": specimen.box_number.name,
        "name": specimen.name,
        "description": specimen.description,
        "notes": specimen.notes,
        "sample_date": specimen.sample_date,
        "project": specimen.project.name,
        "storage_method": specimen.storage_method.name,
        "staff_member": specimen.staff_member.name,
    }

    if isinstance(specimen, Bacterium):
        result.update({
            'species_id': specimen.species.id,
            'strain': specimen.strain.name,
            'medium': specimen.medium.name,
            'plasmid': specimen.plasmid.name,
            'resistance_marker': specimen.resistance_marker.name,
        })
    else:
        result.update({
            'phage_identifier': specimen.phage_identifier.name,
            'host_id': specimen.host.id,
        })

    return result


def specimen_form_lookup_names():
    return ['box_number', 'project', 'storage_method', 'staff_member']


def bacterium_form_lookup_names():
    return specimen_form_lookup_names() +  ['strain', 'medium', 'plasmid', 'resistance_marker']


def phage_form_lookup_names():
    return specimen_form_lookup_names() +  ['phage_identifier', 'host_id']
