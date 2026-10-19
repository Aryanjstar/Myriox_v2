#!/usr/bin/env python3
"""Embeds docs/building_codes/ada_clauses.json via Azure OpenAI and loads them into the
Cosmos DB `codeClauses` vector container. Run from the Simulation Service virtual environment
(which supplies azure-cosmos and langchain-openai).

Usage:
    cd apps/simulation-service && source .venv/bin/activate
    python ../../infra/scripts/seed_code_clauses.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "simulation-service"))

from app.core.config import get_settings  # noqa: E402
from app.services.cosmos import code_clauses_container  # noqa: E402
from langchain_openai import AzureOpenAIEmbeddings  # noqa: E402

CLAUSES_PATH = Path(__file__).resolve().parents[2] / "docs" / "building_codes" / "ada_clauses.json"


def main() -> None:
    settings = get_settings()
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.embedding_deployment,
    )

    clauses = json.loads(CLAUSES_PATH.read_text())
    container = code_clauses_container()

    texts = [c["text"] for c in clauses]
    vectors = embeddings.embed_documents(texts)

    for clause, vector in zip(clauses, vectors):
        doc = {**clause, "embedding": vector}
        container.upsert_item(doc)
        print(f"seeded {clause['id']}")

    print(f"Done. Seeded {len(clauses)} clauses into codeClauses container.")


if __name__ == "__main__":
    main()
