# -*- coding: utf-8 -*-
"""Generate the aggregated registry metadata from the registry data."""

import logging
from collections import OrderedDict

import jsonschema

from . import util


logger = logging.getLogger(__name__)


def complete_metadata(app_name, metadata, git_url):
    """Fill-in any missing data for a given app metadata."""

    metadata.setdefault("state", "registered")
    metadata.setdefault("title", app_name)
    if git_url:
        metadata.setdefault("authors", util.get_git_author(git_url))
    return metadata


def fetch_app_data(app_data, app_name):
    """Fetch additional data for the given app data."""

    # Get Git URL, fail build if git_url is not found or wrong
    git_url = app_data.get("git_url", "")
    hosted_on = util.get_hosted_on(git_url) if git_url else None

    # Check if categories are specified, warn if not
    if "categories" not in app_data:
        logger.info("  >> WARNING: No categories specified.")

    app_data["metainfo"] = complete_metadata(
        app_name, app_data.pop("metadata"), git_url
    )
    if git_url:
        app_data["gitinfo"] = util.get_git_branches(git_url)
    if hosted_on:
        app_data["hosted_on"] = hosted_on

    return app_data


def validate_apps_meta(apps_meta, apps_meta_schema):
    """Validate the apps_meta file against the corresponding JSON-schema."""

    jsonschema.validate(instance=apps_meta, schema=apps_meta_schema)

    for app, appdata in apps_meta["apps"].items():
        for category in appdata["categories"]:
            assert category in apps_meta["categories"]


def generate_apps_meta(data):
    """Generate the comprehensive app registry index.

    This function produces the apps_meta file, a comprehensive metadata directory that
    combines the apps data and additionally fetched data (such as the git info).

    The apps_meta file can be used to generate the app registery website and if
    published online, by other platforms that want to operate on the app registry
    and, e.g., integrate with registered apps.
    """

    apps_meta = {
        "apps": OrderedDict(),
        "categories": data.categories,
    }
    logger.info("Fetching app data...")
    for app_name in sorted(data.apps.keys()):
        assert util.get_html_app_fname(app_name) == f"{app_name}.html"
        logger.info(f"  - {app_name}")
        app_data = fetch_app_data(data.apps[app_name], app_name)
        app_data["name"] = app_name
        app_data["subpage"] = f"apps/{app_name}/index.html"
        app_data["meta_url"] = ""
        apps_meta["apps"][app_name] = app_data

    return apps_meta
