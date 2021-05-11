# AiiDAlab Application Registry

This repository contains the **source code** of the official App registry for the [AiiDAlab](https://www.materialscloud.org/aiidalab).

<p align="center">
 <a href="http://aiidalab.github.io/aiidalab-registry" rel="Go to AiiDAlab app registry">
  <img src="make_ghpages/static/gotobutton.svg">
 </a>
</p>

## Adding an app to the registry

Apps are added to the registry by adding an entry to the `apps.yaml` file within this repository.

*Feel free to propose a new app category to be added to [`category.yaml`](https://github.com/aiidalab/aiidalab-registry/edit/main/categories.yaml) before or after adding your app.*

1. Create a pull request to this repository that adds a new entry to the `apps.yaml` file, e.g., by [editing the file directly in the browser](https://github.com/aiidalab/aiidalab-registry/edit/main/apps.yaml?message=Add%20app%20%3Capp-name%3E). Example:

    ```yaml
    hello-world:
      metadata:
        title: AiiDAlab hello world app
        description: |
            The hello world app demonstrates how to develop and
            register an app for AiiDAlab.
        authors: A. Doe, B. Doe
        external_url: https://github.com/aiidalab/aiidalab-hello-world
        documentation_url: https://github.com/aiidalab/aiidalab-hello-world#readme
        state: stable
      logo: https://raw.githubusercontent.com/aiidalab/aiidalab-widgets-base/master/miscellaneous/logos/aiidalab.png
      categories:
        - tutorials
      releases:
        - "git+https://github.com/aiidalab/aiidalab-hello-world.git@:"
    ```

    **Note**: Only the metadata fields `title` and `description` are mandatory.

2. Your app will show up in the [AiiDAlab App Store](http://aiidalab.github.io/aiidalab-registry) once your pull request is approved and merged.

**Tip**: The app store supports the `$ref` syntax to reference externally hosted documents.
That means you can reference metadata that is hosted at a different location, which makes it easier to dynamically update it.
For example, if you place a `metadata.yaml` file within your app repository, then you can reference that file in the app store like this:

```yaml
hello-world:
  metadata:
    $ref: https://raw.githubusercontent.com/aiidalab/aiidalab-hello-world/master/metadata.yaml
```
You can even reference only parts of the metadata, example:
```yaml
hello-world:
  metadata:
    title: AiiDAlab hello world app
    description:
      $ref: https://raw.githubusercontent.com/aiidalab/aiidalab-hello-world/master/metadata.yaml#description
```

*The app store will assume that external references are in JSON format unless the referenced path ends with `.yaml` or `.yml`.*

### Valid keys for app entries in `apps.yaml`

| Key | Requirement | Description |
|:---:|:---:|:---|
| `metadata` | **Mandatory** | General description of the app (see below). |
| `releases` | **Mandatory** | List the source(s) for releases, e.g., a git repository. |
| `categories` | Optional | If provided, must be one of the valid categories specified in [`categories.yaml`](https://github.com/aiidalab/aiidalab-registry/blob/main/categories.yaml). |

### Valid keys for app metadata:

| Key | Requirement | Description |
|:---:|:---:|:---|
| `title` | **Mandatory** | The title will be displayed in the list of apps in the application manager. |
| `description` | **Mandatory** | The description will be displayed on the detail page of your app. |
| `authors` | Optional | Comma-separated list of authors. |
| `state` | Optional | One of<br>- `registered`: lowest level - app may not yet be in a working state. Use this to secure a specific name.<br>- `development`: app is under active development, expect the occasional bug.<br>- `stable`: app can be used in production. |
| `documentation_url` | Optional | The link to the online documentation of the app (e.g. on [Read The Docs](https://readthedocs.org/)). |
| `external_url` | Optional | General homepage for your app. |

#### Release specification

Releases are specified in the form of a list, where each list entry corresponds to one or more tagged commits of a git repository branch.
In case that it corresponds to multiple commits, the release entry is called a *release line*.

This is how we can specify a release pointing to a specific version:
```yaml
hello-world:
  releases:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@v1.0.0
```
The value behind the `@` symbol must in this case point to a specific tag.
Note that the above example is short-hand for:
```yaml
hello-world:
  releases:
  - url: git+https://github.com/aiidalab/aiidalab-hello-world.git@v1.0.0
```
Specifying a release entry as dictionary allows us to override the environment specification (see next section) as well as the version name.

On the other hand, if we want to add all tagged commits on a specific branch to the release line, we point to the branch name followed by a colon (`:`):
```yaml
hello-world:
  releases:
  - "git+https://github.com/aiidalab/aiidalab-hello-world.git@master:"
```
Typically, most app developers would want to take that approach since it avoids the need to update the registry with each new release: simply push a new tagged commit and the version will be released on AiiDAlab.
If the branch name is omitted, it will fall back to the default branch name, e.g. if 'master' is the default branch, `@:` is equivalent to `@master:`.

You can use the standard [git revision selection syntax](https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection) to further reduce the selected commits on a release line.
For example, `@master:v1.0.0..` means "select all tagged commits on the master branch after v1.0.0".

Here a few more examples, demonstrating all potential release specifications:

```yaml
hello-world:
  releases:
  # All tagged commits on the repository's default branch:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@:
  # All tagged commits on the repository's develop branch:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@develop:
  # Specifically the commit tagged with `v1.0.0`:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@v1.0.0
  # All tagged commits on the `master` branch from `v0.1.0` (exclusive) onwards:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@master:v0.1.0..
  # All tagged commits on the `master` branch from `v0.1.0` (inclusive) onwards:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@master:v0.1.0^..
  # All tagged commits on the `master` branch from `v0.1.0` (exclusive) until `v1.0.0`:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@master:v0.1.0..v1.0.0

  # The following approaches are *not recommended*, but shown here for completeness:
  # The latest commit on the repository's default branch
  - git+https://github.com/aiidalab/aiidalab-hello-world.git
  # The latest commit on the repository's develop branch:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@develop
```

#### Environment specification

The environment specification is typically directly parsed from the app repository, similar to how [repo2docker](https://repo2docker.readthedocs.io) parses repositories to derive instructions to create a docker image.
This app store uses the repo2env tool to automatically parse the environment specification for a specific app release.

In the current version, the following files are parsed:

 - `setup.cfg` - The Python requirements listed in that file must be installed within the Python kernel executing the app.
 - `requirements.txt` (only if setup.cfg does not specify requirements) - The Python requirements listed in that file must be installed within the Python kernel executing the app.

The above listed files are parsed either from a hidden sub-directory called `.aiidalab/` or the repository root directory in that order.
This means for the purpose of the AiiDAlab environment specification, a file `.aiidalab/requirements.txt` would be preferentially parsed over the `./requirements.txt`.
If a `.aiidalab` directory exists, only files within that directory are parsed.

We recommend that app developers test the specification on their app before a release.
Simply install and then run `repo2env` on a local repository to see the environment specification:
```
repo2env /path/to/app/repo
```
See the [repo2env documentation](https://github.com/aiidalab/repo2env#readme) for details.

To override the environment specification for one or more versions, simply add an explicit specification to the release.
For example, to override the environment specification for version v1.0.0:
```yaml
hello-world:
  releases:
  # The tagged commits on the default branch will use the parsed environment specification:
  - git+https://github.com/aiidalab/aiidalab-hello-world.git@:
  # The environment specification for version v1.0.0 is overriden:
  - url: git+https://github.com/aiidalab/aiidalab-hello-world.git@v1.0.0
    environment:
      python-requirements:
        - aiidalab>=20.02.0b2
        - some-missing-requirement
```

This is useful to retoractively override environment specifications if the in-repository specification via the requirements-files is incorrect or incomplete.

Tip: For individual releases, the same approach can also be used to override the version number, in case that it should deviate from the tag name.
Example:
```yaml
hello-world:
  releases:
  - url: git+https://github.com/aiidalab/aiidalab-hello-world.git@v1.0.0
    version: 1.0.0
```  

## Information for maintainers

To prepare a development environment, please run the following steps:
```console
$ pip install -r src/requirements.txt -r tests/requirements.txt
$ pre-commit install
```

This will install all requirements needed to run the git pre-commit hooks (linters), build the website locally, and execute the test framework.

To execute tests, run:
```console
$ PYTHONPATH=src pytest
```

Executed tests include unit, integration, and validation tests.
The validation tests check the validity of all schema files, the data files (e.g. `apps.yaml` and `categories.yaml`, and – if present – the configuration file (`config.yaml`).

To generate the website, simply execute the following script:

```console
$ python src/build.py
```

The continuous-integration workflow is implemented with GitHub actions, which runs the pre-commit hooks, unit, integration, and validation tests.
In addition, all commits on the `main` branch are automatically deployed to GitHub pages.

### Versioning and migrations

* The public registry API specification is maintained under `src/static/api/openapi-v{version}.yaml`.
* The public registry API is published at `api/v{version}/` and is considered user-facing.
* The versioning of the API is semantic and all versions within one major version are backwards-compatible.
* The schemas for JSON files and responses are maintained within the repository at `src/static/schemas/v{version}/` and the tree version number should correspond to the API with the same major version number.
* The schemas are considered implementation detail, but updates must still be made with care as the public API relies on some of the schemas.
* Should the number of apps maintained within this registry grow substantially, a re-implementation of the registry as a database application with RESTful API server should be considered. Such a re-implementation would likely require a migration to a new server (see next point).
* For a migration to a different server both the old and the new registry should be kept online concurrently during a reasonable transition phase.

## Acknowledgements

This work is supported by the [MARVEL National Centre for Competency in Research](<http://nccr-marvel.ch>)
funded by the [Swiss National Science Foundation](<http://www.snf.ch/en>), as well as by the [MaX
European Centre of Excellence](<http://www.max-centre.eu/>) funded by the Horizon 2020 EINFRA-5 program,
Grant No. 676598.

![MARVEL](make_ghpages/static/img/MARVEL.png)
![MaX](make_ghpages/static/img/MaX.png)
