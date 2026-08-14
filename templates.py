"""
Template geological structure descriptions for quick start examples.
"""

TEMPLATES = {
    "Normal Fault": """# Normal Fault Cross Section

## Section Overview
A vertical cross-section showing a classic **normal fault** in an extensional tectonic setting.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Fault F1 (Normal Fault)
- **Location:** Surface trace at x = 20 km
- **Dip:** 60° to the east (dipping RIGHT/eastward)
- **Displacement:** 2 km vertical throw
- **Type:** Normal fault - extensional
- **Motion:** Hanging wall (EAST side - above the eastward-dipping plane) moves DOWN

### Structural Blocks
1. **Western Block (Footwall)** - 0-20 km
   - Relatively uplifted (higher stratigraphic position)
   
2. **Eastern Block (Hanging Wall)** - 20-40 km  
   - Downthrown by 2 km (layers at deeper depths)

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone and shale
- **Thickness:** 2 km

### Layer 2 (Middle)
- **Lithology:** Limestone
- **Thickness:** 2 km

### Layer 3 (Bottom - Oldest)
- **Lithology:** Basement rocks
- **Thickness:** 4 km (extends to section base)
""",

    "Thrust Fault": """# Thrust Fault Cross Section

## Section Overview
A vertical cross-section showing a **reverse fault (thrust fault)** in a compressional tectonic setting.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Fault F1 (Thrust Fault)z
- **Location:** Surface trace at x = 20 km
- **Dip:** 30° to the WEST (low-angle thrust)
- **Displacement:** 3 km vertical throw
- **Type:** Reverse fault (thrust) - compressional
- **Motion:** Hanging wall (WEST side - above the westward-dipping plane) moves UP and OVER footwall

### Structural Blocks
1. **Western Block (Hanging Wall)** - 0-20 km
   - Uplifted by ~3 km (layers at SHALLOWER depths)
   - Older rocks at surface due to thrust displacement
   
2. **Eastern Block (Footwall)** - 20-40 km
   - Relatively down (layers at DEEPER depths)
   - Baseline stratigraphic position

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone and shale
- **Thickness:** 2 km
- **Note:** May be eroded in hanging wall

### Layer 2 (Middle)
- **Lithology:** Limestone and shale
- **Thickness:** 2 km

### Layer 3 (Lower)
- **Lithology:** Sandstone
- **Thickness:** 2 km

### Layer 4 (Basement)
- **Lithology:** Crystalline basement
- **Thickness:** 2 km
""",

    "Listric Normal Fault": """# Listric Normal Fault Cross Section

## Section Overview
A vertical cross-section showing a **listric normal fault** in an extensional tectonic setting.

## Section Extent
* **Horizontal:** 0 km to 20 km
* **Vertical:** 0 km (surface) to 5 km (depth)

## Geological Features

### Fault F1 (Listric Normal Fault)
- **Location:** Surface trace at x = 8 km
- **Dip:** 60° to the east (dipping RIGHT/eastward)
- **Displacement:** 1 km vertical throw
- **Type:** Normal fault - extensional
- **Curvature** Curving eastwards, flattening to a 20° dip at the depth of 5 km. Curvature is approximated with 6 short straight segments.
- **Motion:** Hanging wall (EAST side - above the eastward-dipping plane) moves DOWN

### Structural Blocks
1. **Western Block (Footwall)** - 0-8 km
   - Relatively uplifted (higher stratigraphic position)
   
2. **Eastern Block (Hanging Wall)** - 8-20 km  
   - Downthrown by 1 km (layers at deeper depths)

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone and shale
- **Thickness:** 1 km in the footwall, thickening to 2 km in the hanging wall (due to syn-tectonic deposition).

### Layer 2 (Middle)
- **Lithology:** Limestone
- **Thickness:** 2 km

### Layer 3 (Bottom - Oldest)
- **Lithology:** Basement rocks
- **Thickness:** 2 km in the footwall, thinning to 1 km in the hanging wall to accommodate fault displacement and section base.
""",

    "Horst and Graben": """# Horst and Graben Cross Section

## Section Overview
A vertical cross-section showing a classic **horst and graben** structure with central uplifted block flanked by downthrown blocks.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Fault F1 (Western Boundary Fault)
- **Location:** x = 10 km
- **Dip:** 60° westward (dipping AWAY from horst)
- **Throw:** 2 km vertical displacement
- **Type:** Normal fault

### Fault F2 (Eastern Boundary Fault)
- **Location:** x = 30 km
- **Dip:** 60° eastward (dipping AWAY from horst)
- **Throw:** 2 km vertical displacement
- **Type:** Normal fault

### Structural Blocks
1. **Western Graben** - 0-10 km
   - Downthrown block

2. **Central Horst** - 10-30 km
   - Uplifted block (relatively higher)
   - Width: 20 km

3. **Eastern Graben** - 30-40 km
   - Downthrown block

## Stratigraphic Layers

### Layer 1 (Top)
- **Lithology:** Sandstone and shale
- **Thickness:** 1.5 km

### Layer 2 (Middle)
- **Lithology:** Limestone
- **Thickness:** 1.5 km

### Layer 3 (Basement)
- **Lithology:** Metamorphic rocks
- **Thickness:** 5 km
""",

    "Anticline": """# Anticline Cross Section

## Section Overview
A vertical cross-section showing a symmetric **anticline** fold structure.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Fold Structure
- **Type:** Anticline (upward-arching fold)
- **Symmetry:** Symmetric
- **Axial trace:** x = 20 km (center)
- **Amplitude:** 2 km (from crest to baseline)
- **Wavelength:** ~20 km (half-wavelength from axis to limb)

### Fold Geometry
- Layers arch upward at center (x = 20 km)
- Layers dip away from axis on both sides
- Western limb: Layers dip westward
- Eastern limb: Layers dip eastward

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone
- **Thickness:** 1.5 km
- **Folded:** Follows anticline geometry

### Layer 2 (Upper Middle)
- **Lithology:** Shale
- **Thickness:** 1.5 km
- **Folded:** Follows anticline geometry

### Layer 3 (Lower Middle)
- **Lithology:** Limestone
- **Thickness:** 2 km
- **Folded:** Follows anticline geometry

### Layer 4 (Basement)
- **Lithology:** Crystalline basement
- **Thickness:** 3 km
- **Folded:** Follows anticline geometry at top
""",

    "Syncline": """# Syncline Cross Section

## Section Overview
A vertical cross-section showing a symmetric **syncline** fold structure.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Fold Structure
- **Type:** Syncline (downward-arching fold)
- **Symmetry:** Symmetric
- **Axial trace:** x = 20 km (center)
- **Amplitude:** 2 km (from trough to baseline)
- **Wavelength:** ~20 km (half-wavelength from axis to limb)

### Fold Geometry
- Layers arch downward at center (x = 20 km)
- Layers dip toward axis on both sides
- Western limb: Layers dip eastward (toward axis)
- Eastern limb: Layers dip westward (toward axis)
- Younger rocks preserved in trough

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone
- **Thickness:** 1.5 km
- **Folded:** Follows syncline geometry

### Layer 2 (Upper Middle)
- **Lithology:** Shale
- **Thickness:** 1.5 km
- **Folded:** Follows syncline geometry

### Layer 3 (Lower Middle)
- **Lithology:** Limestone
- **Thickness:** 2 km
- **Folded:** Follows syncline geometry

### Layer 4 (Basement)
- **Lithology:** Crystalline basement
- **Thickness:** 3 km
- **Folded:** Follows syncline geometry at top
""",

    "Simple Layers": """# Simple Layered Cross Section

## Section Overview
A simple vertical cross-section showing horizontal sedimentary layers with no deformation.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

No faults or folds - simple layer-cake stratigraphy.

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone and shale
- **Thickness:** 2 km
- **Top:** 0 km (surface)
- **Base:** 2 km

### Layer 2 (Middle)
- **Lithology:** Limestone
- **Thickness:** 2 km
- **Top:** 2 km
- **Base:** 4 km

### Layer 3 (Lower)
- **Lithology:** Shale
- **Thickness:** 2 km
- **Top:** 4 km
- **Base:** 6 km

### Layer 4 (Basement)
- **Lithology:** Crystalline basement rocks
- **Thickness:** 2 km
- **Top:** 6 km
- **Base:** 8 km (section base)
""",

    "Salt Diapir": """# Salt Diapir Cross Section

## Section Overview
A vertical cross-section showing a **mushroom-shaped salt diapir** intruding through sedimentary layers.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Salt Diapir
- **Type:** Mushroom-shaped salt intrusion
- **Position:** Center of section (x = 20 km)
- **Shape:** Dome with overhanging edges (mushroom cap)
- **Intrusion depth:** Rises from basement to near surface
- **Does NOT breach surface:** Top at ~0.5 km depth

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone and shale
- **Thickness:** 2 km
- **Deformed:** Uplifted and pierced by diapir

### Layer 2 (Middle-Upper)
- **Lithology:** Limestone
- **Thickness:** 2 km
- **Deformed:** Strongly deformed by salt intrusion

### Layer 3 (Middle-Lower)
- **Lithology:** Shale
- **Thickness:** 2 km
- **Deformed:** Deformed by rising salt

### Layer 4 (Source Layer)
- **Lithology:** Salt layer (source of diapir)
- **Thickness:** 2 km
- **Note:** Diapir rises from this layer
""",

    "Vertical Dike": """# Tilted Dike Cross Section

## Section Overview
A vertical cross-section showing a **tilted igneous dike** cutting through sedimentary layers at a slight angle.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Dike Intrusion
- **Type:** Tilted igneous dike (sub-vertical)
- **Position:** Approximately x = 18-22 km (with slight tilt)
- **Orientation:** Dips ~80° to the east (tilted 10° from vertical)
- **Width:** ~1.5-2 km (thicker than typical dykes for visibility)
- **Extent:** Cuts through all layers from basement to near-surface
- **Geometry:** 
  - Bottom (8 km depth): Centered at x = 18 km
  - Top (near surface): Offset to x = 22 km
  - Irregular width: Varies slightly (1.5-2 km) - not perfectly uniform
- **Lithology:** Basalt or diabase
- **Note:** Slight tilt and variable thickness create more realistic appearance

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone
- **Thickness:** 2 km
- **Note:** Cut by dike

### Layer 2 (Middle-Upper)
- **Lithology:** Limestone
- **Thickness:** 2 km
- **Note:** Cut by dike

### Layer 3 (Middle-Lower)
- **Lithology:** Shale
- **Thickness:** 2 km
- **Note:** Cut by dike

### Layer 4 (Basement)
- **Lithology:** Crystalline basement
- **Thickness:** 2 km
- **Note:** Source region for dike intrusion
""",

    "Horizontal Sill": """# Horizontal Sill Cross Section

## Section Overview
A vertical cross-section showing a **horizontal igneous sill** intruded between sedimentary layers.

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Sill Intrusion
- **Type:** Horizontal sill (concordant intrusion)
- **Position:** Between Layer 2 and Layer 3 (at 4 km depth)
- **Orientation:** Horizontal (parallel to bedding)
- **Thickness:** ~0.3-0.5 km
- **Extent:** Extends across most of section (5-35 km)
- **Lithology:** Dolerite or diabase

## Stratigraphic Layers

### Layer 1 (Top - Youngest)
- **Lithology:** Sandstone
- **Thickness:** 2 km

### Layer 2 (Middle-Upper)
- **Lithology:** Limestone
- **Thickness:** 2 km
- **Note:** Sill intrudes below this layer

### Sill (Intrusion)
- **Lithology:** Igneous sill
- **Thickness:** 0.4 km
- **Position:** 4 km depth

### Layer 3 (Middle-Lower)
- **Lithology:** Shale
- **Thickness:** 2 km
- **Note:** Sill intrudes above this layer

### Layer 4 (Basement)
- **Lithology:** Crystalline basement
- **Thickness:** ~3.6 km
""",

    "Laccolith Dyke": """# Laccolith Dyke Intrusion Cross Section

## Section Extent
* **Horizontal:** 0 km to 40 km
* **Vertical:** 0 km (surface) to 8 km (depth)

## Geological Features

### Feeder Dyke
- **Width:** 0.8 km
- **Dip:** 75° east
- **Location:** Bottom at x=19 km (depth 8 km), top at x=22 km (depth 5 km)
- **Lithology:** Basalt

### Laccolith Sill
- **Type:** Lens-shaped intrusion at top of shale layer (5 km depth)
- **Peak:** x=22 km, thickness 1.2 km
- **West side:** Gradual taper from x=15 km to x=22 km
- **East side:** Steeper taper from x=22 km to x=26 km
- **Edges:** Taper smoothly to zero thickness
- **Top:** Smooth dome shape
- **Lithology:** Diorite

### Layer Deformation
- Layers 1 and 2 bend upward over laccolith, maintaining constant 2 km thickness
- Maximum uplift ~1.2 km at x=22 km
- Layers return to flat beyond x=15 km (west) and x=26 km (east)

## Stratigraphic Layers
- **Layer 1 (Sandstone):** 2 km thick, deformed over laccolith
- **Layer 2 (Limestone):** 2 km thick, deformed over laccolith
- **Layer 3 (Shale):** 2.5 km thick, laccolith intrudes at top
- **Layer 4 (Basement):** 2.5 km thick, flat
""",

    "Prograding Delta": """# Prograding Delta Cross Section

## Section Overview
A West-East cross-section showing an overall **progradation of a delta** with clear cliniform geometries.

## Section Extent
* **Horizontal:** 0 km to 15 km (W-E)
* **Vertical:** 0 km (surface) to 4 km (depth)

## Geological Features

### Progradational System
- **Type:** Deltaic progradation
- **Direction:** West to East
- **Geometry:** Sigmoidal/Cliniform layers dipping eastward
- **Overall Geometry:** Layers pinch out towards the East

## Stratigraphic Layers

### Layer 1-8 (Deltaic Sequence)
- **Count:** 8 distinct layers above basement
- **Western Thickness:**
  - Bottom layer: ~0.2 km thick
  - Thickness increases upward: Top layers reach ~0.5 km thick
  - Total sediment thickness in West: ~2-3 km
- **Eastern Geometry:** Layers thin and pinch out towards the East
- **Cliniforms:** Layers show sigmoidal dipping geometry (clinoforms) indicating progradation

### Basement
- **Lithology:** Crystalline basement
- **Western Thickness:** 1 km
- **Eastern Thickness:** 0.2 km
- **Geometry:** Thins from West to East
""",
    "Domino-style Listric Rift": """# Domino-style Listric Rift Cross Section

## Section overview

Create a simplified vertical cross-section of an asymmetric extensional rift like a Basin-and-Range tilted-block system. It must contain one master listric normal fault, five synthetic listric normal-fault splays, and two antithetic normal faults. The six east-dipping listric faults form a linked fault fan above the master detachment. The fault-bounded upper-plate blocks are rotated, producing a repeated sawtooth surface of ranges and half-graben basins. The two antithetic faults occur only in the broad basin on the right.

This is a structural-block diagram, not a stratigraphic section. Include only crystalline basement and air. Do not add sedimentary layers, basin fill, water, an unconformity, labels, arrows, or text inscriptions. All basement pieces must use the same base name so that they receive the same automatic color; the faults are visible as shared black polygon boundaries.

## Section extent and required polygon names

- Horizontal extent: x = 0 to 70 km.
- Vertical extent: z = 0 km at the rectangular top to z = -10 km at the section base.
- The union of all polygons must exactly fill this 70 by 10 km rectangle, without gaps or overlaps.
- Use exactly two polygon base names: `air` and `basement`.
- Use one continuous `air` polygon above the irregular land surface.
- Split the rock into fault-bounded polygons named `basement^lower_plate`, `basement^block_1`, `basement^block_2`, and so on. Every rock polygon must retain the `basement` base name.

## Topographic surface and air layer

- The rectangular top at z = 0 is the top of the air layer; the irregular air-basement boundary below it is the land surface.
- Far-left basement plateau: approximately z = -1.2 km from x = 0 to the master-fault breakaway at x = 8 km.
- At the breakaway, show the largest fault scarp: the footwall surface is near z = -1.2 km and the adjacent hanging-wall surface is near z = -2.8 km.
- From x = 8 to about 51 km, make five successive rotated range blocks. Each block top rises gently to the right, then steps downward across the next east-dipping normal fault. This repeated asymmetric sawtooth geometry is essential: gentle rightward-rising block tops alternate with steep fault scarps.
- Put approximate synthetic-fault surface traces at x = 18, 28, 37, 45, and 51 km. Each hanging wall on the right is downthrown by about 0.7-1.0 km at the surface relative to the footwall on the left.
- Keep the central sawtooth surface mostly between z = -2.2 and z = -3.6 km. The left breakaway plateau and far-right plateau must be distinctly higher than the central rift floor.
- From x = 51 to 63 km, form one broad, low half-graben basin with a gently irregular floor near z = -3.2 to -4.0 km. The two antithetic faults cut this basin.
- East of x = 63 km, raise the basement surface relatively steeply to a far-right plateau near z = -1.4 km, then keep it approximately flat to x = 70 km.
- The bottom edge of the single `air` polygon must follow every plateau, tilted block top, fault scarp, basin floor, and right-side rise. Do not smooth away the fault-scarp steps.

## Six linked east-dipping listric normal faults

Treat the following as a hard count: there must be exactly SIX east-dipping listric normal faults in total, F1 through F6. F1 is the master fault and F2-F6 are five synthetic splays. Do not add other east-dipping faults.

### F1: master listric fault and basal detachment

- F1 begins at the breakaway on the land surface near (8, -1.2) km.
- It dips steeply right/east at about 65 degrees near the surface, is concave upward, and progressively flattens with depth into a low-angle detachment.
- Guide its trace through approximately (8.5, -2.5), (10, -4.0), (13, -5.5), (18, -7.0), (25, -8.0), (34, -8.8), (43, -9.4), (50, -9.7), (53.5, -9.85), (54.5, -9.90), and (58, -9.96) km.
- Continue F1 all the way to the section base near (60, -10.0) km. It must not stop within the basement.
- Approximate F1 with at least 12 ordered vertices, with progressively smaller changes in depth relative to horizontal distance, so the concave-up flattening is smooth rather than angular.
- F1 separates `basement^lower_plate` below and to the left from all rotated upper-plate blocks above and to the right.

### F2-F6: synthetic listric splays

- F2, F3, F4, F5, and F6 all dip right/east, have normal displacement, curve concave upward, flatten downward, and terminate exactly against F1. They must not cross F1 and must not continue below it.
- Their approximate surface-trace and F1-junction pairs are:
  - F2: surface near (18, -2.3), joining F1 near (25, -8.0).
  - F3: surface near (28, -2.5), joining F1 near (34, -8.8).
  - F4: surface near (37, -2.6), joining F1 near (43, -9.4).
  - F5: surface near (45, -2.8), joining F1 near (50, -9.7).
  - F6: surface near (51, -3.0), joining F1 near (53.5, -9.85).
- Use at least 8 ordered vertices along each of F2-F6. Near the surface, successive vertices should move mostly downward with little rightward shift; toward F1, they should move increasingly rightward with less downward shift. This is required to make every splay smoothly listric.
- Make each junction a single shared vertex used by F1 and the relevant splay boundaries. Do not leave tiny gaps, overlaps, or crossing lines at the junctions.
- The upper-plate basement between successive faults forms five clearly rotated domino blocks. Their land-surface tops rise gently toward the right and their internal fault boundaries remain continuous from the surface to F1.

## Two right-side antithetic faults

- Add exactly TWO antithetic normal faults, A1 and A2, in the broad half-graben to the right of F6. Do not add antithetic faults elsewhere.
- A1 starts on the basin floor near x = 57 km. A2 starts farther right near x = 62 km.
- Both faults dip left/west, opposite to F1-F6. For these west-dipping normal faults, the hanging wall is on the left and is downthrown relative to the footwall on the right.
- Give each antithetic fault a smaller surface throw than the synthetic faults, about 0.3-0.5 km. Show this as a small upward step when crossing each antithetic fault from left to right.
- Curve each trace gently and use at least 6 ordered vertices. A1 must terminate against F1 near (54.5, -9.90) and A2 near (58, -9.96). Thus A1 shifts about 2.5 km left and A2 about 4 km left from surface to termination; neither trace may be vertical or dip right. They must share their terminal vertices with F1, must not cross F1, and must not reach the section base independently.
- Keep A1 and A2 spatially separate from F6 and from each other. Together they subdivide only the rightmost hanging-wall basin into three smaller basement polygons.

## Topology and visual priorities

- Faults are not separate thin polygons. Represent each fault as the same ordered chain of shared vertices along the boundaries of its two adjacent `basement^...` polygons.
- Every fault must be visible from its land-surface trace to its specified junction or base termination. Adjacent polygons must reuse all intermediate fault vertices, not merely the two endpoints.
- Use separate vertices for the top and bottom of each surface scarp; identical coordinate pairs are forbidden.
- Keep all polygons simple and clockwise, and use every declared vertex in at least one polygon.
- Visual priority, in order: (1) exactly six smooth, linked east-dipping listric faults; (2) exactly two west-dipping antithetic faults on the right; (3) the repeated tilted-block sawtooth topography; (4) the high left and right plateaus and lower central rift basin; (5) complete rectangular coverage by one air unit and fault-split basement.
""",

    "Syn-rift Half-graben": """# Syn-rift Half-graben Cross Section

## Section overview

A vertical geological cross-section through an asymmetric syn-rift half-graben. The section must show the geometric and temporal relationships among pre-rift stratigraphy, a listric master normal fault, an antithetic fault, syn-rift growth strata, an angular unconformity, and post-rift drape units. The master fault and antithetic fault must be clearly represented as single, continuous fault surfaces, with vertices aligned along each fault so that the fault traces are unambiguous.

## Section extent

- Horizontal extent: 0 to 40 km.
- Vertical extent: z = 0 km at the surface to z = 10 km (depth) at the section base.
- The complete result must fill this rectangular extent.
- Do not include air, water, or topography.
- Use a single base name for each stratigraphic unit and express lateral variations in thickness by the unit geometry.
- When a unit is divided into disconnected polygon parts by a fault, retain its base name and append one descriptive suffix after a single `^`, for example `prerift_upper^footwall`, `prerift_upper^proximal_hangingwall`, and `prerift_upper^distal_hangingwall`. Do not invent alternative base names for parts of the same unit.

## Required polygon names

Use these exact base names:

- `postrift_upper`
- `postrift_lower`
- `synrift_upper`
- `synrift_middle`
- `synrift_lower`
- `prerift_upper`
- `prerift_middle`
- `prerift_lower`
- `basement`

## Pre-rift succession

- Place crystalline `basement` at the bottom of the section.
- Above basement, include three initially continuous pre-rift units, in ascending order: `prerift_lower`, `prerift_middle`, and `prerift_upper`.
- The pre-rift units must be offset and rotated by the syn-rift faults.
- Preserve their stratigraphic order on every side of each fault.
- In the western footwall, keep the pre-rift horizons approximately planar and gently dipping to emphasize the contrast with the rotated hanging-wall rollover.
- Where pre-rift units are cut by faults, represent footwall and hanging-wall parts as separate polygons using the `^suffix` convention (for example, `prerift_middle^footwall` and `prerift_middle^hangingwall`).

## Master fault and rollover

- Include one major east-dipping listric normal fault bounding the half-graben.
- The master fault must terminate upward at the angular unconformity near x = 12 km; it must not cut either post-rift unit.
- With increasing depth, curve the fault eastward and progressively reduce its dip, reaching the section base near x = 25 km.
- Represent the curved fault with several connected straight segments and shared vertices, but as a single continuous surface. Ensure that vertices along this fault are shared by adjacent polygons so that the fault alignment is clearly visible through the units.
- Show approximately 2 km of normal-fault vertical throw in the pre-rift marker horizons, measured at mid-section (for example near x = 20 km).
- The eastern hanging wall is downthrown relative to the western footwall.
- In the hanging wall, bend and rotate the pre-rift succession into a rollover anticline adjacent to the concave-up master fault. The rollover geometry must remain consistent with normal displacement and must not create overlaps or gaps. The rollover should be centered between x ≈ 18-24 km and z ≈ 4-7 km.
- Where syn-rift and pre-rift units are cut by the master fault, split them into footwall and hanging-wall polygons using the `^suffix` convention, and keep their contacts on either side of the fault aligned with the fault vertices.

## Antithetic fault

- Include one west-dipping antithetic normal fault within the master-fault hanging wall.
- Start it at the angular unconformity near x = 30 km.
- Curve or incline it westward with depth and terminate it against the master fault near z = 7 km; it must not cross the master fault.
- Give it a smaller displacement than the master fault (vertical throw on pre-rift horizons should be ≤ 1 km).
- It must offset the pre-rift and lower syn-rift succession consistently, but it must not cut the post-rift units. Ensure the antithetic fault is a single continuous surface with aligned vertices, and that only the polygons below the unconformity are split by this fault using the `^suffix` convention.

## Syn-rift growth succession

- Add three syn-rift growth units above the faulted pre-rift succession, in ascending order: `synrift_lower`, `synrift_middle`, and `synrift_upper`.
- Each syn-rift unit must thicken toward the master fault in the hanging wall and thin away from it toward the east.
- Show progressive decrease in deformation upward: `synrift_lower` is the most tilted and most strongly offset, `synrift_middle` is less deformed, and `synrift_upper` is only gently deformed. Explicitly keep `synrift_upper` nearly parallel to the angular unconformity.
- The growth units must onlap the rotating hanging-wall succession where appropriate while preserving complete polygon coverage. Onlap surfaces should be drawn so that strata terminate against older units without gaps or overlaps.
- Where syn-rift units are divided by the master or antithetic faults, represent their parts as separate polygons with `^footwall`, `^proximal_hangingwall`, or `^distal_hangingwall` suffixes, and keep their boundaries aligned with the fault segments.

## Angular unconformity and post-rift succession

- Place a laterally continuous angular unconformity at approximately z = 2 km as a single, continuous polygon boundary extending from x = 0 to x = 40 km.
- The unconformity must truncate the master fault, antithetic fault, rollover structure, tilted pre-rift units, and deformed syn-rift units. No fault or older unit may cross this surface. The unconformity line must be drawn as a single polygon boundary shared by all units above and below it.
- Above it, add two laterally continuous, undeformed, approximately horizontal drape units: `postrift_lower` below `postrift_upper`. Both post-rift units must be single polygons that are planar to very gently dipping and uniform across the whole section.
- Neither fault may offset or cut the post-rift units. The master and antithetic faults must terminate exactly at the unconformity surface and must not be drawn above it."""
}
