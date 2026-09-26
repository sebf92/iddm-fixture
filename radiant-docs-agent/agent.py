from deepagents import FilesystemPermission
from managed_deepagents import define_deep_agent

from tools.web import fetch_page, web_search

# Delegation target: the only place pages are downloaded. It gets its own tool
# set and a read-only filesystem, so the parent and the subagent differ in
# both tools and permissions.
page_reader = {
    "name": "page-reader",
    "description": (
        "Reads one or more web pages (URLs from web_search) and returns the "
        "passages that answer the question, with each source URL."
    ),
    "system_prompt": (
        "Fetch each URL you are given with fetch_page. Return only the passages "
        "relevant to the task, quoted or closely paraphrased, each followed by "
        "its source URL. Do not answer beyond what the pages say."
    ),
    "tools": [fetch_page],
    "permissions": [
        FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ],
}

# Kimi-K3 through LangSmith Gateway, billed to workspace Gateway Credits.
agent = define_deep_agent(
    name="radiant-docs-agent",
    model="langsmith:moonshotai/kimi-k3",
    tools=[web_search],
    subagents=[page_reader],
)
