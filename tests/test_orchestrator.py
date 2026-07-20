import pytest

from app.orchestrator import validate_question


def test_validate_question_accepts_valid_question() -> None:
    question = (
        "What controls are required "
        "for high-impact AI agents?"
    )

    result = validate_question(question)

    assert result == question


def test_validate_question_rejects_short_question() -> None:
    with pytest.raises(ValueError):
        validate_question("AI")


def test_validate_question_rejects_empty_question() -> None:
    with pytest.raises(ValueError):
        validate_question("")


def test_validate_question_removes_extra_spaces() -> None:
    result = validate_question(
        "  What controls reduce agent risk?  "
    )

    assert result == (
        "What controls reduce agent risk?"
    )


def test_validate_question_rejects_broad_question() -> None:
    with pytest.raises(ValueError):
        validate_question("Tell me about AI")