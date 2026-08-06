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


def model_geometry(
    vertices: list[tuple[int, float, float]],
    polygons: list[tuple[str, list[int]]],
) -> tuple[list[list[float]], list[list[list[float]]]]:
    coordinates = {vertex_id: [x, z] for vertex_id, x, z in vertices}
    model_vertices = [coordinates[vertex_id] for vertex_id, _, _ in vertices]
    model_polygons = [[coordinates[vertex_id] for vertex_id in vertex_ids] for _, vertex_ids in polygons]
    return model_vertices, model_polygons


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
            "model_vertices": None,
            "model_polygons": None,
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
        model_vertices, model_polygons = model_geometry(vertices, polygons)
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
                "model_polygons": model_polygons,
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
            "model_polygons": None,
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
                    "model_polygons": None,
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
            model_vertices, model_polygons = model_geometry(vertices, polygons)
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
                    "model_polygons": model_polygons,
                    "failure_reason": (
                        None if geosirr_valid else "final output failed independent GeoSIRR validation"
                    ),
                }
            )
        else:
            record.update({"model_vertices": None, "model_polygons": None})
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
    return MODEL, "ollama"


def write_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    import matplotlib.pyplot as plt
    import numpy as np

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
        statistics_result.update(
            {
                "vertex_count_mean": statistics.fmean(vertex_counts),
                "vertex_count_min": min(vertex_counts),
                "vertex_count_max": max(vertex_counts),
                "polygon_count_mean": statistics.fmean(polygon_counts),
                "polygon_count_min": min(polygon_counts),
                "polygon_count_max": max(polygon_counts),
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
        "The figure overlays every polygon boundary and every declared vertex from each final valid generation. Colors identify runs. No correspondence between vertices in different runs is assumed, so the overlay is descriptive and does not define a scalar geometric-uncertainty metric.",
    ]
    if valid:
        summary_lines.extend(
            [
                "",
                f"- Vertices per valid model: mean {statistics.fmean(vertex_counts):.1f}, range {range_text(vertex_counts, 0)}",
                f"- Polygons per valid model: mean {statistics.fmean(polygon_counts):.1f}, range {range_text(polygon_counts, 0)}",
            ]
        )
        fig, ax = plt.subplots(figsize=(11, 5.5))
        colors = plt.colormaps["tab10"]
        all_vertices = []
        for record in valid:
            run_number = int(record["run"])
            color = colors((run_number - 1) % 10)
            vertices = np.asarray(record["model_vertices"], dtype=float)
            all_vertices.append(vertices)
            for polygon in record["model_polygons"]:
                points = np.asarray(polygon + [polygon[0]], dtype=float)
                ax.plot(points[:, 0], points[:, 1], color=color, linewidth=0.8, alpha=0.22)
            ax.scatter(
                vertices[:, 0],
                vertices[:, 1],
                facecolors="none",
                edgecolors=[color],
                s=14 + 3 * (RUN_COUNT - run_number),
                linewidths=0.9,
                alpha=0.9,
                label=f"Run {record['run']}",
                zorder=3,
            )
        annotation_lines = [
            f"Attempted: {RUN_COUNT}",
            f"N_valid: {len(valid)}   R_gen: {statistics_result['R_gen']:.2f}",
            f"Attempts: mean {statistics.fmean(attempts):.2f}, range {range_text(attempts, 0)}",
            f"Time: mean {statistics.fmean(times):.1f} s, range {range_text(times, 1)} s",
            f"Vertices/model: mean {statistics.fmean(vertex_counts):.1f}, range {range_text(vertex_counts, 0)}",
            f"Polygons/model: mean {statistics.fmean(polygon_counts):.1f}, range {range_text(polygon_counts, 0)}",
        ]
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
        combined = np.vstack(all_vertices)
        x_span = max(float(np.ptp(combined[:, 0])), 1.0)
        z_span = max(float(np.ptp(combined[:, 1])), 1.0)
        ax.set_xlim(combined[:, 0].min() - 0.02 * x_span, combined[:, 0].max() + 0.02 * x_span)
        ax.set_ylim(combined[:, 1].min() - 0.04 * z_span, combined[:, 1].max() + 0.04 * z_span)
        ax.set_xlabel("Horizontal distance x (km)")
        ax.set_ylabel("Elevation z (km)")
        ax.set_title("Final GeoSIRR geometry realizations and all model vertices")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(color="0.75", linestyle="--", linewidth=0.5)
        ax.legend(
            loc="upper right",
            ncols=2,
            fontsize=7,
            title=f"Model: {model}\nBackend: {backend}",
            title_fontsize=7.5,
        )
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "uq_summary.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
    else:
        summary_lines.extend(["", "The geometry overlay was not created because no final generation was valid."])

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
                    "polygon_count": len(geometries[0][1]),
                    "model_vertices": geometries[0][0],
                    "model_polygons": geometries[0][1],
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
                    "model_polygons": None,
                    "attempts": 0,
                    "generation_time_seconds": 0.0,
                }
                for run in range(2, RUN_COUNT + 1)
            )
            (OUTPUT_DIR / "vertex_uncertainty.csv").write_text("obsolete\n", encoding="utf-8")
            result = write_analysis(records)
            assert result["valid"] == 1
            assert result["R_gen"] == 0.1
            assert (OUTPUT_DIR / "uq_summary.png").is_file()
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
