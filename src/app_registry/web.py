# -*- coding: utf-8 -*-
"""Generate the app registry website."""

import codecs
import json
import logging
import shutil
from collections.abc import Mapping
from copy import deepcopy
from functools import singledispatch
from itertools import chain
from pathlib import Path
from typing import Union

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from . import yaml
from .apps_meta import generate_apps_meta
from .apps_meta import validate_apps_meta
from .config import Config
from .core import AppRegistryData
from .core import AppRegistrySchemas


logger = logging.getLogger(__name__)


def build_html(apps_meta, root):
    """Generate the app registry website at the root path."""

    # Create root directory if needed
    root.mkdir(parents=True, exist_ok=True)

    # Load template environment
    env = Environment(
        loader=PackageLoader("mod"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    singlepage_template = env.get_template("singlepage.html")
    main_index_template = env.get_template("main_index.html")

    # Make single-entry page based on singlepage.html
    root.joinpath("apps").mkdir()
    for app_name, app_data in apps_meta["apps"].items():
        subpage_name = app_data["subpage"]
        subpage_abspath = root / subpage_name
        subpage_abspath.parent.mkdir()

        app_html = singlepage_template.render(
            category_map=apps_meta["categories"], **app_data
        )
        with codecs.open(subpage_abspath, "w", "utf-8") as f:
            f.write(app_html)
        yield subpage_abspath

    # Make index page based on main_index.html
    rendered = main_index_template.render(**apps_meta)
    outfile = root / "index.html"
    outfile.write_text(rendered, encoding="utf-8")
    yield outfile


def build_api_v1(apps_meta, base_path):
    outfile = base_path / "apps_meta.json"
    rendered = json.dumps(deepcopy(apps_meta), ensure_ascii=False)
    outfile.write_text(rendered, encoding="utf-8")
    yield outfile


def build_api_v2(apps_meta, base_path):
    # write individual apps metadata files
    base_path.mkdir(parents=True, exist_ok=True)

    for key, value in apps_meta["apps"].items():
        outfile = base_path / f"{key}.metadata.json"
        rendered = json.dumps(deepcopy(value["metainfo"]), ensure_ascii=False)
        outfile.write_text(rendered, encoding="utf-8")
        yield outfile


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

    # Generate the aggregated apps metadata registry.
    apps_meta = generate_apps_meta(data=data)
    if validate_output:
        validate_apps_meta(apps_meta, schemas.apps_meta)

    root = Path(config.build.html)

    # Remove previous build (if present).
    shutil.rmtree(root, ignore_errors=True)

    # Copy static data (if configured).
    if config.build.static_src:
        shutil.copytree(config.build.static_src, root)

    for outfile in chain(
        # Build the html pages.
        build_html(apps_meta, root=root),
        # Build the API endpoints.
        build_api_v1(apps_meta, base_path=root),
        build_api_v2(apps_meta, base_path=root / "api" / "v2"),
    ):
        logger.info(f"  - {outfile.relative_to(root)}")


@build_from_config.register
def _(config: Mapping, *args, **kwargs):
    build_from_config(Config.from_mapping(config), *args, **kwargs)


@build_from_config.register(str)
@build_from_config.register(Path)
def _(config: Union[str, Path], *args, **kwargs):
    build_from_config(Config.from_path(config), *args, **kwargs)
