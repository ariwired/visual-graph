import pytest

from visual_graph.graph.connection import create_driver, verify_connection

pytestmark = pytest.mark.integration


def test_backend_can_connect_to_neo4j() -> None:
    driver = create_driver()
    try:
        verify_connection(driver)
    finally:
        driver.close()
