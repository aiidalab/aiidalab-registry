# Materials Cloud App Registry

This is the App registry for Materials Cloud Apps for [jupyter.materialscloud.org](jupyter.materialscloud.org)

## Adding your app

Just make a pull request that adds your app to the `apps.json` file. Example:

```
    "aiida-tutorials": {
        "git_url": "https://github.com/aiidateam/aiida_demos.git",
        "meta_url": "https://raw.githubusercontent.com/aiidateam/aiida_demos/master/metadata.json",
        "label": "AiiDA Tutorials"
    }
```

Your app will show up in the [App Manager](https://github.com/materialscloud-org/mc-home/blob/master/appmanager.ipynb) as soon as your pull request is merged.
