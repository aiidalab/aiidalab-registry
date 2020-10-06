# -*- coding: utf-8 -*-

import codecs
import json
import os
import shutil
import string
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
import exceptions as exc

## Requires jinja2 >= 2.9
from jinja2 import Environment, PackageLoader, select_autoescape

### BEGIN configuration
# inputs
apps_file = 'apps.json'
categories_file = 'categories.json'
templates_folder = 'templates'
static_folder = 'static'

# outputs
out_folder = 'out'
html_subfolder_name = 'apps' # subfolder for HTMLs of apps
apps_meta_file = 'apps_meta.json'

# configuration
TIMEOUT_SECONDS = 30  # seconds
### END configuration


def get_html_app_fname(app_name):
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = "".join(c for c in app_name if c in valid_characters)

    return "{}.html".format(simple_string)


def get_hosted_on(url):
    try:
        urlopen(url, timeout=TIMEOUT_SECONDS)
    except Exception:
        raise exc.MissingGit("Value for 'git_url' in apps.json may be wrong: '{}'".format(url))

    netloc = urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

    return netloc


def get_meta_info(json_url):
    try:
        response = urlopen(json_url, timeout=TIMEOUT_SECONDS)
        json_txt = response.read()
    except Exception:
        raise exc.MissingMetadata("Value for 'meta_url' in apps.json may be wrong: '{}'".format(json_url))

    try:
        json_data = json.loads(json_txt)
    except ValueError:
        raise exc.WrongMetadata("Cannot perform 'json.loads()' on given metadata.json file.")

    return json_data

def get_git_branches(git_url):
    from dulwich.client import get_transport_and_path_from_url
    t, p = get_transport_and_path_from_url(git_url)
    branches = t.get_refs(p)
    res = {}
    for key, value in branches.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res

def get_git_author(git_url):
    git_author = urlparse(git_url).path

    git_author = git_author.split('/')[1]

    ## Special condition, only valid when git_author is 'aiidalab'
    if git_author == 'aiidalab':
        git_author = 'AiiDA Lab Team'

    return git_author

def complete_meta_info(app_name, meta_info, git_url):
    if 'state' not in meta_info:
        meta_info['state'] = 'registered'

    if 'title' not in meta_info:
        meta_info['title'] = app_name

    if 'authors' not in meta_info:
        meta_info['authors'] = get_git_author(git_url)

    return meta_info

def validate_categories(categories, raw_data):
    if not isinstance(categories, list):
        raise exc.MissingCategories("Value for 'categories' in apps.json must be a list: '{}'".format(str(categories)))

    if not categories:
        print("  >> WARNING: No categories specified.")
        return

    for category in categories:
        if category not in raw_data:
            raise exc.WrongCategory("Specified category '{}' not found in list {}. ".format(category, str(raw_data.keys()))
                                    + "Edit categories.json to propose new categories.")

def get_logo_url(logo_rel_path, meta_url):
    logo_url = meta_url[:-len('metadata.json')] + logo_rel_path

    # Validate url to logo
    try:
        urlopen(logo_url, timeout=TIMEOUT_SECONDS)
    except Exception:
        raise exc.MissingLogo("Value for 'logo' in your app's metadata.json may be wrong: '{}'".format(logo_url))

    return logo_url


def fetch_app_data(app_data, app_name):
    # Get Git URL, fail build if git_url is not found or wrong
    if 'git_url' in app_data:
        hosted_on = get_hosted_on(app_data['git_url'])
    else:
        raise exc.MissingGit("No 'git_url' key for '{}' in apps.json".format(app_name))

    # Get metadata.json from the project;
    # fail build if meta_url is not found or wrong
    if 'meta_url' in app_data:
        meta_info = get_meta_info(app_data['meta_url'])
    else:
        raise exc.MissingMetadata("No 'meta_url' key for '{}' in apps.json".format(app_name))

    # Check if categories are specified, warn if not
    if 'categories' not in app_data:
        print("  >> WARNING: No categories specified.")
    # Check correct categories are specified
    else:
        validate_categories(app_data['categories'], apps_meta['categories'])

    app_data['metainfo'] = complete_meta_info(app_name, meta_info, app_data['git_url'])
    app_data['gitinfo'] = get_git_branches(app_data['git_url'])
    app_data['hosted_on'] = hosted_on

    # Get logo URL, if it has been specified
    if 'logo' in app_data['metainfo']:
        app_data['logo'] = get_logo_url(app_data['metainfo']['logo'], app_data['meta_url'])

    return app_data


def generate_apps_meta(apps_raw_data, categories_raw_data):
    apps_meta = {}
    apps_meta['apps'] = OrderedDict()
    apps_meta['categories'] = categories_raw_data
    print("Fetch app data...")
    for app_name in sorted(apps_raw_data.keys()):
        print("  - {}".format(app_name))
        app_data = fetch_app_data(apps_raw_data[app_name], app_name)
        app_data['name'] = app_name
        app_data['subpage'] = os.path.join(html_subfolder_name,
                              get_html_app_fname(app_name))
        apps_meta['apps'][app_name] = app_data

    return apps_meta


if __name__ == "__main__":
    pwd = os.path.split(os.path.abspath(__file__))[0]
    outdir_abs = os.path.join(pwd, out_folder)
    static_abs = os.path.join(pwd, static_folder)

    # Create output folder, copy static files
    if os.path.exists(outdir_abs):
        shutil.rmtree(outdir_abs)
    os.mkdir(outdir_abs)
    shutil.copytree(static_abs, os.path.join(outdir_abs, static_folder))

    env = Environment(
        loader=PackageLoader('mod'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    singlepage_template = env.get_template("singlepage.html")
    main_index_template = env.get_template("main_index.html")

    # Get apps.json raw data
    with open(os.path.join(pwd, os.pardir, apps_file)) as f:
        apps_raw_data = json.load(f)

    # Get categories.json raw data
    with open(os.path.join(pwd, os.pardir, categories_file)) as f:
        categories_raw_data = json.load(f)

    apps_meta = generate_apps_meta(apps_raw_data, categories_raw_data)

    html_subfolder_abs = os.path.join(outdir_abs, html_subfolder_name)
    os.mkdir(html_subfolder_abs)

    # Make single-entry page based on singlepage.html
    print("[apps]")
    for app_name, app_data in apps_meta['apps'].items():
        subpage_name = app_data['subpage']
        subpage_abspath = os.path.join(outdir_abs, subpage_name)

        app_html = singlepage_template.render(category_map=apps_meta['categories'], **app_data)
        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(app_html)
        print("  - {} generated.".format(subpage_name))

    # Make index page based on main_index.html
    print("[main index]")
    rendered = main_index_template.render(**apps_meta)
    outfile = os.path.join(outdir_abs, 'index.html')
    with codecs.open(outfile, 'w', 'utf-8') as f:
        f.write(rendered)
    print("  - index.html generated")

    # Save json data for the app manager
    outfile = os.path.join(outdir_abs, apps_meta_file)
    with codecs.open(outfile, 'w', 'utf-8') as f:
        json.dump(apps_meta, f, ensure_ascii=False, indent=2)
    print("  - apps_meta.json generated")

    # Copy schemas
    print("[schemas/v1]")
    schemas_outdir = Path(outdir_abs).joinpath('schemas/v1')
    schemas_outdir.mkdir(parents=True)
    for schemafile in Path(pwd).glob('../schemas/*.schema.json'):
        print(f"  - {schemafile.name}")
        shutil.copyfile(schemafile, schemas_outdir.joinpath(schemafile.name))
