// Sample scene graph created manually (no computer vision involved).
// Idempotent: uses MERGE, so it can be run repeatedly without duplicating data.
// Coordinates: origin top-left, y grows downward. Image is 1280x720.

MERGE (img:Image {id: "sample-street-1"})
  SET img.uri = "samples/street.jpg", img.width = 1280, img.height = 720

MERGE (person:Class {name: "person"})
MERGE (dog:Class {name: "dog"})
MERGE (bicycle:Class {name: "bicycle"})
MERGE (chair:Class {name: "chair"})

MERGE (o_person:ObjectInstance {id: "sample-person-1"})
  SET o_person.x_min = 100, o_person.y_min = 100, o_person.x_max = 300, o_person.y_max = 600
MERGE (o_dog:ObjectInstance {id: "sample-dog-1"})
  SET o_dog.x_min = 320, o_dog.y_min = 450, o_dog.x_max = 420, o_dog.y_max = 600
MERGE (o_bike:ObjectInstance {id: "sample-bicycle-1"})
  SET o_bike.x_min = 500, o_bike.y_min = 200, o_bike.x_max = 800, o_bike.y_max = 650
// Two chairs: several instances of the same class in one image.
MERGE (o_chair1:ObjectInstance {id: "sample-chair-1"})
  SET o_chair1.x_min = 900, o_chair1.y_min = 300, o_chair1.x_max = 1050, o_chair1.y_max = 600
MERGE (o_chair2:ObjectInstance {id: "sample-chair-2"})
  SET o_chair2.x_min = 1100, o_chair2.y_min = 320, o_chair2.x_max = 1230, o_chair2.y_max = 600

MERGE (img)-[:CONTAINS]->(o_person)
MERGE (img)-[:CONTAINS]->(o_dog)
MERGE (img)-[:CONTAINS]->(o_bike)
MERGE (img)-[:CONTAINS]->(o_chair1)
MERGE (img)-[:CONTAINS]->(o_chair2)

MERGE (o_person)-[:IS_A]->(person)
MERGE (o_dog)-[:IS_A]->(dog)
MERGE (o_bike)-[:IS_A]->(bicycle)
MERGE (o_chair1)-[:IS_A]->(chair)
MERGE (o_chair2)-[:IS_A]->(chair)

// Spatial relationships (directional ones are stored in both directions;
// NEAR is symmetric and stored once).
MERGE (o_person)-[:NEAR]->(o_dog)
MERGE (o_person)-[:LEFT_OF]->(o_bike)
MERGE (o_bike)-[:RIGHT_OF]->(o_person)
MERGE (o_dog)-[:BELOW]->(o_person)
MERGE (o_person)-[:ABOVE]->(o_dog)
MERGE (o_dog)-[:LEFT_OF]->(o_bike)
MERGE (o_bike)-[:RIGHT_OF]->(o_dog)
MERGE (o_bike)-[:NEAR]->(o_chair1)
MERGE (o_bike)-[:LEFT_OF]->(o_chair1)
MERGE (o_chair1)-[:RIGHT_OF]->(o_bike)
MERGE (o_chair1)-[:LEFT_OF]->(o_chair2)
MERGE (o_chair2)-[:RIGHT_OF]->(o_chair1)
MERGE (o_chair1)-[:NEAR]->(o_chair2)
