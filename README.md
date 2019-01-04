# AiiDA Lab Application Registry

This repository contains the **source code** of the official App registry for the [AiiDA Lab](aiidalab.materialscloud.org).

<p align="center">
 <a href="http://aiidateam.github.io/aiida-registry" rel="Go to AiiDA Lab app registry">
  <img src="make_ghpages/static/gotobutton.svg">
 </a>
 </p>

## Adding your app

 1. Add a `meta.json` file to your app repository. Example:

    ```
        {
            "title": "label": "AiiDA Tutorials",
            "description": "Learn how to use AiiDA using jupyter notebooks on the AiiDA lab.",
            "authors": "L. Talirz",
            "logo": "folder/logo.png",
            "state": "development"
        }
    ```

    Note: The fields `title` and `description` are mandatory.


 1. Make a pull request that adds your app to the `apps.json` file. Example:

    ```
        "aiida-tutorials": {
            "git_url": "https://github.com/aiidateam/aiida_demos.git",
            "meta_url": "https://raw.githubusercontent.com/aiidateam/aiida_demos/master/metadata.json",
        }
    ```

Your app will show up in the [App Manager](https://github.com/aiidalab/aiidalab-home/blob/master/appmanager.ipynb) once your pull request is merged.


### Valid keys for `meta.json`

#### title
The title will be displayed in the list of apps in the application manager.

#### description
The description will be displayed on the detail page of your app.

#### authors
Comma-separated list of authors.

#### logo
Relative path to a logo (png or jpg) within your repository.

#### state
One of
* `registered`: lowest level - app may not yet be in a working state.
  Use this to secure a specific name.
* `development`: app is under active development, expect the occasional bug.
* `stable`: app can be used in production.

#### documentation_url
The link to the online documentation of the app (e.g. on [Read The Docs](https://readthedocs.org/)).


## Acknowledgements

This work is supported by the [MARVEL National Centre for Competency in Research](<http://nccr-marvel.ch>)
funded by the [Swiss National Science Foundation](<http://www.snf.ch/en>), as well as by the [MaX
European Centre of Excellence](<http://www.max-centre.eu/>) funded by the Horizon 2020 EINFRA-5 program,
Grant No. 676598.

![MARVEL](make_ghpages/static/img/MARVEL.png)
![MaX](make_ghpages/static/img/MaX.png)
