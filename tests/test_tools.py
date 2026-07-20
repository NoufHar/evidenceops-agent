import json
from pathlib import Path

from app.tools.research_tools import (
    build_tools,
    record_audit_event,
    save_report,
)


def test_save_report_creates_markdown_file(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    message = save_report(
        "Test Report",
        "# Result",
    )

    assert "saved" in message.lower()
    assert Path("reports/test_report.md").exists()


def test_save_report_writes_correct_content(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    save_report(
        "AI Governance",
        "# AI Governance\n\nApproved content.",
    )

    path = Path("reports/ai_governance.md")

    assert path.read_text(
        encoding="utf-8"
    ) == "# AI Governance\n\nApproved content."


def test_save_report_sanitizes_filename(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    save_report(
        "../../Unsafe Report!",
        "# Safe",
    )

    files = list(Path("reports").glob("*.md"))

    assert len(files) == 1
    assert files[0].parent == Path("reports")


def test_record_audit_event_creates_jsonl(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    record_audit_event(
        "test",
        "tool executed",
    )

    assert Path(
        "reports/audit_log.jsonl"
    ).exists()


def test_record_audit_event_is_valid_json(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    record_audit_event(
        "research_started",
        "report_id=abc123",
    )

    line = Path(
        "reports/audit_log.jsonl"
    ).read_text(
        encoding="utf-8"
    ).strip()

    event = json.loads(line)

    assert event["action"] == "research_started"
    assert event["report_id"] == "report_id=abc123"
    assert event["details"] == {}
    assert "timestamp" in event


def test_save_tool_hidden_without_approval(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.tools.research_tools.load_query_engine",
        lambda: object(),
    )

    tools = build_tools(
        approved_to_save=False
    )

    tool_names = [
        tool.metadata.name
        for tool in tools
    ]

    assert "save_report" not in tool_names


def test_save_tool_available_after_approval(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.tools.research_tools.load_query_engine",
        lambda: object(),
    )

    tools = build_tools(
        approved_to_save=True
    )

    tool_names = [
        tool.metadata.name
        for tool in tools
    ]

    assert "save_report" in tool_names