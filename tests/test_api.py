from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_research_rejects_short_question() -> None:
    response = client.post(
        "/research",
        json={
            "question": "AI",
            "require_approval": True,
        },
    )

    assert response.status_code == 422


def test_research_accepts_valid_schema(
    monkeypatch,
) -> None:
    async def fake_run_research(
        question: str,
        approved_to_save: bool = False,
    ) -> dict[str, str]:
        return {
            "report_id": "test123",
            "status": "awaiting_approval",
            "result": "Test result",
        }

    monkeypatch.setattr(
        "app.api.main.run_research",
        fake_run_research,
    )

    response = client.post(
        "/research",
        json={
            "question": (
                "What controls reduce "
                "risk in AI agents?"
            ),
            "audience": "AI governance team",
            "require_approval": True,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "report_id": "test123",
        "status": "awaiting_approval",
        "result": "Test result",
    }