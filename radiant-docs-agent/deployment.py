"""LangGraph entry points for a direct (serverless) LangSmith deployment.

`mda deploy` generates equivalent shims under `.mda/build/`, but those embed
absolute local paths and are git-ignored. This module is the portable,
checked-in counterpart referenced by `langgraph.json`.
"""

from pathlib import Path

from langgraph_sdk.runtime import ServerRuntime
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


async def agent(config, runtime: ServerRuntime):
    execution = runtime.execution_runtime
    return await compile_managed_agent_async(
        _definition,
        config,
        system_prompt=_instructions,
        identity=_identity,
        run_context=execution.context if execution is not None else None,
        is_run=execution is not None,
    )
