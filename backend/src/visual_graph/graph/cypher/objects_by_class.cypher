// Retrieve objects by class (across all images).
// Params: $class_name
MATCH (img:Image)-[:CONTAINS]->(o:ObjectInstance)-[:IS_A]->(:Class {name: $class_name})
RETURN img.id AS image_id, o.id AS object_id
ORDER BY image_id, object_id
