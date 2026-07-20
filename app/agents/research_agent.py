from __future__ import annotations

from llama_index.core.agent.workflow import FunctionAgent

from app.services.llm import configure_models
from app.tools.research_tools import build_tools


SYSTEM_PROMPT = """
You are EvidenceOps, a careful research operations agent.

Operational rules:
1. Break complex requests into explicit subproblems.
2. Search the knowledge base before making factual claims.
3. Distinguish evidence, inference, and recommendation.
4. Never invent information or citations.
5. Ask for human approval before saving a final report.
6. Record important actions in the audit log.
7. End with findings, evidence limitations, confidence, and next action.
"""


def build_agent(
    approved_to_save: bool = False,
) -> FunctionAgent:
    configure_models()

    return FunctionAgent(
        name="EvidenceOpsAgent",
        description=(
            "Plans research, retrieves evidence, "
            "synthesizes findings, and prepares reports."
        ),
        system_prompt=SYSTEM_PROMPT,
        tools=build_tools(
            approved_to_save=approved_to_save
        ),
    )