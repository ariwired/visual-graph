// Retrieve objects near another object (NEAR is symmetric: match without direction).
// Params: $object_id
MATCH (:ObjectInstance {id: $object_id})-[:NEAR]-(other:ObjectInstance)-[:IS_A]->(c:Class)
RETURN DISTINCT other.id AS object_id, c.name AS class
ORDER BY object_id
