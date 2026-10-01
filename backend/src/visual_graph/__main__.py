import uvicorn

from visual_graph.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "visual_graph.main:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )


if __name__ == "__main__":
    main()