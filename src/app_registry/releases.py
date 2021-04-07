# -*- coding: utf-8 -*-
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import run
from urllib.parse import urldefrag
from urllib.parse import urlsplit

from dulwich.repo import Repo
from packaging.specifiers import InvalidSpecifier
from packaging.specifiers import SpecifierSet


def _get_current_branch(repo):
    branch = run(
        ["git", "branch", "--show-current"],
        cwd=Path(repo.path),
        check=True,
        capture_output=True,
        encoding="utf-8",
    ).stdout
    if not branch:
        raise RuntimeError(
            "Unable to determine current branch name, likely in detached HEAD state."
        )
    return branch.strip()


def _get_releases_for_channel(repo, channel):
    branch_ref = f"refs/remotes/origin/{channel}"
    if branch_ref.encode() in repo.refs:  # channel is branch
        yield from run(
            ["git", "tag", "--merged", branch_ref],
            cwd=repo.path,
            check=True,
            capture_output=True,
            encoding="utf-8",
        ).stdout.splitlines()
    else:  # channel must be committish (tag or sha)
        yield channel


def _read_file(repo_path, version, file_path):
    try:
        return run(
            ["git", "show", f"{version}:{file_path}"],
            cwd=Path(repo_path),
            check=True,
            capture_output=True,
            encoding="utf-8",
        ).stdout
    except CalledProcessError as error:
        if re.match(
            f"fatal: Path '{re.escape(file_path)}' does not exist", error.stderr
        ):
            return None  # file does not exist for that version
        elif re.match("fatal: Invalid object name", error.stderr):
            raise ValueError(f"Unknown version: {version}")
        else:
            raise  # unexpected error


def _parse_dependencies(repo_path, version):
    requirements_txt = _read_file(repo_path, version, "requirements.txt")
    if requirements_txt is not None:
        yield "python-requirements", [
            line.strip()
            for line in requirements_txt.splitlines()
            if not line.strip().startswith("#")
        ]


def _fully_qualified_dependencies(dependencies):
    if isinstance(dependencies, list):
        yield "python-requirements", dependencies
    else:
        yield from dependencies.items()


class _RegexMatchSpecifierSet:
    """Interpret 'invalid' specifier sets as regular expression pattern."""

    def __init__(self, specifiers=""):
        self.specifiers = specifiers

    def __contains__(self, version):
        return re.match(self.specifiers, version) is not None


def _specifier_set(specifiers=""):
    try:
        return SpecifierSet(specifiers=specifiers, prereleases=True)
    except InvalidSpecifier:
        return _RegexMatchSpecifierSet(specifiers=specifiers)


def _find_matching_dependencies(requires, version):
    matches = [spec for spec in requires if version in _specifier_set(spec)]
    if len(matches) > 1:
        raise ValueError(
            f"The explicit dependency specification for version '{version}' is ambiguous; "
            f"multiple matching specifiers: {matches}"
        )
    elif len(matches) == 1:
        yield from _fully_qualified_dependencies(requires[matches[0]])


@contextmanager
def _clone_repo(git_url):
    with tempfile.TemporaryDirectory() as tmp_dir:
        run(
            ["git", "clone", urldefrag(git_url).url, tmp_dir],
            cwd=Path(tmp_dir).parent,
            check=True,
            capture_output=True,
        )
        yield Repo(tmp_dir)


def find_releases_and_dependencies(app_metadata):
    git_url = app_metadata["git_url"]
    requires = app_metadata["metadata"].get("requires", {})

    with _clone_repo(git_url) as repo:
        channel = urlsplit(git_url).fragment or _get_current_branch(repo)
        releases = list(_get_releases_for_channel(repo, channel))

        parsed_dependencies = {
            release: dict(_parse_dependencies(repo.path, release))
            for release in releases
        }

        explicit_dependencies = {
            release: dict(_find_matching_dependencies(requires, release))
            for release in releases
        }

    for release in releases:
        # For each release, return the explicit dependencies or
        # the parsed dependencies with preference for the former.
        yield release, explicit_dependencies[release] or parsed_dependencies[release]
