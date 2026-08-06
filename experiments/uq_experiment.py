#!/usr/bin/env python3
"""Run and analyze repeated GeoSIRR generations for a listric-fault description."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "gemma4:31b"
DEFAULT_DESCRIPTION = ROOT / "experiments" / "listric_fault_baseline.md"
MODEL = DEFAULT_MODEL
DESCRIPTION_PATH = DEFAULT_DESCRIPTION
OUTPUT_DIR = ROOT / "output" / "uq_listric_fault_baseline_gemma4_31b"
RUNS_DIR = OUTPUT_DIR / "runs"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
RUN_COUNT = 10
MAX_GEN_ITERATIONS = 5
MAX_CHATS = 1
TRACE_X = 8.0
SECTION_WIDTH = 20.0
SECTION_DEPTH = 5.0
COORD_TOLERANCE_KM = 0.01
PROXIMITY_KM = 0.05
GRID_SPACING_KM = 0.025
CHI2_95 = 5.991

sys.path.insert(0, str(ROOT))

# Keep matplotlib headless and its cache with the ignored experiment artifacts.
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".matplotlib"))


def configure_experiment(model: str, description: Path, output_dir: Path | None) -> None:
    global MODEL, DESCRIPTION_PATH, OUTPUT_DIR, RUNS_DIR
    MODEL = model
    DESCRIPTION_PATH = description.resolve()
    model_slug = model.replace(":", "_").replace("/", "_")
    if output_dir is None:
        OUTPUT_DIR = ROOT / "output" / f"uq_{DESCRIPTION_PATH.stem}_{model_slug}"
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


def polygon_edges(vertex_ids: list[int]) -> list[tuple[int, int]]:
    return list(zip(vertex_ids, vertex_ids[1:] + vertex_ids[:1]))


def component_side(name: str) -> str | None:
    if "^" not in name:
        return None
    suffix = name.split("^", 1)[1].lower().replace("_", "").replace("-", "")
    if "footwall" in suffix or suffix in {"foot", "west", "western", "left", "fw"}:
        return "footwall"
    if "hangingwall" in suffix or suffix in {"hanging", "east", "eastern", "right", "hw"}:
        return "hangingwall"
    return None


def extract_fault_vertices(definition: str) -> tuple[list[tuple[float, float]] | None, list[str]]:
    """Extract the shared footwall/hanging-wall path, independent of vertex IDs."""
    from geosirr import io

    vertices, polygons = io.parse_text(definition)
    coordinates = {vertex_id: (x, z) for vertex_id, x, z in vertices}
    bases: dict[str, set[str]] = defaultdict(set)
    edge_sides: dict[tuple[int, int], set[str]] = defaultdict(set)

    for name, vertex_ids in polygons:
        base = name.split("^", 1)[0]
        side = component_side(name)
        if side is not None:
            bases[base].add(side)
            for start, end in polygon_edges(vertex_ids):
                edge_sides[tuple(sorted((start, end)))].add(side)

    if not any(sides == {"footwall", "hangingwall"} for sides in bases.values()):
        return None, ["polygon names do not define corresponding footwall and hanging-wall components"]

    shared_edges = [edge for edge, sides in edge_sides.items() if sides == {"footwall", "hangingwall"}]
    if not shared_edges:
        return None, ["no shared footwall/hanging-wall edges were found"]

    adjacency: dict[int, set[int]] = defaultdict(set)
    for start, end in shared_edges:
        adjacency[start].add(end)
        adjacency[end].add(start)

    trace_candidates = [
        vertex_id
        for vertex_id in adjacency
        if abs(coordinates[vertex_id][0] - TRACE_X) <= COORD_TOLERANCE_KM
        and abs(coordinates[vertex_id][1]) <= COORD_TOLERANCE_KM
    ]
    if len(trace_candidates) != 1:
        return None, [f"expected one fault trace near (8, 0), found {len(trace_candidates)}"]

    trace = trace_candidates[0]
    component: set[int] = set()
    stack = [trace]
    while stack:
        current = stack.pop()
        if current in component:
            continue
        component.add(current)
        stack.extend(adjacency[current] - component)

    component_edges = [edge for edge in shared_edges if edge[0] in component and edge[1] in component]
    if len(component_edges) != len(shared_edges):
        return None, ["more than one disconnected footwall/hanging-wall contact was found"]
    if any(len(adjacency[vertex_id] & component) > 2 for vertex_id in component):
        return None, ["shared fault contact branches instead of forming one polyline"]

    endpoints = [vertex_id for vertex_id in component if len(adjacency[vertex_id] & component) == 1]
    if len(endpoints) != 2 or trace not in endpoints:
        return None, ["shared fault contact is not one open polyline beginning at the trace"]
    if len(component_edges) != len(component) - 1:
        return None, ["shared fault contact is not a single connected path"]

    ordered_ids = [trace]
    previous = None
    current = trace
    while True:
        next_ids = list((adjacency[current] & component) - ({previous} if previous is not None else set()))
        if not next_ids:
            break
        if len(next_ids) != 1:
            return None, ["fault path ordering is ambiguous"]
        previous, current = current, next_ids[0]
        ordered_ids.append(current)

    return [coordinates[vertex_id] for vertex_id in ordered_ids], []


def assess_fault_geometry(
    definition: str,
    require_seven_vertices: bool = True,
) -> tuple[bool, list[tuple[float, float]] | None, list[str]]:
    try:
        points, reasons = extract_fault_vertices(definition)
    except Exception as exc:
        return False, None, [f"fault extraction failed: {type(exc).__name__}: {exc}"]
    if points is None:
        return False, None, reasons

    if require_seven_vertices and len(points) != 7:
        reasons.append(f"expected 7 ordered fault vertices, extracted {len(points)}")
    if abs(points[0][0] - TRACE_X) > COORD_TOLERANCE_KM or abs(points[0][1]) > COORD_TOLERANCE_KM:
        reasons.append("fault does not begin at x=8 km on the surface")
    if abs(points[-1][1] + SECTION_DEPTH) > COORD_TOLERANCE_KM:
        reasons.append("fault does not terminate at z=-5 km")
    if any(points[index + 1][1] >= points[index][1] - COORD_TOLERANCE_KM for index in range(len(points) - 1)):
        reasons.append("fault vertices are not monotonically ordered from shallow to deep")
    if any(points[index + 1][0] <= points[index][0] + COORD_TOLERANCE_KM for index in range(len(points) - 1)):
        reasons.append("fault does not progress eastward with depth")

    return not reasons, points, reasons


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
            llm_backend="ollama",
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
            "fault_line_eligible": False,
            "fault_eligible": False,
            "fault_reasons": [],
            "fault_vertices": None,
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
            }
        )
        if geosirr_valid:
            line_eligible, _, line_reasons = assess_fault_geometry(definition, require_seven_vertices=False)
            eligible, points, reasons = assess_fault_geometry(definition)
            record["fault_line_eligible"] = line_eligible
            record["fault_line_reasons"] = line_reasons
            record["fault_eligible"] = eligible
            record["fault_vertices"] = points
            record["fault_reasons"] = reasons
            if not eligible:
                record["failure_reason"] = "prompt-compliance failure: " + "; ".join(reasons)
        else:
            record["failure_reason"] = "final output failed independent GeoSIRR validation"

        try:
            render_section(definition, run_dir / "final_section.png", f"Listric fault realization {run_number}")
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
            "fault_line_eligible": False,
            "fault_eligible": False,
            "fault_reasons": [],
            "fault_vertices": None,
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
                    "fault_line_eligible": False,
                    "fault_eligible": False,
                    "fault_vertices": None,
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
            record.update(
                {
                    "format_valid": format_valid,
                    "format_errors": format_errors,
                    "topology_valid": topology_valid,
                    "topology_errors": topology_errors,
                    "vertex_count": len(vertices),
                    "polygon_count": len(polygons),
                    "geosirr_valid": bool(record.get("generation_success") and format_valid and topology_valid),
                }
            )
            if record["geosirr_valid"]:
                line_eligible, _, line_reasons = assess_fault_geometry(definition, require_seven_vertices=False)
                eligible, points, reasons = assess_fault_geometry(definition)
                record["fault_line_eligible"] = line_eligible
                record["fault_line_reasons"] = line_reasons
                record["fault_eligible"] = eligible
                record["fault_vertices"] = points
                record["fault_reasons"] = reasons
                record["failure_reason"] = None if eligible else "prompt-compliance failure: " + "; ".join(reasons)
            else:
                record["fault_line_eligible"] = False
                record["fault_eligible"] = False
                record["fault_vertices"] = None
        records.append(record)
    return records


def uncertainty_statistics(faults: list[list[list[float]]]) -> tuple[Any, Any, Any, float, float]:
    import numpy as np

    values = np.asarray(faults, dtype=float)
    if values.shape[0] < 2 or values.shape[1:] != (7, 2):
        raise ValueError("uncertainty requires at least two eligible seven-vertex faults")
    means = values.mean(axis=0)
    covariances = np.stack([np.cov(values[:, index, :], rowvar=False, ddof=1) for index in range(7)])
    radial = np.sqrt(np.trace(covariances, axis1=1, axis2=2))
    overall = float(np.sqrt(np.trace(covariances, axis1=1, axis2=2).mean()))
    return values, means, covariances, radial, overall


def distance_to_fault_grid(fault: Any, grid_x: Any, grid_z: Any) -> Any:
    import numpy as np

    minimum = np.full(grid_x.shape, np.inf)
    for start, end in zip(fault[:-1], fault[1:]):
        dx = end[0] - start[0]
        dz = end[1] - start[1]
        scale = dx * dx + dz * dz
        projection = ((grid_x - start[0]) * dx + (grid_z - start[1]) * dz) / scale
        projection = np.clip(projection, 0.0, 1.0)
        nearest_x = start[0] + projection * dx
        nearest_z = start[1] + projection * dz
        minimum = np.minimum(minimum, np.hypot(grid_x - nearest_x, grid_z - nearest_z))
    return minimum


def probability_grid(values: Any) -> tuple[Any, Any, Any]:
    import numpy as np

    x = np.arange(0.0, SECTION_WIDTH + GRID_SPACING_KM / 2, GRID_SPACING_KM)
    z = np.arange(-SECTION_DEPTH, GRID_SPACING_KM / 2, GRID_SPACING_KM)
    grid_x, grid_z = np.meshgrid(x, z)
    counts = np.zeros(grid_x.shape, dtype=float)
    for fault in values:
        counts += distance_to_fault_grid(fault, grid_x, grid_z) <= PROXIMITY_KM
    return x, z, counts / len(values)


def add_covariance_shape(ax: Any, mean: Any, covariance: Any) -> None:
    import numpy as np
    from matplotlib.patches import Ellipse

    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    eigenvalues = np.maximum(eigenvalues, 0.0)
    if eigenvalues[-1] < 1e-14:
        ax.plot(mean[0], mean[1], marker="o", markerfacecolor="none", markeredgecolor="black", markersize=7)
        return
    principal = eigenvectors[:, -1]
    if eigenvalues[0] < 1e-14:
        half_length = math.sqrt(CHI2_95 * eigenvalues[-1])
        endpoints = np.vstack((mean - half_length * principal, mean + half_length * principal))
        ax.plot(endpoints[:, 0], endpoints[:, 1], color="black", linewidth=1.2)
        return
    width, height = 2.0 * np.sqrt(CHI2_95 * eigenvalues)
    angle = math.degrees(math.atan2(principal[1], principal[0]))
    ax.add_patch(
        Ellipse(
            xy=mean,
            width=height,
            height=width,
            angle=angle,
            facecolor="none",
            edgecolor="black",
            linewidth=1.1,
        )
    )


def range_text(values: list[float], digits: int = 2) -> str:
    return f"{min(values):.{digits}f}–{max(values):.{digits}f}"


def write_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    import matplotlib.pyplot as plt
    import numpy as np

    valid = [record for record in records if record.get("geosirr_valid")]
    line_eligible = [record for record in records if record.get("fault_line_eligible")]
    eligible = [record for record in records if record.get("fault_eligible")]
    rates = {
        "attempted": RUN_COUNT,
        "valid": len(valid),
        "line_eligible": len(line_eligible),
        "eligible": len(eligible),
        "R_gen": len(valid) / RUN_COUNT,
        "R_line": len(line_eligible) / RUN_COUNT,
        "R_fault": len(eligible) / RUN_COUNT,
    }

    with (OUTPUT_DIR / "run_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "run",
            "generation_success",
            "geosirr_valid",
            "fault_line_eligible",
            "fault_eligible",
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
        "# Listric-fault experiment summary",
        "",
        f"- Attempted runs: {RUN_COUNT}",
        f"- Independently valid GeoSIRR generations: {len(valid)}",
        f"- Extractable final fault polylines: {len(line_eligible)}",
        f"- Listric-geometry-eligible generations: {len(eligible)}",
        f"- R_gen: {rates['R_gen']:.3f}",
        f"- R_line: {rates['R_line']:.3f}",
        f"- R_fault: {rates['R_fault']:.3f}",
        f"- Eligibility coordinate tolerance: {COORD_TOLERANCE_KM:g} km",
        f"- Probability-map proximity radius: {PROXIMITY_KM:g} km",
        "",
        "A GeoSIRR-valid output that fails the seven-vertex listric criteria is a prompt-compliance failure and is excluded from vertex covariance calculations, but its extractable final fault polyline remains in the proximity heat map.",
        "",
        "## Uncertainty definitions",
        "",
        "For eligible run r and ordered fault vertex j, let v_r,j = [x_r,j, z_r,j]^T. The per-vertex mean and sample covariance are",
        "",
        "mu_j = (1/N) sum_r v_r,j,",
        "",
        "Sigma_j = (1/(N-1)) sum_r (v_r,j - mu_j)(v_r,j - mu_j)^T.",
        "",
        "The radial vertex dispersion is u_j = sqrt(trace(Sigma_j)). The overall metric is U_RMS = sqrt((1/7) sum_j trace(Sigma_j)), and U_RMS* = U_RMS / 5 km.",
        "",
        "The plotted 95% covariance contour satisfies (v - mu_j)^T Sigma_j^-1 (v - mu_j) = 5.991. Singular covariance is shown as a point or line.",
        "",
        "For grid point q and extractable final fault polyline F_r, P_epsilon(q) = (1/N_line) sum_r I[d(q, F_r) <= epsilon], with epsilon = 0.05 km.",
    ]

    has_vertex_uncertainty = len(eligible) >= 2
    if has_vertex_uncertainty:
        faults = [record["fault_vertices"] for record in eligible]
        _, means, covariances, radial, overall = uncertainty_statistics(faults)
        normalized = overall / SECTION_DEPTH
        rates.update({"U_RMS_km": overall, "U_RMS_normalized": normalized})

        with (OUTPUT_DIR / "vertex_uncertainty.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                ["vertex_index", "mean_x_km", "mean_z_km", "cov_xx_km2", "cov_xz_km2", "cov_zz_km2", "u_j_km"]
            )
            for index in range(7):
                writer.writerow(
                    [
                        index,
                        means[index, 0],
                        means[index, 1],
                        covariances[index, 0, 0],
                        covariances[index, 0, 1],
                        covariances[index, 1, 1],
                        radial[index],
                    ]
                )
    else:
        means = covariances = None
        overall = normalized = None
        (OUTPUT_DIR / "vertex_uncertainty.csv").write_text(
            "vertex_index,mean_x_km,mean_z_km,cov_xx_km2,cov_xz_km2,cov_zz_km2,u_j_km\n",
            encoding="utf-8",
        )
        summary_lines.extend(["", "Vertex covariance was not calculated because fewer than two runs had seven fault vertices."])

    line_values = [np.asarray(record["fault_vertices"], dtype=float) for record in line_eligible]
    if line_values:
        x, z, probability = probability_grid(line_values)
        fig, ax = plt.subplots(figsize=(11, 5.5))
        heatmap = ax.imshow(
            probability,
            origin="lower",
            extent=(x[0], x[-1], z[0], z[-1]),
            cmap="YlOrRd",
            vmin=0.0,
            vmax=1.0,
            interpolation="nearest",
            aspect="equal",
        )
        colors = plt.colormaps["tab10"]
        for index, (record, fault) in enumerate(zip(line_eligible, line_values)):
            color = colors(index % 10)
            ax.plot(fault[:, 0], fault[:, 1], color=color, linewidth=1.0, alpha=0.45)
            ax.scatter(
                fault[:, 0],
                fault[:, 1],
                color=color,
                s=20,
                alpha=0.8,
                label=f"Run {record['run']}",
                zorder=3,
            )

        if has_vertex_uncertainty:
            ax.plot(means[:, 0], means[:, 1], color="black", linewidth=2.2, label="7-vertex mean", zorder=4)
            ax.scatter(means[:, 0], means[:, 1], color="black", s=24, zorder=5)
            for mean, covariance in zip(means, covariances):
                add_covariance_shape(ax, mean, covariance)

        attempts = [float(record.get("attempts", 0)) for record in records]
        times = [float(record.get("generation_time_seconds", 0.0)) for record in records]
        annotation_lines = [
            f"Attempted: {RUN_COUNT}",
            f"N_valid: {len(valid)}   N_lines: {len(line_eligible)}",
            f"N_7vertex: {len(eligible)}",
            f"R_gen: {rates['R_gen']:.2f}   R_line: {rates['R_line']:.2f}",
            f"R_fault: {rates['R_fault']:.2f}",
            f"Attempts: mean {statistics.fmean(attempts):.2f}, range {range_text(attempts, 0)}",
            f"Time: mean {statistics.fmean(times):.1f} s, range {range_text(times, 1)} s",
        ]
        if has_vertex_uncertainty:
            annotation_lines.extend(
                [f"U_RMS: {overall:.4f} km", f"U_RMS*: {normalized:.4f}"]
            )
        ax.text(
            0.015,
            0.025,
            "\n".join(annotation_lines),
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8.5,
            bbox={"facecolor": "white", "edgecolor": "0.4", "alpha": 0.9},
        )
        ax.set_xlim(0, SECTION_WIDTH)
        ax.set_ylim(-SECTION_DEPTH, 0)
        ax.set_xlabel("Horizontal distance x (km)")
        ax.set_ylabel("Elevation z (km)")
        ax.set_title("Final listric-fault realizations and empirical 50 m proximity probability")
        ax.grid(color="0.75", linestyle="--", linewidth=0.5)
        ax.legend(loc="upper right", ncols=2, fontsize=7)
        colorbar = fig.colorbar(heatmap, ax=ax, pad=0.02)
        colorbar.set_label(r"Empirical proximity probability $P_{\epsilon}$")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "uq_summary.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
    else:
        summary_lines.extend(["", "The proximity heat map was not created because no final fault polyline was extractable."])

    if has_vertex_uncertainty:
        summary_lines.extend(
            [
                "",
                f"- U_RMS: {overall:.6f} km",
                f"- U_RMS normalized by 5 km depth: {normalized:.6f}",
            ]
        )
    summary_lines.extend(
        [
            "",
            "U_RMS measures repeatability of the seven ordered control vertices in final seven-vertex generations. The heat map uses every extractable final fault polyline, without resampling variable-length vertex sequences, and gives the empirical fraction within 0.05 km of each grid point. Neither quantity represents uncertainty in the real subsurface fault location.",
        ]
    )
    (OUTPUT_DIR / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    write_json(OUTPUT_DIR / "statistics.json", rates)
    return rates


def fixture_definition(points: list[tuple[float, float]], id_offset: int = 0) -> str:
    left_top = id_offset
    fault_ids = list(range(id_offset + 1, id_offset + 1 + len(points)))
    left_bottom = id_offset + 1 + len(points)
    right_top = left_bottom + 1
    right_bottom = left_bottom + 2
    lines = [f"{left_top} 0.0 0.0"]
    lines.extend(f"{vertex_id} {x} {z}" for vertex_id, (x, z) in zip(fault_ids, points))
    lines.extend(
        [
            f"{left_bottom} 0.0 -5.0",
            f"{right_top} 20.0 0.0",
            f"{right_bottom} 20.0 -5.0",
            "unit^footwall " + " ".join(map(str, [left_top, *fault_ids, left_bottom])),
            "unit^hangingwall " + " ".join(map(str, [*fault_ids, right_bottom, right_top][::-1])),
        ]
    )
    return "\n".join(lines) + "\n"


def run_self_tests() -> None:
    global OUTPUT_DIR
    import tempfile

    import numpy as np
    from geosirr import io

    base = [(8.0, 0.0), (8.6, -0.8), (9.3, -1.6), (10.2, -2.5), (11.3, -3.4), (12.6, -4.2), (14.0, -5.0)]
    identical_a = fixture_definition(base, 0)
    identical_b = fixture_definition(base, 100)
    for fixture in (identical_a, identical_b):
        assert io.validate_cross_section_format(fixture)[0]
        assert io.validate_cross_section_topology(fixture)[0]
        eligible, points, reasons = assess_fault_geometry(fixture)
        assert eligible, reasons
        assert points == base

    _, points_a, _ = assess_fault_geometry(identical_a)
    _, points_b, _ = assess_fault_geometry(identical_b)
    values, _, covariances, _, overall = uncertainty_statistics([points_a, points_b])
    assert overall == 0.0
    _, _, probability = probability_grid(values)
    assert probability.max() == 1.0
    assert 0 < np.count_nonzero(probability == 1.0) < probability.size

    shifted = base.copy()
    shifted[1:-1] = [(x + 0.2, z) for x, z in shifted[1:-1]]
    shifted_fixture = fixture_definition(shifted, 200)
    shifted_eligible, shifted_points, shifted_reasons = assess_fault_geometry(shifted_fixture)
    assert shifted_eligible, shifted_reasons
    shifted_values, _, shifted_covariances, _, shifted_overall = uncertainty_statistics([points_a, shifted_points])
    assert shifted_overall > 0.0
    assert np.any(shifted_covariances > covariances)
    _, _, shifted_probability = probability_grid(shifted_values)
    assert np.count_nonzero(shifted_probability) > np.count_nonzero(probability)

    # Remove one interior point while preserving the terminal point.
    short_points = base[:4] + base[5:]
    short_fixture = fixture_definition(short_points, 300)
    short_eligible, extracted, short_reasons = assess_fault_geometry(short_fixture)
    assert not short_eligible
    assert extracted is not None and len(extracted) == 6
    assert any("expected 7" in reason for reason in short_reasons)
    short_line_eligible, _, short_line_reasons = assess_fault_geometry(
        short_fixture, require_seven_vertices=False
    )
    assert short_line_eligible, short_line_reasons

    long_points = base[:4] + [(10.7, -2.9)] + base[4:]
    long_fixture = fixture_definition(long_points, 400)
    long_eligible, extracted, long_reasons = assess_fault_geometry(long_fixture)
    assert not long_eligible
    assert extracted is not None and len(extracted) == 8
    assert any("expected 7" in reason for reason in long_reasons)

    records = [
        {"generation_success": False, "geosirr_valid": False, "fault_eligible": False, "fault_vertices": None},
        {"generation_success": True, "geosirr_valid": True, "fault_eligible": True, "fault_vertices": points_a},
        {"generation_success": True, "geosirr_valid": True, "fault_eligible": True, "fault_vertices": shifted_points},
    ]
    uncertainty_inputs = [record["fault_vertices"] for record in records if record["fault_eligible"]]
    assert len(uncertainty_inputs) == 2
    assert sum(record["geosirr_valid"] for record in records) == 2

    previous_output_dir = OUTPUT_DIR
    try:
        with tempfile.TemporaryDirectory() as directory:
            OUTPUT_DIR = Path(directory)
            line_only_records = [
                {
                    "run": 1,
                    "generation_success": True,
                    "geosirr_valid": True,
                    "fault_line_eligible": True,
                    "fault_eligible": False,
                    "fault_vertices": extracted,
                    "attempts": 1,
                    "generation_time_seconds": 1.0,
                }
            ]
            line_only_records.extend(
                {
                    "run": run,
                    "generation_success": False,
                    "geosirr_valid": False,
                    "fault_line_eligible": False,
                    "fault_eligible": False,
                    "fault_vertices": None,
                    "attempts": 0,
                    "generation_time_seconds": 0.0,
                }
                for run in range(2, RUN_COUNT + 1)
            )
            line_only_statistics = write_analysis(line_only_records)
            assert line_only_statistics["line_eligible"] == 1
            assert line_only_statistics["eligible"] == 0
            assert (OUTPUT_DIR / "uq_summary.png").is_file()
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
    selected = select_ollama_host()

    # Import GeoSIRR only after OLLAMA_HOST has been set.
    import clarification

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
        "model_host": selected,
        "generation": {
            "runs": RUN_COUNT,
            "max_gen_iterations": MAX_GEN_ITERATIONS,
            "max_chats": MAX_CHATS,
            "llm_backend": "ollama",
            "llm_name": MODEL,
            "llm_params": None,
        },
    }
    write_json(OUTPUT_DIR / "experiment.json", experiment)

    clarification_path = OUTPUT_DIR / "clarification.json"
    if clarification_path.exists():
        clarification_result = json.loads(clarification_path.read_text(encoding="utf-8"))
    else:
        print(f"Clarifying frozen description once with {MODEL} at {selected['host']}...")
        clarification_result = clarification.validate_description(
            description, llm_model=MODEL, llm_backend="ollama"
        )
        write_json(clarification_path, clarification_result)
    if clarification_result.get("status") != "complete":
        raise RuntimeError(
            "The one-time clarification check did not classify the frozen description as complete; "
            "no generation runs were started."
        )

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
            f"geosirr_valid={record['geosirr_valid']}, fault_eligible={record['fault_eligible']}, "
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
        help=f"exact Ollama model tag (default: {DEFAULT_MODEL})",
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--self-test", action="store_true", help="run synthetic checks without Ollama")
    group.add_argument("--analyze-only", action="store_true", help="rebuild analysis from saved final outputs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_experiment(args.model, args.description, args.output_dir)
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
