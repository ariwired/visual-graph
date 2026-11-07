"""``python -m visual_graph.graph`` applies the database schema."""

from visual_graph.graph.connection import create_driver, verify_connection
from visual_graph.graph.schema import apply_schema


def main() -> None:
    driver = create_driver()
    try:
        verify_connection(driver)
        apply_schema(driver)
    finally:
        driver.close()
    print("Neo4j schema applied.")


if __name__ == "__main__":
    main()
