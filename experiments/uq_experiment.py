#!/usr/bin/env python3
"""Run and analyze repeated GeoSIRR generations from a Markdown description."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import statistics
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "gemma4:31b"
DEFAULT_BACKEND = "ollama"
DEFAULT_DESCRIPTION = ROOT / "experiments" / "listric_fault_baseline.md"
MODEL = DEFAULT_MODEL
BACKEND = DEFAULT_BACKEND
DESCRIPTION_PATH = DEFAULT_DESCRIPTION
OUTPUT_DIR = ROOT / "output" / "uq_listric_fault_baseline_gemma4_31b"
RUNS_DIR = OUTPUT_DIR / "runs"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
RUN_COUNT = 10
MAX_GEN_ITERATIONS = 5
MAX_CHATS = 1
BOUNDARY_TOLERANCE_KM = 1e-6
MEAN_LINE_SAMPLES = 101
CONTACT_DENSITY_SIGMA_KM = 0.10
UQ_FIGURE_NAME = "uq_geometry_variability.png"
VERTEX_MARKER_SIZE = 20.0
LEGEND_Y = -0.20

sys.path.insert(0, str(ROOT))

# Keep matplotlib headless and its cache with the ignored experiment artifacts.
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".matplotlib"))


def configure_experiment(
    model: str,
    backend: str,
    description: Path,
    output_dir: Path | None,
    vertex_size: float,
    legend_y: float,
) -> None:
    global MODEL, BACKEND, DESCRIPTION_PATH, OUTPUT_DIR, RUNS_DIR, VERTEX_MARKER_SIZE, LEGEND_Y
    if vertex_size <= 0:
        raise ValueError("vertex size must be positive")
    MODEL = model
    BACKEND = backend
    VERTEX_MARKER_SIZE = vertex_size
    LEGEND_Y = legend_y
    DESCRIPTION_PATH = description.resolve()
    model_slug = model.replace(":", "_").replace("/", "_")
    if output_dir is None:
        backend_suffix = "" if backend == DEFAULT_BACKEND else f"_{backend}"
        OUTPUT_DIR = ROOT / "output" / f"uq_{DESCRIPTION_PATH.stem}_{model_slug}{backend_suffix}"
    else:
        OUTPUT_DIR = output_dir if output_dir.is_absolute() else ROOT / output_dir
        OUTPUT_DIR = OUTPUT_DIR.resolve()
    RUNS_DIR = OUTPUT_DIR / "runs"
    os.environ["MPLCONFIGDIR"] = str(OUTPUT_DIR / ".matplotlib")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_value(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def filtered_model_metadata(tag: dict[str, Any], shown: dict[str, Any]) -> dict[str, Any]:
    details = shown.get("details") or tag.get("details") or {}
    allowed_details = (
        "format",
        "family",
        "families",
        "parameter_size",
        "quantization_level",
    )
    return {
        "name": MODEL,
        "digest": tag.get("digest"),
        "modified_at": tag.get("modified_at"),
        "details": {key: details.get(key) for key in allowed_details if details.get(key) is not None},
    }


def probe_ollama_host(host: str, host_type: str) -> dict[str, Any] | None:
    import requests

    try:
        response = requests.get(f"{host}/api/tags", timeout=3)
        response.raise_for_status()
        tags = response.json().get("models", [])
    except (requests.RequestException, ValueError):
        return None

    tag = next(
        (item for item in tags if item.get("name") == MODEL or item.get("model") == MODEL),
        None,
    )
    if tag is None:
        return None

    try:
        shown_response = requests.post(f"{host}/api/show", json={"model": MODEL}, timeout=10)
        shown_response.raise_for_status()
        shown = shown_response.json()
    except (requests.RequestException, ValueError):
        shown = {}

    try:
        version_response = requests.get(f"{host}/api/version", timeout=3)
        version_response.raise_for_status()
        server_version = version_response.json().get("version")
    except (requests.RequestException, ValueError):
        server_version = None

    return {
        "host_type": host_type,
        "host": host,
        "server_version": server_version,
        "client_version": importlib.metadata.version("ollama"),
        "model": filtered_model_metadata(tag, shown),
    }


def select_ollama_host() -> dict[str, Any]:
    load_dotenv(ROOT / ".env")
    host = os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).strip().rstrip("/")
    hostname = urlparse(host).hostname
    host_type = "local" if hostname in {"localhost", "127.0.0.1", "::1"} else "configured"
    selected = probe_ollama_host(host, host_type)
    if selected is None:
        raise RuntimeError(
            f"Exact model {MODEL!r} is unavailable at the configured Ollama host {host}; "
            "check OLLAMA_HOST in .env. No model was pulled or substituted."
        )
    os.environ["OLLAMA_HOST"] = selected["host"]
    return selected


def select_model_provider() -> dict[str, Any]:
    load_dotenv(ROOT / ".env")
    if BACKEND == "ollama":
        selected = select_ollama_host()
        selected["backend"] = BACKEND
        return selected

    from geosirr.llm import load_openai_api_key

    load_openai_api_key()
    return {
        "backend": BACKEND,
        "client_version": importlib.metadata.version("openai"),
        "model": {"name": MODEL},
    }


def model_geometry(
    vertices: list[tuple[int, float, float]],
    polygons: list[tuple[str, list[int]]],
) -> tuple[list[list[float]], list[list[list[float]]]]:
    coordinates = {vertex_id: [x, z] for vertex_id, x, z in vertices}
    edge_counts: dict[tuple[int, int], int] = {}
    for _, vertex_ids in polygons:
        for start, end in zip(vertex_ids, vertex_ids[1:] + vertex_ids[:1]):
            edge = tuple(sorted((start, end)))
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    contacts = [
        [coordinates[start], coordinates[end]]
        for (start, end), count in edge_counts.items()
        if count == 2
    ]
    return [[x, z] for _, x, z in vertices], contacts


def boundary_signature(vertices: list[list[float]]) -> tuple[tuple[float, float], ...]:
    import numpy as np

    values = np.asarray(vertices, dtype=float)
    x_min = values[:, 0].min()
    x_max = values[:, 0].max()
    on_side = np.isclose(values[:, 0], x_min, atol=BOUNDARY_TOLERANCE_KM) | np.isclose(
        values[:, 0], x_max, atol=BOUNDARY_TOLERANCE_KM
    )
    return tuple(sorted((round(float(x), 6), round(float(z), 6)) for x, z in values[on_side]))


def boundary_check(
    records: list[dict[str, Any]],
) -> tuple[bool, tuple[tuple[float, float], ...], list[int]]:
    signatures = [(int(record["run"]), boundary_signature(record["model_vertices"])) for record in records]
    expected = Counter(signature for _, signature in signatures).most_common(1)[0][0]
    inconsistent_runs = [run for run, signature in signatures if signature != expected]
    return not inconsistent_runs, expected, inconsistent_runs


def interior_path(vertices: list[list[float]]) -> Any:
    import numpy as np

    values = np.asarray(vertices, dtype=float)
    x_min = values[:, 0].min()
    x_max = values[:, 0].max()
    on_side = np.isclose(values[:, 0], x_min, atol=BOUNDARY_TOLERANCE_KM) | np.isclose(
        values[:, 0], x_max, atol=BOUNDARY_TOLERANCE_KM
    )
    path = values[~on_side]
    return path[np.argsort(path[:, 1])[::-1]]


def mean_interior_path(records: list[dict[str, Any]]) -> tuple[Any | None, str | None]:
    import numpy as np

    paths = [interior_path(record["model_vertices"]) for record in records]
    if any(len(path) < 2 for path in paths):
        return None, "at least one run has fewer than two interior vertices"
    if any(np.any(np.diff(path[:, 1]) >= 0) for path in paths):
        return None, "at least one run has non-unique or non-monotonic interior-vertex depths"

    tops = [float(path[0, 1]) for path in paths]
    bottoms = [float(path[-1, 1]) for path in paths]
    if max(tops) - min(tops) > BOUNDARY_TOLERANCE_KM or max(bottoms) - min(bottoms) > BOUNDARY_TOLERANCE_KM:
        return None, "interior paths do not share common top and bottom depths"

    common_z = np.linspace(statistics.fmean(tops), statistics.fmean(bottoms), MEAN_LINE_SAMPLES)
    interpolated_x = []
    for path in paths:
        interpolated_x.append(np.interp(common_z[::-1], path[::-1, 1], path[::-1, 0])[::-1])
    return np.column_stack((np.mean(interpolated_x, axis=0), common_z)), None


def mean_interior_nodes(records: list[dict[str, Any]], mean_path: Any) -> Any:
    import numpy as np

    depths = np.unique(
        np.concatenate([interior_path(record["model_vertices"])[:, 1] for record in records])
    )[::-1]
    mean_x = np.interp(depths[::-1], mean_path[::-1, 1], mean_path[::-1, 0])[::-1]
    return np.column_stack((mean_x, depths))


def contact_density_grid(records: list[dict[str, Any]]) -> tuple[Any, Any, Any]:
    import numpy as np

    combined = np.vstack([np.asarray(record["model_vertices"], dtype=float) for record in records])
    x_min, x_max = combined[:, 0].min(), combined[:, 0].max()
    z_min, z_max = combined[:, 1].min(), combined[:, 1].max()
    x_span = max(float(x_max - x_min), 1.0)
    z_span = max(float(z_max - z_min), 1.0)
    nx = 1000
    nz = max(100, round(nx * z_span / x_span))
    x_edges = np.linspace(x_min, x_max, nx + 1)
    z_edges = np.linspace(z_min, z_max, nz + 1)
    x = (x_edges[:-1] + x_edges[1:]) / 2.0
    z = (z_edges[:-1] + z_edges[1:]) / 2.0
    grid_x, grid_z = np.meshgrid(x, z)
    density = np.zeros_like(grid_x)
    for record in records:
        minimum_distance = np.full_like(grid_x, np.inf)
        for start, end in record["internal_contacts"]:
            start_x, start_z = start
            end_x, end_z = end
            dx = end_x - start_x
            dz = end_z - start_z
            length_squared = dx * dx + dz * dz
            if length_squared == 0:
                continue
            projection = ((grid_x - start_x) * dx + (grid_z - start_z) * dz) / length_squared
            projection = np.clip(projection, 0.0, 1.0)
            nearest_x = start_x + projection * dx
            nearest_z = start_z + projection * dz
            minimum_distance = np.minimum(
                minimum_distance, np.hypot(grid_x - nearest_x, grid_z - nearest_z)
            )
        density += np.exp(-minimum_distance**2 / (2.0 * CONTACT_DENSITY_SIGMA_KM**2))
    return x_edges, z_edges, density / len(records)


def generation_attempts(chats: list[list[dict[str, Any]]]) -> int:
    # Each chat starts with system and user messages. A successful attempt adds one
    # assistant message; a failed attempt adds assistant output and user feedback.
    return sum(max(0, (len(chat) - 1) // 2) for chat in chats)


def final_failure_reason(chats: list[list[dict[str, Any]]]) -> str:
    for chat in reversed(chats):
        for message in reversed(chat):
            content = str(message.get("content", ""))
            if message.get("role") == "user" and content.startswith("The generated cross section is invalid."):
                lines = [line for line in content.splitlines()[1:] if line.strip()]
                return " | ".join(lines[:4])
    return f"maximum of {MAX_GEN_ITERATIONS} generation attempts exhausted"


def render_section(definition: str, filename: Path, title: str) -> None:
    import matplotlib.pyplot as plt
    import geosirr as gs

    fig, _ = gs.vis.plot_cross_section(
        definition=definition,
        filename=str(filename),
        title=title,
        vertex_label_color="gray",
    )
    plt.close(fig)


def run_generation(run_number: int, description: str, instruction_prompt: str) -> dict[str, Any]:
    import geosirr as gs

    run_dir = RUNS_DIR / f"run_{run_number:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    try:
        success, definition, full_prompt, chats = gs.llm.generate_section_text(
            instruction_prompt=instruction_prompt,
            text=description,
            image_files=None,
            llm_backend=BACKEND,
            llm_name=MODEL,
            llm_params=None,
            max_gen_iterations=MAX_GEN_ITERATIONS,
            max_chats=MAX_CHATS,
            only_prompt=False,
            section_preview=False,
            verbose=False,
        )
        elapsed = time.perf_counter() - started
        attempts = generation_attempts(chats)
        prompt_hash = hashlib.sha256(full_prompt.encode("utf-8")).hexdigest()
        prompt_path = OUTPUT_DIR / "full_prompt.md"
        if not prompt_path.exists():
            prompt_path.write_text(full_prompt, encoding="utf-8")

        record: dict[str, Any] = {
            "run": run_number,
            "generation_success": bool(success),
            "attempts": attempts,
            "generation_time_seconds": elapsed,
            "full_prompt_sha256": prompt_hash,
            "format_valid": None,
            "format_errors": [],
            "topology_valid": None,
            "topology_errors": [],
            "vertex_count": None,
            "polygon_count": None,
            "geosirr_valid": False,
            "model_vertices": None,
            "internal_contacts": None,
            "failure_reason": None,
        }

        if not success or not definition:
            record["failure_reason"] = final_failure_reason(chats)
            return record

        dsl_path = run_dir / "final_section.txt"
        dsl_path.write_text(definition, encoding="utf-8")
        format_valid, format_errors = gs.io.validate_cross_section_format(definition)
        try:
            topology_valid, topology_errors = gs.io.validate_cross_section_topology(definition)
        except Exception as exc:
            topology_valid = False
            topology_errors = [f"{type(exc).__name__}: {exc}"]
        vertices, polygons = gs.io.parse_text(definition)
        model_vertices, internal_contacts = model_geometry(vertices, polygons)
        geosirr_valid = bool(success and format_valid and topology_valid)
        record.update(
            {
                "format_valid": format_valid,
                "format_errors": format_errors,
                "topology_valid": topology_valid,
                "topology_errors": topology_errors,
                "vertex_count": len(vertices),
                "polygon_count": len(polygons),
                "geosirr_valid": geosirr_valid,
                "model_vertices": model_vertices,
                "internal_contacts": internal_contacts,
            }
        )
        if not geosirr_valid:
            record["failure_reason"] = "final output failed independent GeoSIRR validation"

        try:
            render_section(definition, run_dir / "final_section.png", f"GeoSIRR realization {run_number}")
        except Exception as exc:
            record["render_error"] = f"{type(exc).__name__}: {exc}"
        return record
    except Exception as exc:
        return {
            "run": run_number,
            "generation_success": False,
            "attempts": 0,
            "generation_time_seconds": time.perf_counter() - started,
            "full_prompt_sha256": None,
            "format_valid": None,
            "format_errors": [],
            "topology_valid": None,
            "topology_errors": [],
            "vertex_count": None,
            "polygon_count": None,
            "geosirr_valid": False,
            "model_vertices": None,
            "internal_contacts": None,
            "failure_reason": f"{type(exc).__name__}: {exc}",
        }


def load_and_revalidate_records() -> list[dict[str, Any]]:
    from geosirr import io

    records: list[dict[str, Any]] = []
    for run_number in range(1, RUN_COUNT + 1):
        record_path = RUNS_DIR / f"run_{run_number:02d}" / "record.json"
        if not record_path.exists():
            records.append(
                {
                    "run": run_number,
                    "generation_success": False,
                    "attempts": 0,
                    "generation_time_seconds": 0.0,
                    "format_valid": None,
                    "topology_valid": None,
                    "vertex_count": None,
                    "polygon_count": None,
                    "geosirr_valid": False,
                    "model_vertices": None,
                    "internal_contacts": None,
                    "failure_reason": "run record is missing",
                }
            )
            continue

        record = json.loads(record_path.read_text(encoding="utf-8"))
        definition_path = record_path.parent / "final_section.txt"
        if definition_path.exists():
            definition = definition_path.read_text(encoding="utf-8")
            format_valid, format_errors = io.validate_cross_section_format(definition)
            try:
                topology_valid, topology_errors = io.validate_cross_section_topology(definition)
            except Exception as exc:
                topology_valid = False
                topology_errors = [f"{type(exc).__name__}: {exc}"]
            vertices, polygons = io.parse_text(definition)
            model_vertices, internal_contacts = model_geometry(vertices, polygons)
            geosirr_valid = bool(record.get("generation_success") and format_valid and topology_valid)
            record.update(
                {
                    "format_valid": format_valid,
                    "format_errors": format_errors,
                    "topology_valid": topology_valid,
                    "topology_errors": topology_errors,
                    "vertex_count": len(vertices),
                    "polygon_count": len(polygons),
                    "geosirr_valid": geosirr_valid,
                    "model_vertices": model_vertices,
                    "internal_contacts": internal_contacts,
                    "failure_reason": (
                        None if geosirr_valid else "final output failed independent GeoSIRR validation"
                    ),
                }
            )
        else:
            record.update({"model_vertices": None, "internal_contacts": None})
        record.pop("model_polygons", None)
        record.pop("model_regions", None)
        write_json(record_path, record)
        records.append(record)
    return records


def range_text(values: list[float], digits: int = 2) -> str:
    return f"{min(values):.{digits}f}–{max(values):.{digits}f}"


def experiment_identity() -> tuple[str, str]:
    experiment_path = OUTPUT_DIR / "experiment.json"
    if experiment_path.exists():
        experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
        generation = experiment.get("generation", {})
        return generation.get("llm_name", MODEL), generation.get("llm_backend", "unknown")
    return MODEL, BACKEND


def write_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FuncFormatter

    valid = [record for record in records if record.get("geosirr_valid")]
    model, backend = experiment_identity()
    attempts = [float(record.get("attempts", 0)) for record in records]
    times = [float(record.get("generation_time_seconds", 0.0)) for record in records]
    vertex_counts = [float(record["vertex_count"]) for record in valid]
    polygon_counts = [float(record["polygon_count"]) for record in valid]
    statistics_result = {
        "attempted": RUN_COUNT,
        "valid": len(valid),
        "R_gen": len(valid) / RUN_COUNT,
        "attempts_mean": statistics.fmean(attempts),
        "attempts_min": min(attempts),
        "attempts_max": max(attempts),
        "generation_time_mean_seconds": statistics.fmean(times),
        "generation_time_min_seconds": min(times),
        "generation_time_max_seconds": max(times),
    }
    if valid:
        boundaries_consistent, expected_boundary, inconsistent_runs = boundary_check(valid)
        mean_path, mean_error = (
            mean_interior_path(valid)
            if boundaries_consistent
            else (None, f"boundary coordinates differ in runs {inconsistent_runs}")
        )
        contact_x_edges, contact_z_edges, contact_density = contact_density_grid(valid)
        contact_counts = [len(record["internal_contacts"]) for record in valid]
        statistics_result.update(
            {
                "vertex_count_mean": statistics.fmean(vertex_counts),
                "vertex_count_min": min(vertex_counts),
                "vertex_count_max": max(vertex_counts),
                "polygon_count_mean": statistics.fmean(polygon_counts),
                "polygon_count_min": min(polygon_counts),
                "polygon_count_max": max(polygon_counts),
                "boundary_node_count": len(expected_boundary),
                "expected_boundary_coordinates_km": [list(point) for point in expected_boundary],
                "boundaries_consistent": boundaries_consistent,
                "inconsistent_boundary_runs": inconsistent_runs,
                "mean_interior_path_available": mean_path is not None,
                "internal_contact_count_mean": statistics.fmean(contact_counts),
                "internal_contact_count_min": min(contact_counts),
                "internal_contact_count_max": max(contact_counts),
                "contact_density_sigma_km": CONTACT_DENSITY_SIGMA_KM,
                "maximum_internal_contact_density": float(contact_density.max()),
            }
        )

    with (OUTPUT_DIR / "run_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "run",
            "generation_success",
            "geosirr_valid",
            "attempts",
            "generation_time_seconds",
            "format_valid",
            "topology_valid",
            "vertex_count",
            "polygon_count",
            "failure_reason",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    summary_lines = [
        "# GeoSIRR repeated-generation summary",
        "",
        f"- Model: `{model}`",
        f"- Backend: `{backend}`",
        f"- Attempted runs: {RUN_COUNT}",
        f"- Independently valid GeoSIRR generations: {len(valid)}",
        f"- Generation success rate: $R_{{\\mathrm{{gen}}}}={statistics_result['R_gen']:.3f}$",
        f"- Generation attempts: mean {statistics.fmean(attempts):.2f}, range {range_text(attempts, 0)}",
        f"- Generation time: mean {statistics.fmean(times):.1f} s, range {range_text(times, 1)} s",
        "",
        "The generation success rate is",
        "",
        "$$",
        "R_{\\mathrm{gen}}=\\frac{N_{\\mathrm{valid}}}{N_{\\mathrm{attempted}}}.",
        "$$",
        "",
        "## Geometry overlay",
        "",
        "The figure shows every declared vertex from each final valid generation. Colors identify runs; all points use the same size and transparency.",
    ]
    if valid:
        boundary_status = (
            f"passed ({len(expected_boundary)} identical side-boundary nodes in every run)"
            if boundaries_consistent
            else f"failed (different side-boundary coordinates in runs {inconsistent_runs})"
        )
        summary_lines.extend(
            [
                "",
                f"- Vertices per valid model: mean {statistics.fmean(vertex_counts):.1f}, range {range_text(vertex_counts, 0)}",
                f"- Polygons per valid model: mean {statistics.fmean(polygon_counts):.1f}, range {range_text(polygon_counts, 0)}",
                f"- Boundary consistency check: {boundary_status}",
                f"- Internal contacts per valid model: mean {statistics.fmean(contact_counts):.1f}, range {range_text(contact_counts, 0)}",
                f"- Internal-contact density scale: $\\sigma={CONTACT_DENSITY_SIGMA_KM:.3f}$ km",
                "",
                "### Boundary check and mean line",
                "",
                "For each run, side-boundary nodes are identified geometrically as vertices at the minimum or maximum horizontal coordinate. The expected boundary is the modal coordinate set across valid runs. A mean line is calculated only when every run has that same set.",
                "",
                f"After removing the side-boundary nodes, each remaining path is ordered by depth and linearly resampled at {MEAN_LINE_SAMPLES} common depths. At depth $z_k$, the mean horizontal position is",
                "",
                "$$",
                "\\bar{x}(z_k)=\\frac{1}{N_{\\mathrm{valid}}}\\sum_{r=1}^{N_{\\mathrm{valid}}}x_r(z_k).",
                "$$",
                "",
                "This interpolation avoids assuming that generated DSL vertex IDs or vertex counts correspond between runs.",
                "",
                "### Internal-contact density",
                "",
                "For realization $r$, $E_r$ is the union of polygon edges shared by two polygons; exterior section-boundary edges are excluded. At grid location $\\mathbf q$, $d(\\mathbf q,E_r)$ is the shortest distance to that internal-contact geometry. The displayed density is",
                "",
                "$$",
                "D_{\\sigma}(\\mathbf q)=\\frac{1}{N_{\\mathrm{valid}}}\\sum_{r=1}^{N_{\\mathrm{valid}}}\\exp\\left(-\\frac{d(\\mathbf q,E_r)^2}{2\\sigma^2}\\right).",
                "$$",
                "",
                f"Here $\\sigma={CONTACT_DENSITY_SIGMA_KM:.3f}$ km. Stable contacts form narrow high-density bands; variable contacts form broader, lower-density bands. The field is generated-contact concentration, not a probability of geological structure in the subsurface.",
            ]
        )
        if mean_path is None:
            summary_lines.extend(["", f"The mean line was omitted: {mean_error}."])
            (OUTPUT_DIR / "mean_interior_path.csv").unlink(missing_ok=True)
        else:
            with (OUTPUT_DIR / "mean_interior_path.csv").open(
                "w", newline="", encoding="utf-8"
            ) as handle:
                writer = csv.writer(handle)
                writer.writerow(["sample", "mean_x_km", "z_km"])
                for index, (mean_x, z_value) in enumerate(mean_path):
                    writer.writerow([index, mean_x, z_value])

        fig, ax = plt.subplots(figsize=(11, 6.2))
        heatmap = ax.imshow(
            contact_density,
            origin="lower",
            extent=(contact_x_edges[0], contact_x_edges[-1], contact_z_edges[0], contact_z_edges[-1]),
            cmap="YlOrRd",
            vmin=0.0,
            vmax=1.0,
            interpolation="bilinear",
            aspect="auto",
            alpha=0.72,
            zorder=0,
        )
        colors = plt.colormaps["tab10"]
        all_vertices = []
        for record in valid:
            run_number = int(record["run"])
            color = colors((run_number - 1) % 10)
            vertices = np.asarray(record["model_vertices"], dtype=float)
            all_vertices.append(vertices)
            ax.scatter(
                vertices[:, 0],
                vertices[:, 1],
                color=color,
                s=VERTEX_MARKER_SIZE,
                alpha=0.62,
                label=f"Run {record['run']}",
                clip_on=False,
                zorder=3,
            )
        if mean_path is not None:
            ax.plot(
                mean_path[:, 0],
                mean_path[:, 1],
                color="black",
                linestyle="--",
                linewidth=1.4,
                label="Mean interior path",
                zorder=4,
            )
            mean_nodes = mean_interior_nodes(valid, mean_path)
            ax.scatter(
                mean_nodes[:, 0],
                mean_nodes[:, 1],
                color="black",
                s=14,
                clip_on=False,
                zorder=5,
            )
        annotation_lines = [
            f"Attempted: {RUN_COUNT}",
            f"N_valid: {len(valid)}   R_gen: {statistics_result['R_gen']:.2f}",
            f"Attempts: mean {statistics.fmean(attempts):.2f}, range {range_text(attempts, 0)}",
            f"Time: mean {statistics.fmean(times):.1f} s, range {range_text(times, 1)} s",
            f"Vertices/model: mean {statistics.fmean(vertex_counts):.1f}, range {range_text(vertex_counts, 0)}",
            f"Polygons/model: mean {statistics.fmean(polygon_counts):.1f}, range {range_text(polygon_counts, 0)}",
            f"Boundary check: {'passed' if boundaries_consistent else 'failed'}",
            f"Contacts/model: mean {statistics.fmean(contact_counts):.1f}, range {range_text(contact_counts, 0)}",
            f"Contact scale $\\sigma$: {CONTACT_DENSITY_SIGMA_KM:.3f} km",
        ]
        # ax.text(
        #     0.015,
        #     0.025,
        #     "\n".join(annotation_lines),
        #     transform=ax.transAxes,
        #     ha="left",
        #     va="bottom",
        #     fontsize=8.5,
        #     bbox={"facecolor": "white", "edgecolor": "0.4", "alpha": 0.9},
        # )
        combined = np.vstack(all_vertices)
        ax.set_xlim(combined[:, 0].min(), combined[:, 0].max())
        ax.set_ylim(combined[:, 1].min(), combined[:, 1].max())
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Depth (km)")
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda z_value, _: f"{0 if abs(z_value) < 1e-12 else -z_value:g}")
        )
        title = "Generated model vertices and internal-contact density"
        if mean_path is not None:
            title += ", with mean interior path"
        ax.set_title(title)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(color="0.75", linestyle="--", linewidth=0.5)
        legend = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, LEGEND_Y),
            ncols=6,
            fontsize=7,
            title=f"Model: {model}\nBackend: {backend}",
            title_fontsize=7.5,
        )
        colorbar = fig.colorbar(heatmap, ax=ax, pad=0.02)
        colorbar.set_label(r"Internal-contact density $D_\sigma$")
        fig.tight_layout(rect=(0, 0.12, 1, 1))
        fig.canvas.draw()
        axes_position = ax.get_position()
        colorbar_position = colorbar.ax.get_position()
        colorbar.ax.set_position(
            [colorbar_position.x0, axes_position.y0, colorbar_position.width, axes_position.height]
        )
        fig.savefig(
            OUTPUT_DIR / UQ_FIGURE_NAME,
            dpi=300,
            bbox_inches="tight",
            bbox_extra_artists=(legend,),
        )
        plt.close(fig)
    else:
        summary_lines.extend(["", "The geometry overlay was not created because no final generation was valid."])
        (OUTPUT_DIR / "mean_interior_path.csv").unlink(missing_ok=True)

    (OUTPUT_DIR / "vertex_uncertainty.csv").unlink(missing_ok=True)
    (OUTPUT_DIR / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    write_json(OUTPUT_DIR / "statistics.json", statistics_result)
    return statistics_result


def fixture_definition(points: list[tuple[float, float]], id_offset: int = 0) -> str:
    left_top = id_offset
    interior_ids = list(range(id_offset + 1, id_offset + 1 + len(points)))
    left_bottom = id_offset + 1 + len(points)
    right_top = left_bottom + 1
    right_bottom = left_bottom + 2
    lines = [f"{left_top} 0.0 0.0"]
    lines.extend(f"{vertex_id} {x} {z}" for vertex_id, (x, z) in zip(interior_ids, points))
    lines.extend(
        [
            f"{left_bottom} 0.0 -5.0",
            f"{right_top} 20.0 0.0",
            f"{right_bottom} 20.0 -5.0",
            "unit^west " + " ".join(map(str, [left_top, *interior_ids, left_bottom])),
            "unit^east " + " ".join(map(str, [*interior_ids, right_bottom, right_top][::-1])),
        ]
    )
    return "\n".join(lines) + "\n"


def run_self_tests() -> None:
    global OUTPUT_DIR
    import tempfile

    from geosirr import io

    base = [(8.0, 0.0), (8.6, -0.8), (9.3, -1.6), (10.2, -2.5), (11.3, -3.4), (12.6, -4.2), (14.0, -5.0)]
    identical_a = fixture_definition(base, 0)
    identical_b = fixture_definition(base, 100)
    geometries = []
    for fixture in (identical_a, identical_b):
        assert io.validate_cross_section_format(fixture)[0]
        assert io.validate_cross_section_topology(fixture)[0]
        vertices, polygons = io.parse_text(fixture)
        geometries.append(model_geometry(vertices, polygons))
    assert geometries[0] == geometries[1], "vertex IDs must not affect plotted geometry"
    boundary_records = [
        {"run": 1, "model_vertices": geometries[0][0]},
        {"run": 2, "model_vertices": geometries[1][0]},
    ]
    consistent, expected, inconsistent_runs = boundary_check(boundary_records)
    assert consistent and len(expected) == 4 and not inconsistent_runs
    mean_path, mean_error = mean_interior_path(boundary_records)
    assert mean_path is not None and mean_error is None

    _, _, density = contact_density_grid(
        [
            {"model_vertices": geometries[0][0], "internal_contacts": geometries[0][1]},
            {"model_vertices": geometries[1][0], "internal_contacts": geometries[1][1]},
        ]
    )
    assert 0.99 < density.max() <= 1.0, "identical contacts must produce unit density"

    shifted = fixture_definition([(x + 0.2, z) for x, z in base], 200)
    vertices, polygons = io.parse_text(shifted)
    shifted_geometry = model_geometry(vertices, polygons)
    _, _, shifted_density = contact_density_grid(
        [
            {"model_vertices": geometries[0][0], "internal_contacts": geometries[0][1]},
            {"model_vertices": shifted_geometry[0], "internal_contacts": shifted_geometry[1]},
        ]
    )
    assert shifted_density.max() < density.max(), "shifted contacts must reduce peak concentration"

    changed_boundary = [vertex.copy() for vertex in geometries[1][0]]
    changed_boundary[-3][1] = -4.9
    inconsistent, _, inconsistent_runs = boundary_check(
        [boundary_records[0], {"run": 2, "model_vertices": changed_boundary}]
    )
    assert not inconsistent and inconsistent_runs

    previous_output_dir = OUTPUT_DIR
    try:
        with tempfile.TemporaryDirectory() as directory:
            OUTPUT_DIR = Path(directory)
            records = [
                {
                    "run": 1,
                    "generation_success": True,
                    "geosirr_valid": True,
                    "format_valid": True,
                    "topology_valid": True,
                    "vertex_count": len(geometries[0][0]),
                    "polygon_count": 2,
                    "model_vertices": geometries[0][0],
                    "internal_contacts": geometries[0][1],
                    "attempts": 1,
                    "generation_time_seconds": 1.0,
                }
            ]
            records.extend(
                {
                    "run": run,
                    "generation_success": False,
                    "geosirr_valid": False,
                    "format_valid": None,
                    "topology_valid": None,
                    "vertex_count": None,
                    "polygon_count": None,
                    "model_vertices": None,
                    "internal_contacts": None,
                    "attempts": 0,
                    "generation_time_seconds": 0.0,
                }
                for run in range(2, RUN_COUNT + 1)
            )
            (OUTPUT_DIR / "vertex_uncertainty.csv").write_text("obsolete\n", encoding="utf-8")
            result = write_analysis(records)
            assert result["valid"] == 1
            assert result["R_gen"] == 0.1
            assert result["boundaries_consistent"]
            assert result["mean_interior_path_available"]
            assert (OUTPUT_DIR / UQ_FIGURE_NAME).is_file()
            assert (OUTPUT_DIR / "mean_interior_path.csv").is_file()
            assert not (OUTPUT_DIR / "vertex_uncertainty.csv").exists()
    finally:
        OUTPUT_DIR = previous_output_dir
    print("Synthetic analysis checks passed.")


def run_live_experiment() -> None:
    if git_value("branch", "--show-current") != "dev":
        raise RuntimeError("The live experiment may only run on branch 'dev'.")
    if not DESCRIPTION_PATH.is_file():
        raise RuntimeError(f"Description file not found: {DESCRIPTION_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    selected = select_model_provider()

    description = DESCRIPTION_PATH.read_text(encoding="utf-8")
    instruction_prompt = (ROOT / "prompts" / "section_text_generation.md").read_text(encoding="utf-8")
    (OUTPUT_DIR / "description.md").write_text(description, encoding="utf-8")
    try:
        description_source = str(DESCRIPTION_PATH.relative_to(ROOT))
    except ValueError:
        description_source = str(DESCRIPTION_PATH)

    experiment = {
        "branch": "dev",
        "geosirr_git_commit": git_value("rev-parse", "HEAD"),
        "geosirr_version": "1.0.1",
        "description_source": description_source,
        "model_provider": selected,
        "generation": {
            "runs": RUN_COUNT,
            "max_gen_iterations": MAX_GEN_ITERATIONS,
            "max_chats": MAX_CHATS,
            "llm_backend": BACKEND,
            "llm_name": MODEL,
            "llm_params": None,
        },
    }
    write_json(OUTPUT_DIR / "experiment.json", experiment)

    for run_number in range(1, RUN_COUNT + 1):
        record_path = RUNS_DIR / f"run_{run_number:02d}" / "record.json"
        if record_path.exists():
            print(f"Run {run_number:02d}/{RUN_COUNT}: existing record retained.")
            continue
        print(f"Run {run_number:02d}/{RUN_COUNT}: generating final section...")
        record = run_generation(run_number, description, instruction_prompt)
        write_json(record_path, record)
        print(
            f"Run {run_number:02d}: generation_success={record['generation_success']}, "
            f"geosirr_valid={record['geosirr_valid']}, "
            f"attempts={record['attempts']}, time={record['generation_time_seconds']:.1f}s"
        )

    records = load_and_revalidate_records()
    statistics_result = write_analysis(records)
    print(json.dumps(statistics_result, indent=2))


def analyze_only() -> None:
    if not RUNS_DIR.exists():
        raise RuntimeError(f"No saved runs found at {RUNS_DIR}")
    records = load_and_revalidate_records()
    result = write_analysis(records)
    print(json.dumps(result, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--backend",
        choices=("ollama", "openai"),
        default=DEFAULT_BACKEND,
        help=f"LLM backend (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--description",
        type=Path,
        default=DEFAULT_DESCRIPTION,
        help=f"geological-model description in Markdown (default: {DEFAULT_DESCRIPTION.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="output directory; defaults to output/uq_<description>_<model>",
    )
    parser.add_argument(
        "--vertex-size",
        type=float,
        default=VERTEX_MARKER_SIZE,
        help=f"generated-vertex marker area in points squared (default: {VERTEX_MARKER_SIZE:g})",
    )
    parser.add_argument(
        "--legend-y",
        type=float,
        default=LEGEND_Y,
        help=f"vertical legend anchor in axes coordinates (default: {LEGEND_Y:g})",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--self-test", action="store_true", help="run synthetic checks without Ollama")
    group.add_argument("--analyze-only", action="store_true", help="rebuild analysis from saved final outputs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_experiment(
        args.model, args.backend, args.description, args.output_dir, args.vertex_size, args.legend_y
    )
    try:
        if args.self_test:
            run_self_tests()
        elif args.analyze_only:
            analyze_only()
        else:
            run_live_experiment()
        return 0
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
