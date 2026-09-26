"""Create or update the fixture's second, fully described assistant.

The default assistant that LangGraph creates from `langgraph.json` has no
description, tags or configurable values. This script adds a second assistant
on the same graph that sets all of them, so a deployment inventory sees two
entries for one deployment. Running it again updates the assistant in place.

Usage (from radiant-docs-agent/):
    LANGGRAPH_DEPLOYMENT_URL=https://<deployment>.us.langgraph.app \
        uv run python scripts/seed_assistants.py [--studio-auth]

Add --studio-auth against a live deployment (see main()). A local
`langgraph dev` with MDA_LOCAL_DEV=1 does not need it.

LANGSMITH_API_KEY is read from the environment or from .env.
"""

import os
import sys
from pathlib import Path

from langgraph_sdk import get_sync_client

GRAPH_ID = "radiant-docs-agent"

ASSISTANT = {
    "name": "radiant-docs-agent-concise",
    "description": (
        "Concise variant of the RadiantOne / IDDM documentation assistant: "
        "answers in three sentences or fewer, always with sources."
    ),
    "config": {
        "tags": ["fixture", "concise", "radiantone"],
        "configurable": {
            # Must be a model the LangSmith Gateway serves for this workspace.
            "model": "langsmith:moonshotai/kimi-k3",
            "system_prompt": (
                "You answer questions about Radiant Logic products (RadiantOne, "
                "IDDM, FID, IDO). Search with web_search, delegate page reading "
                "to the page-reader subagent, then answer in three sentences or "
                "fewer. End with the source URLs as markdown links. If the "
                "sources do not answer the question, say so."
            ),
        },
    },
    "metadata": {"fixture": "radiant-docs-agent", "variant": "concise"},
}


def _api_key() -> str:
    if key := os.environ.get("LANGSMITH_API_KEY"):
        return key
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("LANGSMITH_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("LANGSMITH_API_KEY is not set and not found in .env")


def main() -> None:
    url = os.environ.get("LANGGRAPH_DEPLOYMENT_URL")
    if not url:
        sys.exit("Set LANGGRAPH_DEPLOYMENT_URL to the deployment's API URL")

    # Managed auth lets only Studio principals write assistants, so a plain
    # API-key caller gets 403 on a live deployment. --studio-auth sends
    # `x-auth-scheme: langsmith`, the path Studio takes: the platform verifies
    # the workspace API key instead of the MDA custom auth. Opt-in only.
    headers = {"x-auth-scheme": "langsmith"} if "--studio-auth" in sys.argv[1:] else None
    client = get_sync_client(url=url, api_key=_api_key(), headers=headers)
    existing = [
        a
        for a in client.assistants.search(graph_id=GRAPH_ID, limit=100)
        if a["name"] == ASSISTANT["name"]
    ]
    if existing:
        assistant = client.assistants.update(existing[0]["assistant_id"], **ASSISTANT)
        action = "updated"
    else:
        assistant = client.assistants.create(graph_id=GRAPH_ID, **ASSISTANT)
        action = "created"
    print(f"{action} {assistant['name']} ({assistant['assistant_id']})")


if __name__ == "__main__":
    main()
