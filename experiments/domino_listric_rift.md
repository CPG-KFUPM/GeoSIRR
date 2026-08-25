# Domino-style Listric Rift Cross Section

## Section overview

A simplified vertical cross-section of an asymmetric extensional rift like a Basin-and-Range tilted-block system. It must contain one master listric normal fault, five synthetic listric normal-fault splays, and two antithetic normal faults. The six east-dipping listric faults form a linked fault fan above the master detachment. The fault-bounded upper-plate blocks are rotated, producing a repeated sawtooth surface of ranges and half-graben basins. The two antithetic faults occur only in the broad basin on the right.

This is a structural-block diagram containing crystalline basement, local syn-rift sedimentary basin fill, and air. Do not add water, a regional sedimentary cover, an unconformity, labels, arrows, or text inscriptions. All basement pieces must use the same base name so that they receive the same automatic color. All sediment wedges must likewise share one base name. The faults are visible as shared black polygon boundaries.

## Section extent and required polygon names

- Horizontal extent: x = 0 to 70 km.
- Vertical extent: z = 0 km at the rectangular top to z = -10 km at the section base.
- The union of all polygons must exactly fill this 70 by 10 km rectangle, without gaps or overlaps.
- Use exactly three polygon base names: `air`, `basement`, and `basin_fill`.
- Use one continuous `air` polygon above the irregular land surface.
- Split the rock into fault-bounded polygons named `basement^lower_plate`, `basement^block_1`, `basement^block_2`, and so on. Every rock polygon must retain the `basement` base name.
- Represent the local sediment accumulations as separate polygons named `basin_fill^basin_1`, `basin_fill^basin_2`, and so on. They are disconnected parts of the same sedimentary unit and must retain the `basin_fill` base name so that all receive one color.

## Topographic surface and air layer

- The rectangular top at z = 0 is the top of the air layer; the irregular air-basement boundary below it is the land surface.
- Far-left basement plateau: approximately z = -1.2 km from x = 0 to the master-fault breakaway at x = 8 km.
- At the breakaway, show the largest fault scarp: the footwall surface is near z = -1.2 km and the adjacent hanging-wall surface is near z = -2.8 km.
- From x = 8 to about 51 km, make five successive rotated range blocks. Each block top rises gently to the right, then steps downward across the next east-dipping normal fault. This repeated asymmetric sawtooth geometry is essential: gentle rightward-rising block tops alternate with steep fault scarps.
- Put approximate synthetic-fault surface traces at x = 18, 28, 37, 45, and 51 km. Each hanging wall on the right is downthrown by about 0.7-1.0 km at the surface relative to the footwall on the left.
- Keep the central sawtooth surface mostly between z = -2.2 and z = -3.6 km. The left breakaway plateau and far-right plateau must be distinctly higher than the central rift floor.
- From x = 51 to 63 km, form one broad, low half-graben basin whose sediment surface consists of horizontal, fault-offset segments near z = -3.2 to -4.0 km. The two antithetic faults cut this basin.
- East of x = 63 km, raise the basement surface relatively steeply to a far-right plateau near z = -1.4 km, then keep it approximately flat to x = 70 km.
- The land surface alternates between the top of sedimentary fill in the half-graben lows and exposed basement on the tilted range crests. The bottom edge of the single `air` polygon must follow every plateau, sediment surface, exposed block top, fault scarp, and right-side rise. Do not smooth away the fault-scarp steps.

## Horizontal syn-rift sedimentary basin fill

- Add exactly SIX local, wedge-shaped syn-rift sediment accumulations: one on the down-dip left side of each rotated hanging-wall block associated with F1 through F6. Do not create a laterally continuous sedimentary blanket across the ranges.
- Each wedge rests directly on the tilted basement top, is thickest beside the normal fault on its left, and thins progressively to the right until it pinches out onto the crest of the tilted basement block. The basement-sediment contact must rise gently rightward, consistent with block rotation. Create the wedge geometry entirely with this inclined basal contact; do not incline the top of the sediment with the rotated basement block.
- Sediment thickness beside F1-F5 should be approximately 1.0-1.5 km. Make every wedge visually prominent at the full-section scale rather than a thin sliver. Each of the first five wedges should pinch out before reaching the next synthetic fault, leaving a short interval of exposed basement at the up-dip right-hand range crest.
- Place the approximate rightward pinchouts of `basin_fill^basin_1` through `basin_fill^basin_5` near x = 16, 26, 35, 43, and 49.5 km, respectively. Use at least one intermediate shaping vertex along the basal contact so that each wedge follows the tilted basement rather than becoming a simple triangle.
- The sediment-air contact at the top of every uninterrupted basin-fill polygon must be exactly horizontal and parallel to sea level at z = 0. All vertices along that top contact must have the same z coordinate. Different half-grabens may have different horizontal top elevations, and faults may produce vertical steps between adjacent sediment polygons, but no sediment top segment may slope or follow the rotated basement.
- At the left edge of each wedge, the top is the downthrown land surface and its base meets a deeper vertex on the corresponding fault. Therefore, the upper segment of each normal fault forms the steep left boundary of its basin fill and remains visibly continuous into basement below.
- The sixth accumulation, `basin_fill^basin_6`, occupies the broad half-graben from the F6 hanging wall near x = 51 km to the rising eastern margin near x = 63 km. It should be approximately 1.2-1.8 km thick, remain clearly visible across all three antithetically faulted parts, and not cover the high far-right plateau.
- A1 and A2 cut completely through the sixth sediment accumulation before continuing through basement to F1. Split this fill into `basin_fill^basin_6_west`, `basin_fill^basin_6_centre`, and `basin_fill^basin_6_east`; reuse every A1 and A2 vertex that lies within the sediment in the adjacent fill polygons. Preserve the smaller normal offsets across both antithetic faults. Keep the top of each of these three polygons horizontal; represent any surface displacement as a vertical step at the fault, never as an inclined sediment top.
- Basin fill must never occupy the lower plate, cover the left breakaway plateau, or cover the exposed crests of the five central tilted blocks. Do not add internal sediment layers: the reference shows one basin-fill unit repeated in separate half-grabens.

## Six linked east-dipping listric normal faults

Treat the following as a hard count: there must be exactly SIX east-dipping listric normal faults in total, F1 through F6. F1 is the master fault and F2-F6 are five synthetic splays. Do not add other east-dipping faults.

### F1: master listric fault and basal detachment

- F1 begins at the breakaway on the land surface near (8, -1.2) km.
- It dips steeply right/east at about 65 degrees near the surface, is concave upward, and progressively flattens with depth into a low-angle detachment.
- Guide its trace through approximately (8.5, -2.5), (10, -4.0), (13, -5.5), (18, -7.0), (25, -8.0), (34, -8.8), (43, -9.4), (50, -9.7), (53.5, -9.85), (54.5, -9.90), and (58, -9.96) km.
- Continue F1 all the way to the section base near (60, -10.0) km. It must not stop within the basement.
- Approximate F1 with at least 12 ordered vertices, with progressively smaller changes in depth relative to horizontal distance, so the concave-up flattening is smooth rather than angular.
- F1 separates `basement^lower_plate` below and to the left from all rotated upper-plate blocks and basin fill above and to the right.

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
- The upper-plate basement between successive faults forms five clearly rotated domino blocks. Each basement top rises gently toward the right beneath a sediment wedge, then becomes exposed near the right-hand crest. Every internal fault boundary remains continuous from the land surface, through any sediment beside it, through basement, and down to F1.

## Two right-side antithetic faults

- Add exactly TWO antithetic normal faults, A1 and A2, in the broad half-graben to the right of F6. Do not add antithetic faults elsewhere.
- A1 starts on the basin floor near x = 57 km. A2 starts farther right near x = 62 km.
- Both faults dip left/west, opposite to F1-F6. For these west-dipping normal faults, the hanging wall is on the left and is downthrown relative to the footwall on the right.
- Give each antithetic fault a smaller surface throw than the synthetic faults, about 0.3-0.5 km. Show this as a small upward step when crossing each antithetic fault from left to right.
- Curve each trace gently and use at least 6 ordered vertices. A1 must terminate against F1 near (54.5, -9.90) and A2 near (58, -9.96). Thus A1 shifts about 2.5 km left and A2 about 4 km left from surface to termination; neither trace may be vertical or dip right. They must share their terminal vertices with F1, must not cross F1, and must not reach the section base independently.
- Keep A1 and A2 spatially separate from F6 and from each other. Together they subdivide the rightmost hanging-wall basin into three basin-fill polygons and three underlying basement polygons.

## Topology and visual priorities

- Faults are not separate thin polygons. Represent each fault as the same ordered chain of shared vertices along the boundaries of its two adjacent `basement^...` polygons.
- Where a fault passes through or bounds basin fill, its upper vertices must instead be shared by the adjacent `basin_fill^...` and/or `basement^...` polygons as required. Every fault must remain visible from its land-surface trace to its specified junction or base termination. Adjacent polygons must reuse all intermediate fault vertices, not merely the two endpoints.
- Use separate vertices for the top and bottom of each surface scarp; identical coordinate pairs are forbidden.
- Keep all polygons simple and clockwise, and use every declared vertex in at least one polygon.
- Visual priority, in order: (1) exactly six smooth, linked east-dipping listric faults; (2) exactly two west-dipping antithetic faults on the right; (3) six wedge-shaped sediment fills with horizontal, sea-level-parallel top contacts that thicken leftward only because their basal contacts are inclined; (4) the repeated tilted-block sawtooth topography; (5) the high left and right plateaus and lower central rift basin; (6) complete rectangular coverage by air, basin fill, and fault-split basement.
