"""Create a PNG from a GeoSIRR cross-section text file."""

import argparse
from pathlib import Path

from geosirr.vis import plot_cross_section


def main():
    parser = argparse.ArgumentParser(
        description="Plot a GeoSIRR text cross-section as a PNG."
    )
    parser.add_argument("input", type=Path, help="Cross-section .txt file to plot.")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="PNG path. Defaults to the input path with a .png suffix."
    )
    parser.add_argument(
        "--title", default="Geological Cross Section",
        help="Title displayed above the section."
    )
    parser.add_argument(
        "--padding", type=float, default=0.1,
        help="Section padding as a fraction of each axis range (default: 0.1)."
    )
    parser.add_argument(
        "--legend-padding", type=float, default=0.25,
        help="Figure width reserved for the legend (default: 0.25)."
    )
    parser.add_argument(
        "--font-size", type=float, default=8,
        help="Legend font size in points (default: 8)."
    )
    parser.add_argument(
        "--vertex-font-size", type=float,
        help="Vertex-label font size in points (default: --font-size)."
    )
    parser.add_argument(
        "--line-width", type=float, default=1,
        help="Polygon boundary width in points (default: 1)."
    )
    parser.add_argument(
        "--vertex-size", type=float, default=3,
        help="Vertex marker size in points (default: 3)."
    )
    parser.add_argument(
        "--figsize", nargs=2, type=float, metavar=("WIDTH", "HEIGHT"),
        default=(10, 6), help="Figure size in inches (default: 10 6)."
    )
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")

    output = args.output or args.input.with_suffix(".png")
    plot_cross_section(
        definition=str(args.input),
        filename=str(output),
        title=args.title,
        figsize=tuple(args.figsize),
        padding=args.padding,
        legend_padding=args.legend_padding,
        font_size=args.font_size,
        vertex_font_size=args.vertex_font_size,
        line_width=args.line_width,
        vertex_size=args.vertex_size,
        show=False,
    )


if __name__ == "__main__":
    main()
