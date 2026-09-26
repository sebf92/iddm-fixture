from managed_deepagents import define_deep_agent

from tools.web import fetch_page, web_search

# Kimi-K3 through LangSmith Gateway, billed to workspace Gateway Credits.
agent = define_deep_agent(
    name="radiant-docs-agent",
    model="langsmith:moonshotai/kimi-k3",
    tools=[web_search, fetch_page],
)
