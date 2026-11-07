<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/Neo4j-4581C3?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j">
<img src="https://img.shields.io/badge/Cypher-018BFF?style=for-the-badge" alt="Cypher">
<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
<img src="https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white" alt="Vue.js">
<img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
<img src="https://img.shields.io/badge/Cytoscape.js-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="Cytoscape.js">
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">

# VisualGraph

Graph-based visual search and scene exploration using computer vision and Neo4j.

## About

VisualGraph is a project for representing visual scenes as graphs. The initial idea is to detect objects in images, derive spatial relationships between them, and store this information in a Neo4j graph database.

For example, an image may be represented as:

```text
Image
 ├── CONTAINS → Person
 ├── CONTAINS → Dog
 └── CONTAINS → Bicycle

Person ── NEAR ──→ Dog
Person ── LEFT_OF ──→ Bicycle
```

This graph representation can then be explored and queried using Cypher.

## Initial Proposal

The first version of the project will focus on:

* object detection in images;
* extraction of bounding boxes and object classes;
* generation of spatial relationships between detected objects;
* representation of image scenes as property graphs;
* persistence and querying with Neo4j;
* visualization of the generated scene graph.

The initial relationships will be based on geometric information from bounding boxes, such as:

```text
LEFT_OF
RIGHT_OF
ABOVE
BELOW
NEAR
OVERLAPS
```

Future versions may explore image embeddings, vector search, semantic relationships, and hybrid visual search.

## Local development

### Neo4j

Requirements: Docker with Compose, and [uv](https://docs.astral.sh/uv/) for the backend.

```bash
cp .env.example .env        # then set NEO4J_PASSWORD (.env is not versioned)
docker compose up -d --wait # starts Neo4j and waits until it is healthy
```

* Neo4j Browser: <http://localhost:7474> (Connect URL `bolt://localhost:7687`, user/password from `.env`)
* Data and logs are stored in `./neo4j/` (git-ignored). Stop with `docker compose down`;
  reset the database with `docker compose down` followed by deleting `./neo4j/data`.

Verify the backend can connect (needs the container running):

```bash
cd backend
uv sync
uv run pytest -m integration
```

### Database schema

Constraints and indexes are created idempotently (safe to run repeatedly):

```bash
cd backend
uv run python -m visual_graph.graph
```

## License

This project is licensed under the MIT License.
