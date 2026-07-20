from __future__ import annotations

import asyncio
from uuid import uuid4

from app.agents.research_agent import build_agent
from app.tools.research_tools import record_audit_event


MAX_EXECUTION_SECONDS = 180


def validate_question(question: str) -> str:
    cleaned_question = question.strip()

    if len(cleaned_question) < 10:
        raise ValueError(
            "Please enter a more specific research objective."
        )

    broad_questions = {
        "research ai",
        "tell me about ai",
        "artificial intelligence",
        "research",
    }

    if cleaned_question.lower() in broad_questions:
        raise ValueError(
            "The research objective is too broad."
        )

    return cleaned_question


async def run_research(
    question: str,
    approved_to_save: bool = False,
) -> dict[str, str]:
    report_id = uuid4().hex[:12]

    try:
        question = validate_question(question)

        status = (
            "approved"
            if approved_to_save
            else "awaiting_approval"
        )

        record_audit_event(
            action="research_started",
            report_id=report_id,
            details={
                "question": question,
                "approved_to_save": approved_to_save,
            },
        )

        agent = build_agent(
            approved_to_save=approved_to_save,
        )

        approval_instruction = (
            "The user approved saving the final report."
            if approved_to_save
            else (
                "Prepare a draft. The save_report tool is not "
                "available until the user approves."
            )
        )

        prompt = f"""
Report ID: {report_id}
Research objective: {question}
Execution constraint: {approval_instruction}

Use the available tools and produce an evidence-grounded response.
"""

        result = await asyncio.wait_for(
            agent.run(user_msg=prompt),
            timeout=MAX_EXECUTION_SECONDS,
        )

        record_audit_event(
            action="research_completed",
            report_id=report_id,
            details={
                "status": status,
            },
        )

        return {
            "report_id": report_id,
            "status": status,
            "result": str(result),
        }

    except asyncio.TimeoutError:
        record_audit_event(
            action="research_failed",
            report_id=report_id,
            details={
                "reason": "execution_timeout",
            },
        )

        return {
            "report_id": report_id,
            "status": "failed",
            "result": "The research execution timed out.",
        }

    except Exception as exc:
        record_audit_event(
            action="research_failed",
            report_id=report_id,
            details={
                "error_type": type(exc).__name__,
                "reason": str(exc),
            },
        )

        return {
            "report_id": report_id,
            "status": "failed",
            "result": str(exc),
        }