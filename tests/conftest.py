import shutil
import pytest
from faker import Faker
from lbrc_flask.pytest.fixtures import *
from phage_catalogue.config import TestConfig
from phage_catalogue import create_app
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider, LbrcFileProvider
from lbrc_flask.pytest.helpers import login
from tests.faker import LookupProvider, SpecimenProvider, UploadProvider


@pytest.fixture(scope="function")
def standard_lookups(client, faker):
    return faker.create_standard_lookups()


@pytest.fixture(scope="function")
def loggedin_user(client, faker):
    return login(client, faker)


@pytest.fixture(scope="function")
def app():
    yield create_app(TestConfig)

    shutil.rmtree(TestConfig().FILE_UPLOAD_DIRECTORY, ignore_errors=True)


@pytest.fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(LbrcFlaskFakerProvider)
    result.add_provider(LbrcFileProvider)
    result.add_provider(LookupProvider)
    result.add_provider(SpecimenProvider)
    result.add_provider(UploadProvider)    

    yield result
