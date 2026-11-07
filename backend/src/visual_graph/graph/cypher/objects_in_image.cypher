// Retrieve all objects contained in an image.
// Params: $image_id
MATCH (:Image {id: $image_id})-[:CONTAINS]->(o:ObjectInstance)-[:IS_A]->(c:Class)
RETURN o.id AS object_id, c.name AS class
ORDER BY object_id
