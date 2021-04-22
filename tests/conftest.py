import json
from functools import partial
from pathlib import Path

import jsonschema
import pytest

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
def apps_schema(config_yaml):
    return json.loads(ROOT.joinpath(config_yaml["schemas"]["apps"]).read_text())


@pytest.fixture
def apps_meta_schema(config_yaml):
    return json.loads(ROOT.joinpath(config_yaml["schemas"]["apps_meta"]).read_text())


@pytest.fixture
def categories_schema(config_yaml):
    return json.loads(ROOT.joinpath(config_yaml["schemas"]["categories"]).read_text())


@pytest.fixture
def metadata_schema(config_yaml):
    return json.loads(ROOT.joinpath(config_yaml["schemas"]["metadata"]).read_text())


@pytest.fixture
def mock_schema_endpoints(requests_mock):
    schemas_path = ROOT.joinpath("src/static/schemas")
    schemas_endpoint = "https://aiidalab.github.io/aiidalab-registry/schemas"
    for schema in schemas_path.glob("**/*.schema.json"):
        endpoint = f"{schemas_endpoint}/{schema.relative_to(schemas_path)}"
        requests_mock.get(endpoint, text=schema.read_text())
