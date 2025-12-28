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

    "Laccolith": """# Laccolith Intrusion Cross Section

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
"""
}
