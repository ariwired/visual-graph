# Property graph model

The model is independent of the computer-vision pipeline: it only needs an image,
individual detected objects with bounding boxes, and their classes.

```text
(:Image)-[:CONTAINS]->(:ObjectInstance)-[:IS_A]->(:Class)
(:ObjectInstance)-[:LEFT_OF|RIGHT_OF|ABOVE|BELOW|NEAR|OVERLAPS]->(:ObjectInstance)
```

## Nodes

### `Image`

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string (UUID) | yes | Unique identifier |
| `uri` | string | yes | Where the file is stored (path or URL) |
| `width` | integer | yes | Pixels |
| `height` | integer | yes | Pixels |
| `created_at` | datetime | no | Ingestion time |

### `ObjectInstance`

One concrete detected object in one image. Two people in the same photo are two
`ObjectInstance` nodes.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string (UUID) | yes | Unique identifier (globally unique, not per image) |
| `x_min`, `y_min`, `x_max`, `y_max` | float | yes | Bounding box, image coordinates (origin top-left, `y` grows downward) |
| `confidence` | float in [0, 1] | no | Absent for manually created objects |

Derived values (`center_x`, `width`, ...) are **not** stored; they are computed from the box.

### `Class`

A category such as `person` or `dog`. One node per class name, shared by all instances.

| Property | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Unique, lowercase (e.g. `person`, `traffic light`) |

## Relationships

| Type | Direction | Meaning |
|---|---|---|
| `CONTAINS` | `Image → ObjectInstance` | The object was found in the image |
| `IS_A` | `ObjectInstance → Class` | The object's category (exactly one per instance) |
| `LEFT_OF` | `A → B` | A is left of B |
| `RIGHT_OF` | `A → B` | A is right of B (inverse of `LEFT_OF`; both are stored) |
| `ABOVE` | `A → B` | A is above B |
| `BELOW` | `A → B` | A is below B (inverse of `ABOVE`; both are stored) |
| `NEAR` | `A → B` | Symmetric: stored once, queried without direction `(a)-[:NEAR]-(b)` |
| `OVERLAPS` | `A → B` | Symmetric: stored once, queried without direction |

Spatial relationships connect **object instances**, never classes or images, and
both ends must belong to the same image. Rules for each relationship are defined in
[spatial-relationships.md](spatial-relationships.md); the engine's output
(`source_id`, `type`, `target_id`) maps directly to these edges.
Spatial relationships carry no properties: everything needed to recompute them is on the nodes.

### What lives where

- **Nodes** hold intrinsic facts (identity, geometry, confidence, file info).
- **Relationships** hold only structure (membership, classification, spatial predicate).
  They are derived data and can be regenerated from the node geometry.

## Identifiers and uniqueness

- `Image.id` and `ObjectInstance.id` are application-generated UUIDs (unique constraints, see issue #4).
- `Class.name` is the natural key; `Class` nodes are created with `MERGE` so classes are not duplicated.

## Example: two people, a dog and a bicycle

```cypher
CREATE (img:Image {id: "img-1", uri: "samples/street.jpg", width: 1280, height: 720})
CREATE (p1:ObjectInstance {id: "obj-1", x_min: 100, y_min: 100, x_max: 300, y_max: 600})
CREATE (p2:ObjectInstance {id: "obj-2", x_min: 400, y_min: 120, x_max: 580, y_max: 600})
CREATE (d:ObjectInstance  {id: "obj-3", x_min: 320, y_min: 450, x_max: 420, y_max: 600})
CREATE (b:ObjectInstance  {id: "obj-4", x_min: 800, y_min: 200, x_max: 1100, y_max: 650})
MERGE (person:Class {name: "person"})
MERGE (dog:Class {name: "dog"})
MERGE (bike:Class {name: "bicycle"})
CREATE (img)-[:CONTAINS]->(p1), (img)-[:CONTAINS]->(p2), (img)-[:CONTAINS]->(d), (img)-[:CONTAINS]->(b)
CREATE (p1)-[:IS_A]->(person), (p2)-[:IS_A]->(person), (d)-[:IS_A]->(dog), (b)-[:IS_A]->(bike)
CREATE (p1)-[:LEFT_OF]->(p2), (p2)-[:RIGHT_OF]->(p1)
CREATE (p1)-[:LEFT_OF]->(b), (b)-[:RIGHT_OF]->(p1)
CREATE (d)-[:NEAR]->(p1), (d)-[:NEAR]->(p2)
CREATE (d)-[:BELOW]->(p1), (p1)-[:ABOVE]->(d)
```

## Validation against the requirements

- **Classes vs. instances**: `Class` and `ObjectInstance` are separate labels linked by `IS_A`.
- **Several objects of the same class in one image**: `obj-1` and `obj-2` are both `person`
  in `img-1`; `MATCH (:Image {id:"img-1"})-[:CONTAINS]->(o)-[:IS_A]->(:Class {name:"person"}) RETURN count(o)` returns 2.
- **Relations connect instances**: `(obj-1)-[:LEFT_OF]->(obj-2)` distinguishes the two people,
  which a class-level edge could not.
- **Structural queries**: e.g. images with a person `NEAR` a dog:

  ```cypher
  MATCH (i:Image)-[:CONTAINS]->(p)-[:IS_A]->(:Class {name:"person"}),
        (i)-[:CONTAINS]->(d)-[:IS_A]->(:Class {name:"dog"}),
        (p)-[:NEAR]-(d)
  RETURN DISTINCT i
  ```
