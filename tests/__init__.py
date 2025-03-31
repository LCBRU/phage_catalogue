from dotenv import load_dotenv

from phage_catalogue.model.specimens import Bacterium

# Load environment variables from '.env' file.
load_dotenv()


def convert_specimens_to_spreadsheet_data(specimens):
    result = []

    for s in specimens:
        if isinstance(s, Bacterium):
            result.append({
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
                'bacterial species': s.species.name,
                'strain': s.strain.name,
                'media': s.medium.name,
                'plasmid name': s.plasmid.name,
                'resistance marker': s.resistance_marker.name,
            })
        else:
            result.append({
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
                'phage id': s.phage_identifier.name,
                'host species': s.host.name,
            })
    
    return result
