import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from '.env' file.
load_dotenv()

from lbrc_flask.config import BaseConfig, BaseTestConfig

class ConfigMixin:
    FILE_UPLOAD_DIRECTORY = Path(os.environ["FILE_UPLOAD_DIRECTORY"])

class Config(BaseConfig, ConfigMixin):
    pass

class TestConfig(BaseTestConfig, ConfigMixin):
    FILE_UPLOAD_DIRECTORY = Path(os.environ["FILE_UPLOAD_DIRECTORY"]) / 'test'
