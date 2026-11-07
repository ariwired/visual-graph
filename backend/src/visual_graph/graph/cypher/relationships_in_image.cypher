// Retrieve spatial relationships between objects of an image.
// Params: $image_id
MATCH (:Image {id: $image_id})-[:CONTAINS]->(a:ObjectInstance)
MATCH (a)-[r:LEFT_OF|RIGHT_OF|ABOVE|BELOW|NEAR|OVERLAPS]->(b:ObjectInstance)
RETURN a.id AS source, type(r) AS relationship, b.id AS target
ORDER BY source, relationship, target
