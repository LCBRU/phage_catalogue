import os
import shutil
import pytest
from faker import Faker
from lbrc_flask.pytest.fixtures import *
from phage_catalogue import create_app
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider, LbrcFileProvider, UserProvider
from lbrc_flask.pytest.helpers import login
from phage_catalogue.config import TestConfig
from phage_catalogue.security import ROLENAME_EDITOR, ROLENAME_UPLOADER, init_authorization
from tests.faker import LookupProvider, SpecimenProvider, UploadProvider


@pytest.fixture(scope="function")
def standard_lookups(client, faker):
    return faker.create_standard_lookups()


@pytest.fixture(scope="function")
def loggedin_user(client, faker):
    init_authorization()
    return login(client, faker)


@pytest.fixture(scope="function")
def loggedin_user_editor(client, faker):
    init_authorization()

    user = faker.get_test_user(rolename=ROLENAME_EDITOR)
    return login(client, faker, user)


@pytest.fixture(scope="function")
def loggedin_user_uploader(client, faker):
    init_authorization()

    user = faker.get_test_user(rolename=ROLENAME_UPLOADER)
    return login(client, faker, user)


@pytest.fixture(scope="function")
def app(tmp_path):
    class LocalTestConfig(TestConfig):
        # FILE_UPLOAD_DIRECTORY = tmp_path
        # FILE_UPLOAD_DIRECTORY = 'upload'
        pass

    yield create_app(LocalTestConfig)


@pytest.fixture(scope="function")
def faker():
    result: Faker = Faker("en_GB")
    result.add_provider(UserProvider)
    result.add_provider(LbrcFlaskFakerProvider)
    result.add_provider(LbrcFileProvider)
    result.add_provider(LookupProvider)
    result.add_provider(SpecimenProvider)
    result.add_provider(UploadProvider)

    yield result
