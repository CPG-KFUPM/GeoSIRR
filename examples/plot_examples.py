"""Plot every valid GeoSIRR text example with editable per-example settings."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from geosirr import io
from geosirr.vis import plot_cross_section

DEFAULT_OPTIONS = {
    "padding": 0,
    "legend_padding": 0.25,
    "legend_gap": 0.03,
    "line_width": 1,
    "vertex_size": 3,
    "vertex_font_size": None,
    "font_size": 8,
    "title_padding": 12,
    "figsize": (10, 6),
}

# Add or change options here to customize an individual example.
PLOT_OPTIONS = {
    "example_single_layer.txt": {"title": "Simple cross section with a single layer"},
    "example_two_layers.txt": {"title": "Two Horizontal Layers"},
    "example_salt_diapir.txt": {"title": "Salt Diapir"},
    "example_listric_normal_fault.txt": {"title": "Listric Normal Fault"},
    "example_listric_normal_fault_2.txt": {"title": "Listric Normal Fault (repeated)"},
    "example_listric_normal_fault_2_refined.txt": {
        "title": "Refined Listric Normal Fault: Rollover Added", "vertex_font_size": 6, "vertex_size": 2
    },
    "example_listric_normal_fault_2_refined_2.txt": {
        "title": "Refined Listric Normal Fault: Second Fault Added", "vertex_font_size": 6, "vertex_size": 2
    },
    "example_laccolith_dyke.txt": {"title": "Laccolith Dyke Intrusion", "vertex_font_size": 6, "vertex_size": 2},
        "example_laccolith_dyke_2.txt": {"title": "Laccolith Dyke Intrusion (repeated)", "vertex_font_size": 6, "vertex_size": 2},
    "example_prograding_delta.txt": {"title": "Prograding Delta", "vertex_font_size": 6, "vertex_size": 2, "legend_padding": 0.2},
    "example_domino_listric_rift.txt": {"title": "Domino-style Listric Rift", "legend_padding": 0.1, "font_size": 6, "vertex_font_size": 5, "line_width": 0.7, "vertex_size": 2},
    "example_syn-rift_half-graben.txt": {"title": "Syn-rift Half-graben", "legend_padding": 0.1, "font_size": 6, "vertex_font_size": 5, "line_width": 0.7, "vertex_size": 2},
}


def main():
    examples_dir = Path(__file__).resolve().parent

    for input_path in sorted(examples_dir.glob("example_*.txt")):
        is_valid, _ = io.validate_cross_section_format(input_path.read_text())
        if not is_valid:
            print(f"Skipping {input_path.name}: not a GeoSIRR cross-section definition.")
            continue

        options = DEFAULT_OPTIONS | PLOT_OPTIONS.get(input_path.name, {})
        output_path = input_path.with_suffix(".png")
        fig, _ = plot_cross_section(
            definition=str(input_path),
            filename=str(output_path),
            show=False,
            **options,
        )
        plt.close(fig)


if __name__ == "__main__":
    main()
