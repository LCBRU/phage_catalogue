"""Create BacterialSpecies

Revision ID: f78b5800f287
Revises: 6ede5d9b2133
Create Date: 2025-03-27 16:00:46.948726

"""
from pathlib import Path
from alembic import op
import sqlalchemy as sa
from lbrc_flask.database import db
from phage_catalogue.model.specimens import BacterialSpecies
from phage_catalogue import create_app


# revision identifiers, used by Alembic.
revision = 'f78b5800f287'
down_revision = '6ede5d9b2133'
branch_labels = None
depends_on = None


def upgrade() -> None:
    application = create_app()
    application.app_context().push()

    this_path = Path(__file__).resolve().parent

    with open(this_path / 'bacterial_species.txt') as f:
        species = {l.strip().lower(): l.strip() for l in f.readlines()}.values()

    db.session.add_all([BacterialSpecies(name=s) for s in species])
    db.session.commit()

def downgrade() -> None:
    pass
