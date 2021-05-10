# -*- coding: utf-8 -*-
import os
import re
from dataclasses import dataclass
from dataclasses import replace
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from repo2env import Environment
from repo2env import fetch_from_url
from repo2env.git_util import GitRepo


@dataclass
class Release:
    environment: Environment
    url: str


RELEASE_LINE_PATTERN = r"^(?P<rev>[^:]*?)(:(?P<rev_selection>[^:]+?))?$"


def _this_or_only_subdir(path):
    members = list(path.iterdir())
    return members[0] if len(members) == 1 and members[0].is_dir() else path


def _get_release_commits(repo, release_line):
    match = re.match(RELEASE_LINE_PATTERN, release_line)
    if not match:
        raise ValueError(f"Invalid release line specification: {release_line}")
    rev = match.groupdict()["rev"]

    if match.groupdict()["rev_selection"]:
        selected_commits = repo.rev_list(match.groupdict()["rev_selection"])
    else:
        selected_commits = None

    def selected(commit):
        return selected_commits is None or commit in selected_commits

    try:
        for tag in repo.get_merged_tags(rev):
            commit = repo.get_commit_for_tag(tag)
            if selected(commit):
                yield tag, commit
    except ValueError:
        if f"refs/tags/{rev}".encode() in repo.refs:
            commit = repo.get_commit_for_tag(rev)
            if selected(commit):
                yield rev, commit
        else:  # rev must be committish (commit)
            if selected(rev):
                yield rev, rev


def _gather_releases(release_specs, scan_environment):
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

        with fetch_from_url(url) as repo_path:
            if parsed_url.scheme.startswith("git+"):
                repo = GitRepo(os.fspath(repo_path))
                release_line = urlsplit(url).fragment or repo.get_current_branch()
                for ref, sha in _get_release_commits(repo, release_line):
                    # Replace release url path to point to specific commit.
                    path = f"{parsed_url.path.rsplit('@', 1)[0]}@{sha}"
                    # Parse environment from local copy of repository.
                    environment = scan_environment(
                        f"git+file:{os.fspath(repo_path.resolve())}@{sha}"
                    )
                    release = Release(
                        url=urlunsplit(parsed_url._replace(path=path)),
                        environment=environment,
                    )
                    yield _set_overrides(ref, release)
            else:
                release = Release(
                    url=url,
                    environment=scan_environment(
                        f"file:{os.fspath(repo_path.resolve())}"
                    ),
                )
                yield _set_overrides(None, release)


def gather_releases(app_data, scan_environment):
    for version, release in _gather_releases(
        app_data.get("releases", []), scan_environment
    ):
        if version is None:
            raise ValueError(f"Unable to determine version for: {release}")
        yield version, release
