import re
from typing import List, Tuple
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union


def clean_code_block_markers(text: str) -> str:
    """
    Remove Markdown code block fences and language identifiers from text.

    - If the entire string is wrapped in a triple-backtick code block (with optional language), unwrap it.
    - Remove any stray triple-backtick markers or language tags within the text.
    - Return the cleaned, stripped content.
    """
    # 1. Unwrap a full code block if present:
    full_block = re.match(r"^\s*```(?:[^\n]*)\n([\s\S]*?)\n```\s*$", text)
    if full_block:
        text = full_block.group(1)

    # 2. Remove any remaining opening fences with optional language tag
    text = re.sub(r"```[a-zA-Z0-9]*\n?", "", text)
    # 3. Remove any closing fences
    text = text.replace("```", "")

    return text.strip()


def parse_text(text: str) -> Tuple[List[Tuple[int, float, float]], List[Tuple[str, List[int]]]]:
    r"""
    Parses a text representation of vertices and polygons.
    Returns a list of vertices ``(id, x, z)`` and polygons ``(name, [vertex_ids])``.

    Notes
    -----
    Inline comments (starting with '#') are ignored.

    Parameters
    ----------
    text : :obj:`str`
        Multiline string containing vertex and polygon definitions.

    Returns
    -------
    :obj:`tuple` of :obj:`list[tuple[int, float, float]]` and :obj:`list[tuple[str, list[int]]]`
        The first list contains vertices as tuples of (id, x, z).
        The second list contains polygons as tuples of (name, [vertex_ids]).    
    """
    vertices: List[Tuple[int, float, float]] = []
    polygons: List[Tuple[str, List[int]]] = []

    for lineno, raw in enumerate(text.splitlines(), start=1):
        # strip inline comments and whitespace
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue

        parts = line.split()
        # vertex: id x z
        if len(parts) == 3 and parts[0].isdigit():
            vid = int(parts[0])
            x = float(parts[1])
            z = float(parts[2])
            vertices.append((vid, x, z))

        # polygon: name id1 id2 ...
        elif len(parts) >= 2:
            name = parts[0]
            # Check if name is valid (only one ^ is allowed)
            if '^' in name:
                if name.count('^') > 1:
                    raise ValueError(f"Line {lineno}: Polygon name '{name}' contains more than one '^'.")
            try:
                ids = [int(p) for p in parts[1:]]
            except ValueError as e:
                raise ValueError(
                    f"Line {lineno}: cannot parse polygon IDs in '{line}'"
                ) from e
            polygons.append((name, ids))

        else:
            raise ValueError(f"Line {lineno}: Unrecognized line format: '{line}'")

    return vertices, polygons


def validate_cross_section_format(text: str) -> Tuple[bool, List[str]]:
    """
    Validate that `text` follows the cross-section format:
      - Vertex lines: id x z (id unique; x,z floats;)
      - Polygon lines: name id1 id2 ...   (each id exists)
      - Blank lines and lines starting with '#' are ignored.
      - All declared vertices must be used at least once in some polygon.

    Parameters
    ----------
    text : :obj:`str`
        Multiline string containing vertex and polygon definitions.

    Returns
    -------
    :obj:`tuple` of :obj:`bool` and :obj:`list[str]` containing validation results.
        The tuple contains:
        is_valid: True if no errors were found
        errors:  List of human-readable error messages
    """
    errors: List[str] = []
    vertex_ids = set()
    used_vertex_ids = set()
    polygons_names = set()
    polygons_updated = False

    for lineno, raw in enumerate(text.splitlines(), start=1):
        # Strip off inline comments and whitespace
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue  # skip blank or comment-only lines

        parts = line.split()

        # Vertex definition: exactly three tokens, first is an integer ID
        if len(parts) == 3 and parts[0].isdigit():
            vid = int(parts[0])
            if vid in vertex_ids:
                errors.append(f"Line {lineno}: Duplicate vertex ID {vid}.")
            vertex_ids.add(vid)

            # Check coordinates
            x_str, z_str = parts[1], parts[2]
            try:
                float(x_str)
            except ValueError:
                errors.append(f"Line {lineno}: Invalid x-coordinate '{x_str}'.")
            try:
                float(z_str)
            except ValueError:
                errors.append(f"Line {lineno}: Invalid z-coordinate '{z_str}'.")

            # Check if there are polygons before vertices
            if polygons_names and polygons_updated:
                errors.append(f"Polygons {', '.join(polygons_names)} are defined before all vertices are defined.")
                polygons_updated = False

        # Polygon definition: first token is the polygon name, rest should be integer IDs
        elif len(parts) >= 2:
            name = parts[0]
            if name.isdigit():
                errors.append(f"Line {lineno}: Polygon name '{name}' cannot start with a number.")
            if name in polygons_names:
                errors.append(f"Line {lineno}: Polygon name '{name}' is not unique.")
            for id_str in parts[1:]:
                if not id_str.isdigit():
                    errors.append(
                        f"Line {lineno}: Polygon '{name}' has invalid vertex ID '{id_str}'."
                    )
                    continue
                used_vertex_ids.add(int(id_str))
            polygons_names.add(name)
            polygons_updated = True

        # Anything else is unrecognized
        else:
            errors.append(f"Line {lineno}: Unrecognized format: '{line}'.")

    # Check if there are vertices defined
    if not vertex_ids:
        errors.append("No vertices are defined")

    # Check if there are polygons defined
    if not polygons_names:
        errors.append("No polygons are defined")
    
    # Cross-check: polygons only reference existing vertices
    for vid in sorted(used_vertex_ids):
        if vid not in vertex_ids:
            errors.append(f"Polygon references undefined vertex ID {vid}.")

    # Cross-check: every vertex must be used
    unused = vertex_ids - used_vertex_ids
    if unused:
        errors.append(f"Vertices never used in any polygon: {sorted(unused)}.")

    return (not errors), errors


def validate_cross_section_topology(text: str, tol: float = 1e-8) -> Tuple[bool, List[str]]:
    """
    Check the topological validity of a cross-section defined in ``text``.

    The following rules must be satisfied for a valid cross-section:
    1. No two vertices share identical (x, z) coordinates.
    2. Inside every polygon each vertex appears **at most once**.
    3. No vertex (that is *not* one of a polygon's own vertices)
       may lie strictly inside that polygon **or** on one of its edges.
    4. Any two polygons may touch along common edges/vertices
       but must **not overlap** with non-zero area.
    5. The union of all polygons must exactly fill the overall bounding
       rectangle implied by min/max of all x and z coordinates
       (→ no gaps; no out-of-bounds leakage).

    Parameters
    ----------
    text : :obj:`str`
        Multiline string containing vertex and polygon definitions in the cross-section format.
    tol : :obj:`float`, optional
        Tolerance for area checks (default is 1e-8 km²).
        This is used to determine if two polygons overlap or if gaps exist.

    Returns
    -------
    :obj:`tuple` of :obj:`bool` and :obj:`list[str]`
    The tuple contains:
        is_topologically_valid: True if no errors were found
        errors:  List of human-readable error messages
    """
    # ------------------------------------------------------------------
    # Ensure the *format* is already correct
    # ------------------------------------------------------------------
    #ok, fmt_errors = validate_cross_section_format(text)
    #if not ok:
    #    return False, (["Input fails format validation;"] + fmt_errors)

    # ------------------------------------------------------------------
    # Parse vertices & polygons
    # ------------------------------------------------------------------
    try:
        vertices, polygons = parse_text(text)
    except Exception as exc:              # should never happen: format already validated
        return False, [f"Unexpected parse failure: {exc}"]

    id_to_coord = {vid: (x, z) for vid, x, z in vertices}
    errors: List[str] = []

    # ------------------------------------------------------------------
    # Duplicate-coordinate check
    # ------------------------------------------------------------------
    seen_coords = {}
    for vid, (x, z) in id_to_coord.items():
        coord = (x, z)
        if coord in seen_coords:
            errors.append(f"Vertices {seen_coords[coord]} and {vid} "
                          f"share identical coordinates ({x}, {z}).")
        else:
            seen_coords[coord] = vid

    # ------------------------------------------------------------------
    # Build Shapely geometry
    # ------------------------------------------------------------------
    shapely_polys = []
    for name, v_ids in polygons:        
        # Construct geometry
        coords = [id_to_coord[vid] for vid in v_ids]
        try:
            poly = Polygon(coords)
        except Exception as exc:
            errors.append(f"Polygon '{name}' could not be created: {exc}.")
            continue
        if not poly.is_valid:
            errors.append(f"Polygon '{name}' is not a valid (simple) polygon: it may be self-intersecting, malformed or have overlapping edges.")
        shapely_polys.append((name, poly, set(v_ids)))

    # Abort early if geometry itself is broken
    if errors:
        return False, errors
    
    # ------------------------------------------------------------------
    # Vertex-multiplicity inside each polygon
    # ------------------------------------------------------------------
    for name, v_ids in polygons:    
        if len(v_ids) != len(set(v_ids)):
            errors.append(f"Polygon '{name}' lists the same vertex ID twice.")

    # ------------------------------------------------------------------
    # Vertex-inside / on-edge checks
    # ------------------------------------------------------------------
    for vid, (x, z) in id_to_coord.items():
        pt = Point(x, z)
        for name, poly, vset in shapely_polys:
            if vid in vset:
                continue     # a vertex is obviously allowed on its *own* polygon
            if poly.contains(pt):
                errors.append(f"Vertex {vid} lies strictly inside polygon '{name}'.")
            elif poly.touches(pt):
                errors.append(f"Vertex {vid} lies on an edge of polygon '{name}' "
                              "(but is not an endpoint).")

    # ------------------------------------------------------------------
    # Overlap tests between polygons
    # ------------------------------------------------------------------
    n = len(shapely_polys)
    for i in range(n):
        name_i, poly_i, _ = shapely_polys[i]
        for j in range(i + 1, n):
            name_j, poly_j, _ = shapely_polys[j]
            inter = poly_i.intersection(poly_j)
            if inter.area > tol:
                errors.append(f"Polygons '{name_i}' and '{name_j}' overlap "
                              f"(area ≈ {inter.area:.3e} km²).")

    # ------------------------------------------------------------------
    # Gap / leakage check versus bounding rectangle
    # ------------------------------------------------------------------
    # Rectangle spanning *all* vertices
    xs  = [x for _, x, _ in vertices]
    zs  = [z for _, _, z in vertices]
    minx, maxx = min(xs), max(xs)
    minz, maxz = min(zs), max(zs)
    bounding = Polygon([(minx, maxz), (maxx, maxz),
                        (maxx, minz), (minx, minz)])

    # Union of all polygons
    union_poly = unary_union([poly for _, poly, _ in shapely_polys])

    # Any part of the rectangle *not* covered?
    gaps = bounding.difference(union_poly)
    if not gaps.is_empty and gaps.area > tol:
        errors.append(f"The polygons leave gap(s) totalling "
                      f"≈ {gaps.area:.3e} km² inside the bounding rectangle.")

    # Check if any polygons extend outside
    leaks = union_poly.difference(bounding)
    if not leaks.is_empty and leaks.area > tol:
        errors.append(f"The polygons extend outside the bounding rectangle "
                      f"by ≈ {leaks.area:.3e} km².")
    
    # ------------------------------------------------------------------
    # Check that the combined shape is a perfect rectangle
    # ------------------------------------------------------------------
    # Check it's a single polygon
    if not isinstance(union_poly, Polygon):
        errors.append("Combined polygons do not form a single contiguous shape (MultiPolygon detected).")
    else:
        # Compare with bounding rectangle within tolerance
        # Use symmetric difference area as a measure
        diff_area = union_poly.symmetric_difference(bounding).area
        if diff_area > tol:
            errors.append("The combined shape of polygons is not a perfect rectangle matching the bounding box.")

    # Return result    
    return (not errors), errors


def adjust_markdown_headers(md_text: str, level: int) -> str:
    r"""
    Adjusts Markdown header levels so that the top-level header corresponds to the desired highest level.

    Parameters
    ----------
    md_text : :obj:`str`
        A string containing Markdown text.
    level : :obj:`int`
        Desired highest header level (1 through 6).

    Returns
    -------
    :obj:`str`
        The Markdown text with adjusted header levels.

    Raises
    ------
    ValueError
        If `level` is not between 1 and 6, or if no headers are found.
    
    Notes
    -----
    Finds all Markdown header lines (starting with 1-6 `#` characters), determines the minimal
    header level present, computes an offset = desired_highest - current_min, and applies this
    offset to all headers. Adjusted levels are clamped to the range 1 through 6.
    """
    if not (1 <= level <= 6):
        raise ValueError(f"desired_highest must be between 1 and 6, got {level}")

    # Match lines beginning with optional whitespace + 1–6 hashes + space + rest of line
    pattern = re.compile(r'^(?P<prefix>\s*)(?P<hashes>#{1,6})(?P<suffix>\s+.*)$', re.MULTILINE)
    # Collect all existing header levels
    levels = [len(m.group('hashes')) for m in pattern.finditer(md_text)]
    if not levels:
        raise ValueError("No Markdown headers found in the input text.")

    current_min = min(levels)
    offset = level - current_min

    def _shift(m: re.Match) -> str:
        prefix = m.group('prefix')
        orig = m.group('hashes')
        suffix = m.group('suffix')
        new_level = len(orig) + offset
        # Clamp to valid Markdown header range
        new_level = max(1, min(6, new_level))
        return f"{prefix}{'#' * new_level}{suffix}"

    # Perform substitution across all header lines
    return pattern.sub(_shift, md_text)

