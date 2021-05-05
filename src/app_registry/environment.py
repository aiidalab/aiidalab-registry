# -*- coding: utf-8 -*-
"""App environment specification

The specification is used to describe a reproducible environment for a
specific app, similar to the Reproducible Environment Specification (REES) [1]

[1] https://repo2docker.readthedocs.io/en/latest/specification.html

The following configuration files are recognized:

.. glossary::

    requirements.txt
        Describes a list of pip-installable packages that must be present in
        the Python environment that is used to execute the app.

    jupyter-requirements.txt
        Describes a list of pip-installable packages that must be present in
        the Python environment that is used to run Jupyter.
"""
from typing import List
from dataclasses import dataclass
from dataclasses import field


__all__ = [
    "Environment",
]


@dataclass
class Environment:
    """App environment specification.

    This dataclass contains the specification of an app environment and can be
    used to scan an existing environment configuration from a given path and to
    detect whether a given environment is meeting the specification.
    """

    jupyter_requirements: List[str] = field(default_factory=list)
    python_requirements: List[str] = field(default_factory=list)

    _FILES = (
        "jupyter-requirements.txt",
        "requirements.txt",
    )

    @staticmethod
    def _scan(path):
        def _parse_reqs(requirements):
            for line in requirements:
                if not line.strip().startswith("#"):
                    yield line.strip()

        try:
            yield "python_requirements", list(
                _parse_reqs(path.joinpath("requirements.txt").read_text().splitlines())
            )
        except FileNotFoundError:
            pass
        try:
            yield "jupyter_requirements", list(
                _parse_reqs(
                    path.joinpath("requirements-jupyter.txt").read_text().splitlines()
                )
            )
        except FileNotFoundError:
            pass

    @classmethod
    def scan(cls, root):
        """Scan the root path and determine the environment specification."""
        return cls(**dict(cls._scan(root)))
