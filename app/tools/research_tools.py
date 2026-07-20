from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llama_index.core.tools import FunctionTool, QueryEngineTool

from app.services.index_service import load_query_engine


def save_report(title: str, content: str) -> str:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    safe_name = "".join(
        ch
        for ch in title.lower().replace(" ", "_")
        if ch.isalnum() or ch == "_"
    )

    path = reports_dir / f"{safe_name[:60] or 'report'}.md"
    path.write_text(content, encoding="utf-8")

    return f"Report saved to {path}"


#def record_audit_event(action: str, detail: str) -> str:
    log_path = Path("reports/audit_log.jsonl")
    log_path.parent.mkdir(exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "detail": detail,
    }

    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return "Audit event recorded."
def record_audit_event(
    action : str,
    report_id: str,
    tool_name: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    audit_file = Path("reports/audit_log.jsonl")
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_id": report_id,
        "action": action,
        "tool_name": tool_name,
        "details": details or {},
    }

    with audit_file.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

def compare_sources(topic_one: str, topic_two: str) -> str:
    query_engine = load_query_engine()

    result_one = query_engine.query(topic_one)
    result_two = query_engine.query(topic_two)

    return (
        f"Topic One: {topic_one}\n"
        f"Evidence One:\n{result_one}\n\n"
        f"Topic Two: {topic_two}\n"
        f"Evidence Two:\n{result_two}\n\n"
        "Compare the overlap, differences, and evidence limitations."
    )


def build_tools(approved_to_save: bool = False):
    query_engine = load_query_engine()

    knowledge_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="knowledge_base_search",
        description=(
            "Search the indexed bootcamp knowledge base. "
            "Use it before making factual claims."
        ),
    )

    audit_tool = FunctionTool.from_defaults(
        fn=record_audit_event,
        name="record_audit_event",
        description="Record an audit event for important actions.",
    )

    compare_tool = FunctionTool.from_defaults(
        fn=compare_sources,
        name="compare_sources",
        description=(
            "Compare evidence for two topics and return overlap, "
            "differences, and evidence limitations."
        ),
    )

    tools = [
        knowledge_tool,
        audit_tool,
        compare_tool,
    ]

    if approved_to_save:
        save_tool = FunctionTool.from_defaults(
            fn=save_report,
            name="save_report",
            description="Save an approved Markdown report.",
        )

        tools.append(save_tool)

    return tools