// Retrieve images where an object of class $class_a is NEAR an object of class $class_b.
// Params: $class_a, $class_b
// Why a graph: this requires a relationship between two specific instances of the same
// image. Plain co-occurrence of the classes (images_with_two_classes) cannot express it.
MATCH (img:Image)-[:CONTAINS]->(a:ObjectInstance)-[:IS_A]->(:Class {name: $class_a})
MATCH (img)-[:CONTAINS]->(b:ObjectInstance)-[:IS_A]->(:Class {name: $class_b})
MATCH (a)-[:NEAR]-(b)
RETURN DISTINCT img.id AS image_id
ORDER BY image_id
