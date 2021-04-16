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
def mock_schema_endpoints(
    requests_mock, apps_schema, apps_meta_schema, categories_schema, metadata_schema
):
    requests_mock.get(
        "https://aiidalab.github.io/aiidalab-registry/schemas/v2/apps.schema.json",
        text=json.dumps(apps_schema),
    )
    requests_mock.get(
        "https://aiidalab.github.io/aiidalab-registry/schemas/v2/metadata.schema.json",
        text=json.dumps(metadata_schema),
    )
    requests_mock.get(
        "https://aiidalab.github.io/aiidalab-registry/schemas/v2/apps_meta.schema.json",
        text=json.dumps(apps_meta_schema),
    )
    requests_mock.get(
        "https://aiidalab.github.io/aiidalab-registry/schemas/v2/categories.schema.json",
        text=json.dumps(categories_schema),
    )
