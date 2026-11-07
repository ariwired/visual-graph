// Retrieve images where an object of class $class_a is LEFT_OF an object of class $class_b.
// Params: $class_a, $class_b
MATCH (img:Image)-[:CONTAINS]->(a:ObjectInstance)-[:IS_A]->(:Class {name: $class_a})
MATCH (img)-[:CONTAINS]->(b:ObjectInstance)-[:IS_A]->(:Class {name: $class_b})
MATCH (a)-[:LEFT_OF]->(b)
RETURN DISTINCT img.id AS image_id
ORDER BY image_id
