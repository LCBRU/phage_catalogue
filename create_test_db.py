#!/usr/bin/env python3

from dotenv import load_dotenv
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from alembic.config import Config
from alembic import command
from faker import Faker
from phage_catalogue.model import *

fake = Faker()

# Load environment variables from '.env' file.
load_dotenv()

from phage_catalogue import create_app

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")

# Bacteria
bacteria = []

with open('example_data/bacteria.txt') as f:
    for b in {l.strip().title() for l in f.readlines()}:
        bacteria.append(BacterialSpecies(name=b))

db.session.add_all(bacteria)
db.session.commit()

db.session.close()
