from __future__ import annotations

from . import io
from . import llm
from . import vis

import os

try:
    from importlib.metadata import PackageNotFoundError, version as _pkg_version
except Exception:  # pragma: no cover
    PackageNotFoundError = Exception  # type: ignore[assignment]
    _pkg_version = None  # type: ignore[assignment]

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


def _read_version_from_pyproject() -> str | None:
    if tomllib is None:
        return None

    root_dir = os.path.dirname(os.path.dirname(__file__))
    pyproject_path = os.path.join(root_dir, "pyproject.toml")
    if not os.path.isfile(pyproject_path):
        return None

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        project = data.get("project")
        if isinstance(project, dict):
            version = project.get("version")
            if isinstance(version, str) and version.strip():
                return version.strip()
    except Exception:
        return None

    return None


def get_version(dist_name: str = "geosirr") -> str:
    if _pkg_version is not None:
        try:
            return _pkg_version(dist_name)
        except PackageNotFoundError:
            pass
        except Exception:
            pass

    return _read_version_from_pyproject() or "0.0.0"


__version__ = get_version()
