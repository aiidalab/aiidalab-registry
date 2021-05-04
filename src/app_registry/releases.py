# -*- coding: utf-8 -*-
import re
import tarfile
import tempfile
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from urllib.parse import urldefrag
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import requests
from packaging.specifiers import InvalidSpecifier
from packaging.specifiers import SpecifierSet

from .environment import Environment
from .git_util import GitPath
from .git_util import GitRepo


@dataclass
class Release:
    environment: Environment
    url: str


RELEASE_LINE_PATTERN = r"^(?P<ref>[^:]*?)(:(?P<rev_selection>[^:]+?))?$"


def _this_or_only_subdir(path):
    members = list(path.iterdir())
    return members[0] if len(members) == 1 and members[0].is_dir() else path


def _get_release_commits(repo, release_line):
    match = re.match(RELEASE_LINE_PATTERN, release_line)
    if not match:
        raise ValueError(f"Invalid release line specification: {release_line}")
    ref = match.groupdict()["ref"]

    if match.groupdict()["rev_selection"]:
        selected_commits = repo.rev_list(match.groupdict()["rev_selection"])
    else:
        selected_commits = None

    def selected(commit):
        return selected_commits is None or commit in selected_commits

    try:
        for tag in repo.get_merged_tags(ref):
            commit = repo.get_commit_for_tag(tag)
            if selected(commit):
                yield tag, commit
    except ValueError:
        if f"refs/tags/{ref}".encode() in repo.refs:
            commit = repo.get_commit_for_tag(ref)
            if selected(commit):
                yield ref, commit
        else:  # ref must be committish (commit)
            if selected(ref):
                yield ref, ref


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


def _release_from_path(path, environment_dirs):
    for env_path in (path.joinpath(env_dir) for env_dir in environment_dirs):
        if env_path.is_dir():
            return Release(
                url=f"file://{path.resolve()}",
                environment=Environment.scan(env_path),
            )
    raise RuntimeError(f"Unable to determine release from path: {path}")


def _release_from_file(path):
    if path.is_dir():
        return _release_from_path(path)
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with tarfile.open(path) as tar_file:
                tar_file.extractall(path=tmp_dir)
                path_ = _this_or_only_subdir(Path(tmp_dir))
                return None, replace(
                    _release_from_path(path_), url=f"file://{path.resolve()}"
                )


def _gather_releases_from_git(git_url, env_dirs):
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo = GitRepo.clone_from_url(git_url, tmp_dir)
        release_line = urlsplit(git_url).fragment or repo.get_current_branch()
        commits = list(_get_release_commits(repo, release_line))
        for ref, sha in commits:
            path = GitPath(Path(repo.path), sha)
            yield ref, replace(
                _release_from_path(path, env_dirs),
                url=f"{urldefrag(git_url).url}#{sha}",
            )


def _gather_releases_from_git_https_url(git_url):
    git_url = urlunsplit(urlsplit(git_url)._replace(schema="https"))
    yield from _gather_releases_from_git_https_url(git_url)


def _release_from_https(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    content = response.content

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()
        return replace(_release_from_file(Path(tmp_file.name)), url=url)


def _gather_releases(release_specs, env_dirs):
    for release_spec in release_specs:
        if isinstance(release_spec, str):
            url = release_spec
            environment_override = None
            version_override = None
        else:
            url = release_spec["url"]
            environment_override = release_spec.get("environment")
            version_override = release_spec.get("version")

        def _set_overrides(version, release):
            return version_override or version, replace(
                release, environment=environment_override or release.environment
            )

        # The way that an app is retrieved is determined by the scheme of the
        # release url.  For example, "git+https://example.com/my-app.git" means
        # that the app is located at a remote git repository from which it can
        # be downloaded (cloned) via https.
        parsed_url = urlsplit(url)

        # The app is provided at a path on the local file system either as a
        # directory or as a tar-ball.
        if parsed_url.scheme in ("", "file"):
            yield _set_overrides(*_release_from_file(Path(parsed_url.path)))

        # The app is provided as a tar-ball at a remote location from which it
        # can be downloaded via https.
        elif parsed_url.scheme == "https":
            yield _set_overrides(*_release_from_https(url))

        # The app is provided as a git-repository on the local file system.
        elif parsed_url.scheme == "git+file":
            git_url = urlunsplit(parsed_url._replace(scheme=""))
            for version, release in _gather_releases_from_git(git_url, env_dirs):
                yield _set_overrides(
                    version, replace(release, url=f"git+file://{release.url}")
                )

        # The app is provided as a git-repository at a remote location from
        # which it can be downloaded (cloned) via https.
        elif parsed_url.scheme == "git+https":
            git_url = urlunsplit(parsed_url._replace(scheme="https"))
            for version, release in _gather_releases_from_git(git_url, env_dirs):
                yield _set_overrides(
                    version, replace(release, url=f"git+{release.url}")
                )

        else:
            raise ValueError(f"Unsupported url scheme: {parsed_url.scheme} ({url})")


def gather_releases(app_data, env_dirs):
    for version, release in _gather_releases(app_data.get("releases", []), env_dirs):
        if version is None:
            raise ValueError(f"Unable to determine version for: {release}")
        yield version, release
