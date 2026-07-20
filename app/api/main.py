from fastapi import FastAPI, HTTPException

from app.models import ResearchRequest
from app.orchestrator import run_research


app = FastAPI(
    title="EvidenceOps Agent API",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/research")
async def research(
    request: ResearchRequest,
) -> dict[str, str]:
    try:
        result = await run_research(
            request.question,
            approved_to_save=not request.require_approval,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc