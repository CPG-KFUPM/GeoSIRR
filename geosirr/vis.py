import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from . import io


def plot_cross_section(definition: str=None,                       
                       filename: str=None,
                       colormap: str='auto',
                       vertex_label_color: str='gray',
                       title: str='Geological Cross Section',
                       legend_title: str='Bodies',
                       figsize: tuple=(10, 6),
                       padding: float=0.1,
                       legend_padding: float=0.25,
                       font_size: float=8,
                       vertex_font_size: float=None,
                       line_width: float=1,
                       vertex_size: float=3,
                       show: bool=True):
    r"""
    Plot a geological cross-section from vertex and polygon definitions.

    Parameters
    ----------
    definition : :obj:`str`
        Definition of the cross-section geometry, which can be provided in two ways:
        1. As a multiline string containing vertex coordinates and polygon definitions.
        2. As a path to a file containing the same information.    
    filename : :obj:`str`, optional
        If provided, the plot will be saved to this file path. If not provided, the plot will not be saved.
    colormap : :obj:`str`, optional
        The name of the matplotlib colormap to use for coloring the polygons.
        Default is 'auto', which means:
        - 'Set2' for 8 colors and fewer,
        - 'Set3' for more than 8 colors and less than 13.
        - 'tab20' for more than 13 colors and less than 20.
        - 'viridis' for more than 20 colors.
    vertex_label_color : :obj:`str`, optional
        Color of the vertex labels. Default is 'gray'. If None, vertex labels will not be shown.
    title : :obj:`str`, optional
        Title of the plot. Default is 'Geological Cross Section'.
    legend_title : :obj:`str`, optional
        Title of the legend. Default is 'Bodies'.
    figsize: : :obj:`tuple`, optional
        Size of the figure to create, specified as a tuple (width, height) in inches. Default is (10, 6).
    padding : :obj:`float`, optional
        Fraction of each axis range added around the plotted section. Default is 0.1.
    legend_padding : :obj:`float`, optional
        Fraction of the figure width reserved on the right for the legend. Default is 0.25.
    font_size : :obj:`float`, optional
        Font size used for the legend. Default is 8.
    vertex_font_size : :obj:`float`, optional
        Font size used for vertex labels. If omitted, ``font_size`` is used.
    line_width : :obj:`float`, optional
        Width of polygon boundary lines. Default is 1.
    vertex_size : :obj:`float`, optional
        Size of vertex markers in points. Default is 3.
    show : :obj:`bool`, optional
        Whether to display the figure after creating it. Default is True.
    
    Notes
    -----


    Returns
    -------
    fig, ax : :obj:`tuple` of :obj:`matplotlib.figure.Figure` and :obj:`matplotlib.axes.Axes`
        matplotlib Figure and Axes objects for further customization.
    """
    # Load raw definition from file or use string directly
    if isinstance(definition, str) and os.path.isfile(definition):
        with open(definition, 'r') as f:
            raw = f.read()
    else:
        raw = definition or ""

    # Validate the content
    is_valid, errs = io.validate_cross_section_format(raw)
    if not is_valid:            
        print("Format errors:")
        print("\n".join(errs))
        raise ValueError("Invalid format in the input.")
    
    
    # Parse lines, stripping comments and whitespace
    lines = raw.strip().splitlines()
    vertices = {}
    polygons = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('#')[0].strip().split()
        first = parts[0]
        # Vertex definition: ID x y
        if first.isdigit():
            if len(parts) < 3:
                raise ValueError(f"Invalid vertex definition: '{line}'")
            vid = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            # Negate y to match the convention of depth being positive downwards
            vertices[vid] = (x, -y)
        else:
            # Polygon definition: name vid1 vid2 ...            
            raw_name = parts[0] # Get first part as the raw name
            ids = [int(x) for x in parts[1:]]
            polygons[raw_name] = ids

    if not vertices:
        raise ValueError("No vertices found in definition.")
    if not polygons:
        raise ValueError("No polygons found in definition.")

    if padding < 0:
        raise ValueError("padding must be non-negative.")
    if not 0 <= legend_padding < 1:
        raise ValueError("legend_padding must be between 0 (inclusive) and 1 (exclusive).")

    vertex_font_size = font_size if vertex_font_size is None else vertex_font_size

    # Create figure and axes
    fig, ax = plt.subplots(figsize=figsize)

    # Extract raw bases (before any '^') in original order
    bases = [name.split('^', 1)[0] for name in polygons]
    unique_bases = list(dict.fromkeys(bases))  # preserve appearance order
        
    # Get colormap
    ncolors = len(unique_bases)
    if colormap == 'auto':
        if ncolors <= 8:
            colormap = 'Set2'
        elif ncolors < 13:
            colormap = 'Set3'
        elif ncolors < 20:
            colormap = 'tab20'
        else:
            colormap = 'viridis'
    cmap = plt.colormaps[colormap].resampled(ncolors)
    
    # Map each base to its color
    color_map = {base: cmap(i) for i, base in enumerate(unique_bases)}

    # Plot each polygon using the base-colored mapping
    for raw_name, ids in polygons.items():
        base = raw_name.split('^', 1)[0]
        verts = [vertices[i] for i in ids]
        poly = Polygon(
            verts,
            closed=True,
            facecolor=color_map[base],
            edgecolor='k',
            linewidth=line_width,
            label=raw_name.replace('^', ' ')
        )
        ax.add_patch(poly)

    # Plot vertices
    for vid, (x, y) in vertices.items():
        ax.plot(x, y, 'o', color='black', markersize=vertex_size)

    # Compute and pad axis limits
    xs = np.array([v[0] for v in vertices.values()])
    ys = np.array([v[1] for v in vertices.values()])
    x_pad = padding * (xs.max() - xs.min())
    y_pad = padding * (ys.max() - ys.min())
    ax.set_xlim(xs.min() - x_pad, xs.max() + x_pad)
    ax.set_ylim(ys.min() - y_pad, ys.max() + y_pad)
    ax.set_aspect('equal')

    # Add grid, labels, title, legend
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Depth (km)')
    ax.set_title(title)

    # Reverse the y-axis to have depth increase downwards
    ax.set_ylim(ax.get_ylim()[::-1])

    if vertex_label_color is not None:
        # Get the dimensions of the cross-section        
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        x_range = x_max - x_min
        y_range = y_max - y_min
        # Label shift for vertex IDs
        x_shift = 0.005 * x_range
        y_shift = - 0.005 * y_range
        # Add vertex labels with a small shift
        for vid, (x, y) in vertices.items():
            ax.text(x + x_shift, y - y_shift, str(vid),
                    color=vertex_label_color,
                    fontsize=vertex_font_size, ha='left', va='bottom')
            
    # Add legend for polygons
    ax.legend(title=legend_title,
              loc='center left',
              bbox_to_anchor=(1.02, 0.5),
              fontsize=font_size,
              title_fontsize=font_size)

    fig.tight_layout(rect=(0, 0, 1 - legend_padding, 1))

    # Save the figure if a filename is provided (before showing interactively)
    if filename:
        fig.savefig(filename, bbox_inches='tight', dpi=300)
        print(f"Plot saved to {filename}")

    if show:
        plt.show(block=False)  # Show plot without blocking execution

        # Make sure it renders immediately
        fig.canvas.draw()        # draw the figure
        fig.canvas.flush_events()  # push events to the GUI
        plt.pause(0.001)         # short pause to let the GUI update

    return fig, ax
