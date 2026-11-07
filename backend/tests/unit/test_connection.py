import pytest

from visual_graph.config import Settings
from visual_graph.graph.connection import MissingCredentialsError, create_driver


def test_missing_password_raises() -> None:
    settings = Settings(_env_file=None, neo4j_password=None)  # type: ignore[call-arg]
    with pytest.raises(MissingCredentialsError):
        create_driver(settings)
