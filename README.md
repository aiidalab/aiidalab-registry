# Materials Cloud App Registry

This is the App registry for Materials Cloud Apps for [aiidalab.materialscloud.org](aiidalab.materialscloud.org)

## Adding your app

Just make a pull request that adds your app to the `apps.json` file. Example:

```
    "aiida-tutorials": {
        "git_url": "https://github.com/aiidateam/aiida_demos.git",
        "meta_url": "https://raw.githubusercontent.com/aiidateam/aiida_demos/master/metadata.json",
        "label": "AiiDA Tutorials"
    }
```

Your app will show up in the [App Manager](https://github.com/aiidalab/aiidalab-home/blob/master/appmanager.ipynb) as soon as your pull request is merged.

## Acknowledgements

This work is supported by the [MARVEL National Centre for Competency in Research](<http://nccr-marvel.ch>)
funded by the [Swiss National Science Foundation](<http://www.snf.ch/en>), as well as by the [MaX
European Centre of Excellence](<http://www.max-centre.eu/>) funded by the Horizon 2020 EINFRA-5 program,
Grant No. 676598.

![MARVEL](miscellaneous/logos/MARVEL.png)
![MaX](miscellaneous/logos/MaX.png)
