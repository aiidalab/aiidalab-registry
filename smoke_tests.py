import json
from pathlib import Path

from ruamel.yaml import YAML

BUILD_DIR = 'build/api/v1/apps'

def test_all_apps_exist():
    yaml = YAML(typ="safe")
    with open('apps.yaml') as f:
        all_data = yaml.load(f)

    for app in all_data:
        Path(BUILD_DIR, f'{app}.json').is_file()


def test_awb_versions():
    with open(f'{BUILD_DIR}/aiidalab-widgets-base.json') as f:
        awb_data = json.load(f)

    releases = tuple(awb_data["releases"].keys())
    assert 'v1.0.0' in releases
    assert 'v2.0.2' in releases
    assert 'v2.2.3' in releases
    assert 'v2.5.1' in releases
    assert 'v3.0.0a0' not in releases

def test_qeapp_versions():
    with open(f'{BUILD_DIR}/quantum-espresso.json') as f:
        qeapp_data = json.load(f)

    releases = tuple(qeapp_data["releases"].keys())
    assert 'v22.05.0' in releases
    assert 'v26.06.7' in releases
