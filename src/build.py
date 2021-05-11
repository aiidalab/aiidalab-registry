#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from contextlib import contextmanager
from contextlib import nullcontext
from pathlib import Path

import click
import requests_mock
from app_registry import build_from_config
from app_registry.config import Config
from app_registry.util import load_json


logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).parent.parent.resolve()


@contextmanager
def _mock_schemas_endpoints(schemas_path):
    with requests_mock.Mocker(real_http=True) as mocker:
        for schema_path in Path(schemas_path).glob("*.schema.json"):
            schema = load_json(schema_path)
            mocker.get(schema["$id"], text=schema_path.read_text())
        yield


@click.command(help="Build the app store website and API endpoints.")
@click.option(
    "--config",
    type=click.Path(),
    default=ROOT.joinpath("config.yaml"),
    help="Path to the configuration file. Defaults to 'config.yaml' within the repository root.",
)
@click.option(
    "--validate/--no-validate",
    is_flag=True,
    default=True,
    show_default=True,
    help="Validate inputs and outputs against the published or local schemas.",
)
@click.option(
    "-m",
    "--mock-schemas-endpoints",
    "mock_schemas",
    is_flag=True,
    help="Mock the schemas endpoints such that the local versions are used insted of the published ones.",
)
def cli(config, validate, mock_schemas):
    config = Config.from_path(config)
    maybe_mock = (
        _mock_schemas_endpoints(config.schemas.path) if mock_schemas else nullcontext()
    )
    with maybe_mock:
        build_from_config(config, validate_output=validate, validate_input=validate)


if __name__ == "__main__":
    cli()
