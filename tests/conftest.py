from functools import partial
from pathlib import Path

import jsonschema
import pytest

from app_registry import AppRegistrySchemas
from app_registry.config import Config
from app_registry import yaml

ROOT = Path(__file__).parent.parent.resolve()
CONFIG_YAML = ROOT.joinpath("config.yaml")


@pytest.fixture
def validate():
    return partial(jsonschema.validate, format_checker=jsonschema.draft7_format_checker)


@pytest.fixture
def config_yaml():
    return yaml.load(CONFIG_YAML)


@pytest.fixture
def config():
    return Config.from_path(CONFIG_YAML)


@pytest.fixture
def schemas(config):
    return AppRegistrySchemas.from_path(Path(config.schemas.path))


@pytest.fixture
def mock_schema_endpoints(requests_mock):
    schemas_path = ROOT.joinpath("src/static/schemas")
    schemas_endpoint = "https://raw.githubusercontent.com/aiidalab/aiidalab-registry/master/src/static/schemas"
    for schema in schemas_path.glob("**/*.schema.json"):
        endpoint = f"{schemas_endpoint}/{schema.relative_to(schemas_path)}"
        requests_mock.get(endpoint, text=schema.read_text())
