# -*- coding: utf-8 -*-
"""Core data classes for the app registry."""
from dataclasses import dataclass
from dataclasses import fields

import jsonschema

from .util import load_json


@dataclass
class AppRegistrySchemas:
    """The app registry JSON-schema objects."""

    apps: dict
    apps_meta: dict
    categories: dict
    metadata: dict

    @classmethod
    def from_path(cls, path):
        return cls(
            **{
                field.name: load_json(path.joinpath(f"{field.name}.schema.json"))
                for field in fields(cls)
            }
        )


@dataclass
class AppRegistryData:
    """The app registry data objects (apps and categories)."""

    apps: dict
    categories: dict

    def validate(self, schemas: AppRegistrySchemas):
        """Validate the registry data against the provided registry schemas."""
        jsonschema.validate(instance=self.apps, schema=schemas.apps)
        jsonschema.validate(instance=self.categories, schema=schemas.categories)
