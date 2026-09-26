"""LangGraph entry points for a direct (serverless) LangSmith deployment.

`mda deploy` generates equivalent shims under `.mda/build/`, but those embed
absolute local paths and are git-ignored. This module is the portable,
checked-in counterpart referenced by `langgraph.json`.

Unlike the generated entry, it honors an assistant's `configurable.model` and
`configurable.system_prompt`, so what an assistant declares is what its runs
use.
"""

from pathlib import Path

from langgraph_sdk.runtime import ServerRuntime
from managed_deepagents.define_deep_agent import DeepAgentDefinition
from managed_deepagents.runtime import (
    build_managed_auth,
    build_managed_http_app,
    compile_managed_agent_async,
)

from agent import agent as _definition
from identity import identity as _identity

_instructions = (Path(__file__).parent / "instructions.md").read_text(encoding="utf-8")

auth = build_managed_auth(_identity)
app = build_managed_http_app(identity=_identity)


def _configurable_str(config, key: str) -> str | None:
    configurable = (config or {}).get("configurable") or {}
    value = configurable.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else None


async def agent(config, runtime: ServerRuntime):
    definition = _definition
    if model := _configurable_str(config, "model"):
        definition = DeepAgentDefinition({**_definition.config, "model": model})

    execution = runtime.execution_runtime
    return await compile_managed_agent_async(
        definition,
        config,
        system_prompt=_configurable_str(config, "system_prompt") or _instructions,
        identity=_identity,
        run_context=execution.context if execution is not None else None,
        is_run=execution is not None,
    )
