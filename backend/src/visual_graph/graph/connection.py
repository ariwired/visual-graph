"""Neo4j driver factory."""

from neo4j import Driver, GraphDatabase

from visual_graph.config import Settings, get_settings


class MissingCredentialsError(RuntimeError):
    """Raised when NEO4J_PASSWORD is not configured."""


def create_driver(settings: Settings | None = None) -> Driver:
    settings = settings or get_settings()
    if settings.neo4j_password is None:
        raise MissingCredentialsError(
            "NEO4J_PASSWORD is not set. Copy .env.example to .env and set it."
        )
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
    )


def verify_connection(driver: Driver) -> None:
    """Raise if the database is unreachable or credentials are wrong."""
    driver.verify_connectivity()
    with driver.session() as session:
        record = session.run("RETURN 1 AS ok").single()
        if record is None or record["ok"] != 1:
            raise RuntimeError("Unexpected response from Neo4j")
