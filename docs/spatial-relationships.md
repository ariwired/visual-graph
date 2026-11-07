# Spatial relationships

Relationships are computed from axis-aligned bounding boxes using explicit
geometric rules (`backend/src/visual_graph/spatial/`). They do not depend on
Neo4j or on any particular detector.

## Bounding box

`BoundingBox(x_min, y_min, x_max, y_max)` in image coordinates (origin top-left,
`y` grows downward). Boxes must have finite numeric coordinates and strictly
positive width and height; zero-area, inverted or malformed boxes raise
`InvalidBoundingBoxError`.

Derived: `width = x_max - x_min`, `height = y_max - y_min`, `area = width * height`,
`center_x = (x_min + x_max) / 2`, `center_y = (y_min + y_max) / 2`.

## Rules (for the ordered pair `A, B`)

| Relation | Definition |
|---|---|
| `LEFT_OF` | `B.center_x - A.center_x > directional_margin * max(A.width, B.width)` |
| `RIGHT_OF` | `B LEFT_OF A` |
| `ABOVE` | `B.center_y - A.center_y > directional_margin * max(A.height, B.height)` |
| `BELOW` | `B ABOVE A` |
| `OVERLAPS` | `area(A ∩ B) > 0` and `area(A ∩ B) > min_overlap_ratio * min(A.area, B.area)` |
| `NEAR` | `gap(A, B) <= near_ratio * max(A.width, A.height, B.width, B.height)` |

`gap(A, B) = hypot(dx, dy)` with `dx = max(A.x_min - B.x_max, B.x_min - A.x_max, 0)` and
`dy` analogous: the Euclidean distance between the closest edges (`0` when the boxes touch or overlap).

Notes:

- Boxes that only touch along an edge or corner do **not** overlap (intersection area is 0) but are `NEAR`.
- `NEAR` uses an inclusive threshold and is relative to object size, so it is independent of image resolution.
- Directional rules compare centers, so a diagonal pair can satisfy both a horizontal and a vertical relation.

## Configuration (`SpatialConfig`)

| Field | Default | Meaning |
|---|---|---|
| `directional_margin` | `0.0` | Required center offset as a fraction of the larger box dimension |
| `near_ratio` | `0.5` | Maximum gap as a fraction of the larger box's longest side |
| `min_overlap_ratio` | `0.0` | Minimum intersection as a fraction of the smaller box's area (`[0, 1)`) |

## Engine

`compute_relationships(objects, config)` evaluates all pairs of distinct objects:

- an object is never related to itself; duplicate ids raise `ValueError`;
- directional relations are emitted per ordered pair;
- `NEAR` and `OVERLAPS` are symmetric and emitted once per unordered pair (from the object listed first);
- output order depends only on input order, so equal inputs give equal outputs.
