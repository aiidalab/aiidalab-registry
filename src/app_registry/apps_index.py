# -*- coding: utf-8 -*-
"""Generate the apps index including all aggregated metadata."""
import logging
from collections import OrderedDict
from dataclasses import asdict
from copy import deepcopy

import jsonschema

from . import util
from .releases import gather_releases


logger = logging.getLogger(__name__)


def _determine_app_name(app_id):
    """Currently the app name is identical to its id."""
    assert util.get_html_app_fname(app_id) == f"{app_id}.html"
    return app_id


def _complete_metadata(app_metadata):
    for key in (  # remove deprecated keys from app metadata
        "logo",
        "requires",
        "version",
    ):
        if key in app_metadata:
            del app_metadata[key]


def _fetch_app_data(app_id, app_data, scan_environment):
    # Gather all release data.
    app_data["name"] = _determine_app_name(app_id)
    app_data["releases"] = {
        version: asdict(release)
        for version, release in gather_releases(app_data, scan_environment)
    }
    app_data.setdefault("categories", [])
    _complete_metadata(app_data["metadata"])
    return app_data


def generate_apps_index(data, scan_environment):
    """Generate the comprehensive app index.

    This index is built from the apps data and includes additional information
    such as the releases.
    """

    apps_data = OrderedDict()
    index = {
        "apps": OrderedDict(),
        "categories": data.categories,
    }
    logger.info("Fetching app data...")

    for app_id in sorted(data.apps.keys()):
        logger.info(f"  - {app_id}")
        apps_data[app_id] = _fetch_app_data(
            app_id, deepcopy(data.apps[app_id]), scan_environment
        )
        index["apps"][app_id] = {
            key: apps_data[app_id][key] for key in ("categories", "name")
        }

    return index, apps_data


def validate_apps_index_and_apps(apps_index, apps_index_schema, apps, app_schema):
    """Validate the apps_index file."""

    # Validate apps index against schema
    jsonschema.validate(instance=apps_index, schema=apps_index_schema)

    # Validate index categories
    for app_id, apps_index_entry in apps_index["apps"].items():
        for category in apps_index_entry["categories"]:
            assert category in apps_index["categories"]

    # Validate all apps
    for app in apps:
        jsonschema.validate(instance=app, schema=app_schema)
