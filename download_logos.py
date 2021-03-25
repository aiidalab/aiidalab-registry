#!/usr/bin/env python
from pathlib import Path

import requests


APPS_META = "https://aiidalab.github.io/aiidalab-registry/apps_meta.json"

LOGOS = Path("logos")
LOGOS.mkdir(exist_ok=True)


apps_meta = requests.get(APPS_META).json()

for app_name, app_metadata in apps_meta["apps"].items():
    print(app_name)
    app_logo_path = LOGOS.joinpath(f"{app_name}.png")
    try:
        r_logo = requests.get(app_metadata["logo"])
    except KeyError:
        continue
    r_logo.raise_for_status()
    app_logo_path.write_bytes(r_logo.content)
