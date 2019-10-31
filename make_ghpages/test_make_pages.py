# -*- coding: utf-8 -*-

import pytest
import os
import json

import exceptions as exc
import make_pages as mp

TEST_GIT_URL = "https://github.com/aiidalab/aiidalab-registry"

### UTILITY FUNCTIONS ###
def setup_apps_json(tmpdir):
    """ Setup apps.json file
    Create artificial apps.json file
    """
    apps_json = {
        "test": {
            "git_url": TEST_GIT_URL,
            "meta_url": "file://{}".format(os.path.join(tmpdir, 'metadata.json')),
            "categories": ["utilities"]
        }
    }
    return apps_json


def write_json_files(tmpdir, metadata=None, apps=None):
    """Write JSON files to tmpdir"""
    if not metadata:
        metadata = {}

    if not apps:
        apps = setup_apps_json(tmpdir)

    with open(os.path.join(tmpdir, 'metadata.json'), 'w') as fp:
        json.dump(metadata, fp)
    
    with open(os.path.join(tmpdir, 'apps.json'), 'w') as fp:
        json.dump(apps, fp)


### TESTS ###
def test_validate_logo(tmpdir):
    """ Test validate logo in get_logo_url(logo_rel_path, meta_url)
    Make sure exception is raised when logo URL is present,
    but points to a non-existent location.
    """
    # Setup
    metadata_test = {
        "logo": "img/test.png"  # Non-existent file
    }

    write_json_files(tmpdir, metadata=metadata_test)

    # Test
    with pytest.raises(exc.MissingLogo):
        # Load apps.json
        with open(os.path.join(tmpdir, 'apps.json')) as fp:
            app_raw_data = json.load(fp)
        app_data = app_raw_data['test']

        # Load metadata.json (similarly to make_pages.py)
        meta_info = mp.get_meta_info(app_data['meta_url'])
        app_data['metainfo'] = mp.validate_meta_info('test', meta_info, app_data['git_url'])

        # Get logo URL
        app_data['logo'] = mp.get_logo_url(app_data['metainfo']['logo'], app_data['meta_url'])


def test_get_logo_url(tmpdir):
    """ Test get_logo_url(logo_rel_path, meta_url)
    Making path to logo equal to path to metadata.json to test path to "logo"
    is correctly found.
    """
    # Setup
    metadata_test = {
        "logo": "metadata.json"  # While not image, still valid path
    }

    write_json_files(tmpdir, metadata=metadata_test)

    # Test
    # Load apps.json
    with open(os.path.join(tmpdir, 'apps.json')) as fp:
        app_raw_data = json.load(fp)
    app_data = app_raw_data['test']

    # Load metadata.json (similarly to make_pages.py)
    meta_info = mp.get_meta_info(app_data['meta_url'])
    app_data['metainfo'] = mp.validate_meta_info('test', meta_info, app_data['git_url'])

    # Get logo URL
    app_data['logo'] = mp.get_logo_url(app_data['metainfo']['logo'], app_data['meta_url'])

    assert app_data['logo'] == app_data['meta_url']
