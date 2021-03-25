#!/usr/bin/env python
import json
from urllib.parse import urlsplit
from pathlib import Path

import click
import requests

APPS_META = "https://aiidalab.github.io/aiidalab-registry/apps_meta.json"


def _fetch(url):
    o = urlsplit(url)
    if not o.netloc or o.netloc == "file://":
        return json.loads(Path(o.path).read_text())
    else:
        return requests.get(url).json()


def _migrate_app_metadata(app_metadata):
    app_metadata.pop("version", None)
    if "requires" in app_metadata:
        app_metadata["dependencies"] = {
            "package-ecosystem": "pip",
            "requires": app_metadata.pop("requires"),
        }
    return app_metadata


def migrate_app_registry_entry(app_registry_entry):
    metadata = _migrate_app_metadata(app_registry_entry["metainfo"])
    if "git_url" in app_registry_entry:
        metadata["git_url"] = app_registry_entry["git_url"]
    try:
        logo_rl = app_registry_entry["logo"]
    except KeyError:
        pass
    else:
        metadata["logo"] = logo_rl

    metadata["categories"] = app_registry_entry["categories"]
    return metadata


def compile_revised_apps_json(apps_meta):
    for app_name, app_metadata in apps_meta["apps"].items():
        yield app_name, migrate_app_registry_entry(app_metadata)


@click.group()
def cli():
    pass


@cli.command("app-metadata")
@click.argument("url")
def migrate_app_metadata(url):
    app_metadata = _fetch(url)
    print(json.dumps(_migrate_app_metadata(app_metadata), indent=4))


@cli.command("apps-registry")
@click.argument("url")
def migrate_apps_registry(url):
    apps_meta = _fetch(url)
    revised_apps_json = dict(compile_revised_apps_json(apps_meta))
    print(json.dumps(revised_apps_json, indent=4))


if __name__ == "__main__":
    cli()
