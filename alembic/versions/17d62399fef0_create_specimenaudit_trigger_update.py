"""Create SpecimenAudit Trigger update

Revision ID: 17d62399fef0
Revises: 14ad631a54b2
Create Date: 2025-03-28 13:06:41.027221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17d62399fef0'
down_revision = '14ad631a54b2'
branch_labels = None
depends_on = None


CREATE_TRIGGER = '''
CREATE TRIGGER trg_specimen_audit_update
  BEFORE UPDATE ON specimen
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
        NEW.id,
        NEW.type,
        NEW.freezer,
        NEW.drawer,
        NEW.position,
        NEW.name,
        NEW.description,
        NEW.notes,
        NEW.sample_date,
        (SELECT name FROM box_number WHERE id=NEW.box_number_id),
        (SELECT name FROM project WHERE id=NEW.project_id),
        (SELECT name FROM storage_method WHERE id=NEW.storage_method_id),
        (SELECT name FROM staff_member WHERE id=NEW.staff_member_id),
        'UPDATE',
        NEW.last_update_date,
        NEW.last_update_by,
        (SELECT name FROM bacterial_species WHERE id=NEW.species_id),
        (SELECT name FROM strain WHERE id=NEW.strain_id),
        (SELECT name FROM medium WHERE id=NEW.medium_id),
        (SELECT name FROM plasmid WHERE id=NEW.plasmid_id),
        (SELECT name FROM resistance_marker WHERE id=NEW.resistance_marker_id),
        (SELECT name FROM phage_identifier WHERE id=NEW.phage_identifier_id),
        (SELECT name FROM bacterial_species WHERE id=NEW.host_id)
    );
'''

DROP_TRIGGER = '''
DROP TRIGGER trg_specimen_audit_update;
'''

def upgrade() -> None:
    op.execute(CREATE_TRIGGER)


def downgrade() -> None:
    op.execute(DROP_TRIGGER)
