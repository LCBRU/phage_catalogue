#!/usr/bin/env python3

from dotenv import load_dotenv
from lbrc_flask.database import db
from alembic.config import Config
from alembic import command
from phage_catalogue.model.specimens_audit import *
from phage_catalogue.model.specimens import *
from phage_catalogue.model.lookups import *
from phage_catalogue.model.uploads import *
from faker import Faker
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider
from phage_catalogue.security import init_authorization
from tests.faker import LookupProvider, SpecimenProvider, UploadProvider


fake = Faker("en_GB")
fake.add_provider(LbrcFlaskFakerProvider)
fake.add_provider(LookupProvider)
fake.add_provider(SpecimenProvider)
fake.add_provider(UploadProvider)


# Load environment variables from '.env' file.
load_dotenv()

from phage_catalogue import create_app

application = create_app()
application.app_context().push()
db.create_all()
init_authorization()

alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")

fake.create_standard_lookups()
db.session.commit()

for _ in range(20):
    fake.specimen().get(save=True)

db.session.commit()

db.session.close()
