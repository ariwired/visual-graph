// Retrieve images containing two specified classes.
// Params: $class_a, $class_b
MATCH (img:Image)-[:CONTAINS]->(:ObjectInstance)-[:IS_A]->(:Class {name: $class_a})
MATCH (img)-[:CONTAINS]->(:ObjectInstance)-[:IS_A]->(:Class {name: $class_b})
RETURN DISTINCT img.id AS image_id
ORDER BY image_id
