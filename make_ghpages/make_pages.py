# -*- coding: utf-8 -*-

import codecs
import json
import os
import shutil
import sys
import string
from collections import OrderedDict, defaultdict
from urllib.parse import urlparse
from urllib.request import urlopen

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

### END configuration


def get_html_app_fname(app_name):
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = "".join(c for c in app_name if c in valid_characters)

    return "{}.html".format(simple_string)


def get_hosted_on(url):
    try:
        netloc = urlparse(url).netloc
    except Exception as e:
        print(e)
        return None

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

    return netloc


def get_meta_info(json_url):
    try:
        response = urlopen(json_url)
        json_txt = response.read()
    except Exception:
        import traceback
        print("  >> UNABLE TO RETRIEVE THE JSON URL: {}".format(json_url))
        print(traceback.print_exc(file=sys.stdout))
        return None
    try:
        json_data = json.loads(json_txt)
    except ValueError:
        print("  >> WARNING! Unable to parse JSON")
        return None

    return json_data

def get_git_branches(git_url):
    from dulwich.client import get_transport_and_path_from_url
    t, p = get_transport_and_path_from_url(git_url)
    branches = t.get_refs(p)
    res = {}
    for key, value in branches.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res

def validate_meta_info(app_name, meta_info):
    if 'state' not in meta_info:
        meta_info['state'] = 'registered'

    if 'title' not in meta_info:
        meta_info['title'] = app_name

    return meta_info


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


    with open(os.path.join(pwd, os.pardir, apps_file)) as f:
        apps_raw_data = json.load(f)

    with open(os.path.join(pwd, os.pardir, categories_file)) as f:
        categories_raw_data = json.load(f)

    all_data = {}
    all_data['apps'] = OrderedDict()
    all_data['categories'] = categories_raw_data

    html_subfolder_abs = os.path.join(outdir_abs, html_subfolder_name)
    os.mkdir(html_subfolder_abs)

    summaries = defaultdict(list)
    other_summary = []
    other_summary_names = set()

    print("[apps]")
    for app_name in sorted(apps_raw_data.keys()):
        print("  - {}".format(app_name))
        app_data = apps_raw_data[app_name]
        app_data['name'] = app_name

        html_app_fname = get_html_app_fname(app_name)
        subpage_name = os.path.join(html_subfolder_name,
                                    get_html_app_fname(app_name))
        subpage_abspath = os.path.join(outdir_abs, subpage_name)
        hosted_on = get_hosted_on(app_data['git_url'])

        # Get metadata.json from the project;
        # set to None if not retrievable
        try:
            meta_url = app_data['meta_url']
        except KeyError:
            print("  >> WARNING: Missing meta_url!!!")
            meta_info = None
        else:
            meta_info = get_meta_info(meta_url)

        app_data['metainfo'] = validate_meta_info(app_name, meta_info)
        app_data['gitinfo'] = get_git_branches(app_data['git_url'])
        app_data['subpage'] = subpage_name
        app_data['hosted_on'] = hosted_on

        all_data['apps'][app_name] = app_data

        app_html = singlepage_template.render(category_map=categories_raw_data, **app_data)

        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(app_html)
        print("    - Page {} generated.".format(subpage_name))

    print("[main index]")
    rendered = main_index_template.render(**all_data)
    outfile = os.path.join(outdir_abs, 'index.html')
    with codecs.open(outfile, 'w', 'utf-8') as f:
        f.write(rendered)
    print("  - index.html generated")

    # save json data for the app manager
    outfile = os.path.join(outdir_abs, apps_meta_file)
    with codecs.open(outfile, 'w', 'utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("  - apps_meta.json generated")
