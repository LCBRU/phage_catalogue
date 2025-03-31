"""Create SpecimenAudit Trigger delete

Revision ID: f1470e032c21
Revises: 17d62399fef0
Create Date: 2025-03-28 13:07:46.943244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1470e032c21'
down_revision = '17d62399fef0'
branch_labels = None
depends_on = None


CREATE_TRIGGER = '''
CREATE TRIGGER trg_specimen_audit_delete
  BEFORE DELETE ON specimen
  FOR EACH ROW
    INSERT INTO specimen_audit (
        specimen_id,
        type,
        freezer,
        drawer,
        position,
        name,
        description,
        notes,
        sample_date,
        box_number,
        project,
        storage_method,
        staff_member,
        audit_action,
        audit_updated_date,
        audit_updated_by,
        species,
        strain,
        medium,
        plasmid,
        resistance_marker,
        phage_identifier,
        host
    )
    VALUES(
        OLD.id,
        OLD.type,
        OLD.freezer,
        OLD.drawer,
        OLD.position,
        OLD.name,
        OLD.description,
        OLD.notes,
        OLD.sample_date,
        (SELECT name FROM box_number WHERE id=OLD.box_number_id),
        (SELECT name FROM project WHERE id=OLD.project_id),
        (SELECT name FROM storage_method WHERE id=OLD.storage_method_id),
        (SELECT name FROM staff_member WHERE id=OLD.staff_member_id),
        'DELETE',
        OLD.last_update_date,
        OLD.last_update_by,
        (SELECT name FROM bacterial_species WHERE id=OLD.species_id),
        (SELECT name FROM strain WHERE id=OLD.strain_id),
        (SELECT name FROM medium WHERE id=OLD.medium_id),
        (SELECT name FROM plasmid WHERE id=OLD.plasmid_id),
        (SELECT name FROM resistance_marker WHERE id=OLD.resistance_marker_id),
        (SELECT name FROM phage_identifier WHERE id=OLD.phage_identifier_id),
        (SELECT name FROM bacterial_species WHERE id=OLD.host_id)
    );
'''

DROP_TRIGGER = '''
DROP TRIGGER trg_specimen_audit_delete;
'''

def upgrade() -> None:
    op.execute(CREATE_TRIGGER)


def downgrade() -> None:
    op.execute(DROP_TRIGGER)
