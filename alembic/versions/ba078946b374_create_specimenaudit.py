"""Create SpecimenAudit

Revision ID: ba078946b374
Revises: f78b5800f287
Create Date: 2025-03-27 16:47:16.013643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba078946b374'
down_revision = 'f78b5800f287'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('specimen_audit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('specimen_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('freezer', sa.Integer(), nullable=False),
    sa.Column('drawer', sa.Integer(), nullable=False),
    sa.Column('position', sa.String(length=20), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.Column('sample_date', sa.Date(), nullable=False),
    sa.Column('box_number', sa.String(length=100), nullable=False),
    sa.Column('project', sa.String(length=100), nullable=False),
    sa.Column('storage_method', sa.String(length=100), nullable=False),
    sa.Column('staff_member', sa.String(length=100), nullable=False),
    sa.Column('audit_action', sa.String(length=200), nullable=False),
    sa.Column('audit_updated_date', sa.Date(), nullable=False),
    sa.Column('audit_updated_by', sa.String(length=200), nullable=False),
    sa.Column('species', sa.String(length=100), nullable=True),
    sa.Column('strain', sa.String(length=100), nullable=True),
    sa.Column('medium', sa.String(length=100), nullable=True),
    sa.Column('plasmid', sa.String(length=100), nullable=True),
    sa.Column('resistance_marker', sa.String(length=100), nullable=True),
    sa.Column('phage_identifier', sa.String(length=100), nullable=True),
    sa.Column('host', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_specimen_audit_type'), 'specimen_audit', ['type'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_specimen_audit_type'), table_name='specimen_audit')
    op.drop_table('specimen_audit')
    # ### end Alembic commands ###
