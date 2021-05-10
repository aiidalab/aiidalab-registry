# -*- coding: utf-8 -*-
"""Generate the app registry website."""

import json
import logging
import os
import shutil
from collections.abc import Mapping
from copy import deepcopy
from functools import singledispatch
from itertools import chain
from pathlib import Path
from subprocess import run
from typing import Union

from . import api
from . import yaml
from .html import build_html
from .config import Config
from .core import AppRegistryData
from .core import AppRegistrySchemas


logger = logging.getLogger(__name__)


def copy_static_tree(base_path, static_src):
    for root, dirs, files in os.walk(static_src):
        # Create directory
        base_path.joinpath(Path(root).relative_to(static_src)).mkdir(
            parents=True, exist_ok=True
        )

        # Copy all files
        for filename in files:
            src = Path(root).joinpath(filename)
            dst = base_path.joinpath(Path(root).relative_to(static_src), filename)
            dst.write_bytes(src.read_bytes())
            yield dst


@singledispatch
def build_from_config(
    config: Config, validate_output: bool = True, validate_input: bool = False
):
    """Build the app registry website (including schema files) from the configuration.

    This function poses an alternative to a more comprehensive build script and allows
    for the control of the registry website generation via a configuration file.

    This is an example for such a configuration file:

        api_version: v1
        data:
          apps:  apps.yaml
          categories: categories.yaml
        schemas:
          path: src/static/schemas/v2
        build:
          html: build/html  # where to build the page (will be overwritten!)
          static_src: src/static  # static content to be copied
    """

    # Parse the schemas from path specified in the configuration.
    schemas = AppRegistrySchemas.from_path(Path(config.schemas.path))

    # Parse the apps and categories data from the paths given in the configuration.
    data = AppRegistryData(
        apps=yaml.load(Path(config.data.apps)),
        categories=yaml.load(Path(config.data.categories)),
    )
    if validate_input:
        data.validate(schemas)

    root = Path(config.build.html)

    # Remove previous build (if present) and re-create root directory.
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    # Prepare environment command
    def scan_environment(url):
        return json.loads(
            run(
                f"{config.environments.cmd} {url}",
                shell=True,
                check=True,
                capture_output=True,
            ).stdout
        )

    # Build the website and API endpoints.
    for outfile in chain(
        # Copy static files (if configured)
        (
            copy_static_tree(base_path=root, static_src=config.build.static_src)
            if config.build.static_src
            else ()
        ),
        # Build the html pages.
        build_html(base_path=root, data=deepcopy(data)),
        # Build the API endpoints.
        api.build_api_v0(base_path=root, data=deepcopy(data)),
        api.build_api_v1(
            base_path=root / "api" / "v1",
            data=deepcopy(data),
            scan_environment=scan_environment,
        ),
    ):
        logger.info(f"  - {outfile.relative_to(root)}")

    if validate_output:
        api.validate_api_v0(base_path=root, schemas=schemas)
        api.validate_api_v1(base_path=root / "api" / "v1", schemas=schemas)


@build_from_config.register
def _(config: Mapping, *args, **kwargs):
    build_from_config(Config.from_mapping(config), *args, **kwargs)


@build_from_config.register(str)
@build_from_config.register(Path)
def _(config: Union[str, Path], *args, **kwargs):
    build_from_config(Config.from_path(config), *args, **kwargs)
