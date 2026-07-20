from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    question: str = Field(
        min_length=10,
        description=(
            "Research question or objective."
        ),
    )

    audience: str | None = Field(
        default=None,
        description=(
            "Intended audience for the result."
        ),
    )

    require_approval: bool = True