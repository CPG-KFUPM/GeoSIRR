# Syn-rift Half-graben Cross Section

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
- Neither fault may offset or cut the post-rift units. The master and antithetic faults must terminate exactly at the unconformity surface and must not be drawn above it.
