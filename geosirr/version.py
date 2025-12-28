"""GeoSIRR version utilities.

We keep a stable public version (e.g. 1.0) and optionally append a *local*
build identifier using PEP 440 local version metadata:

    1.0+<build>

This is ideal for distinguishing CI/builds without changing the release
version.
"""

from __future__ import annotations

import os
import re

BASE_VERSION = "1.0"


def _normalize_local_version(local: str) -> str:
    """Normalize a local build identifier to be PEP 440-compatible.

    PEP 440 local version labels are restricted to ASCII letters/digits and
    the separators '.', '-', '_'. We coerce any other character to '.' and
    normalize '_' to '.'.
    """

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", ".", local).strip(".")
    cleaned = cleaned.replace("_", ".")
    return cleaned or "local"


def get_build() -> str | None:
    """Return the build identifier (if any).

    Supported environment variables:
    - GEOSIRR_BUILD: preferred, explicit build id
    - GITHUB_RUN_NUMBER: common in GitHub Actions
    - CI_PIPELINE_IID / CI_PIPELINE_ID: common in GitLab CI
    """

    build = (
        os.getenv("GEOSIRR_BUILD")
        or os.getenv("GITHUB_RUN_NUMBER")
        or os.getenv("CI_PIPELINE_IID")
        or os.getenv("CI_PIPELINE_ID")
    )
    if build:
        build = build.strip()
    return build or None


def get_version(base: str = BASE_VERSION) -> str:
    build = get_build()
    if not build:
        return base
    return f"{base}+{_normalize_local_version(build)}"


build = get_build()
version = get_version()
