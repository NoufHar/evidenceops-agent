import asyncio
import json
import time
from pathlib import Path
from typing import Any

from app.orchestrator import run_research
from app.services.index_service import load_query_engine


DATASET_PATH = Path("evaluation/evaluation_dataset.jsonl")
RESULTS_PATH = Path("evaluation/evaluation_results.jsonl")

MAX_QUESTIONS = 5

WAIT_BEFORE_START = 65

WAIT_BETWEEN_QUESTIONS = 120


def load_questions() -> list[dict[str, Any]]:
    """Load evaluation questions from the JSONL dataset."""
    questions: list[dict[str, Any]] = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                questions.append(json.loads(line))

    return questions[:MAX_QUESTIONS]


def get_retrieved_sources(
    query_engine: Any,
    question: str,
) -> list[str]:
    """Retrieve source file names without generating an LLM answer."""
    try:
        nodes = query_engine._retriever.retrieve(question)
    except Exception as exc:
        print(f"Retrieval error: {exc}")
        return []

    sources: list[str] = []

    for node in nodes:
        metadata = node.node.metadata or {}

        source = (
            metadata.get("file_name")
            or metadata.get("source")
            or metadata.get("filename")
            or "unknown"
        )

        source = str(source)

        if source not in sources:
            sources.append(source)

    return sources


def calculate_retrieval_hit(
    expected_source: str | None,
    retrieved_sources: list[str],
) -> bool | None:
    """Check whether the expected source appears in retrieved sources."""
    if not expected_source:
        return None

    expected_name = Path(expected_source).name.lower()

    return any(
        Path(source).name.lower() == expected_name
        for source in retrieved_sources
    )


async def run_agent(question: str) -> tuple[str, str | None, float]:
    """Run the agent and return status, error, and latency."""
    start_time = time.perf_counter()

    try:
        result = await run_research(
            question=question,
            approved_to_save=False,
        )

        latency = time.perf_counter() - start_time

        if isinstance(result, dict):
            status = str(result.get("status", "unknown"))
        else:
            status = "completed"

        return status, None, latency

    except Exception as exc:
        latency = time.perf_counter() - start_time

        return "failed", str(exc), latency


def save_results(results: list[dict[str, Any]]) -> None:
    """Save all completed results to JSONL."""
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open("w", encoding="utf-8") as file:
        for result in results:
            file.write(
                json.dumps(
                    result,
                    ensure_ascii=False,
                )
                + "\n"
            )


def print_summary(results: list[dict[str, Any]]) -> None:
    """Print evaluation summary."""
    retrieval_values = [
        result["retrieval_hit"]
        for result in results
        if result["retrieval_hit"] is not None
    ]

    successful_approval_values = [
        result["approval_compliance"]
        for result in results
        if result["approval_compliance"] is not None
    ]

    latency_values = [
        result["latency_seconds"]
        for result in results
    ]

    retrieval_rate = (
        sum(retrieval_values) / len(retrieval_values) * 100
        if retrieval_values
        else 0
    )

    approval_rate = (
        sum(successful_approval_values)
        / len(successful_approval_values)
        * 100
        if successful_approval_values
        else 0
    )

    average_latency = (
        sum(latency_values) / len(latency_values)
        if latency_values
        else 0
    )

    failed_count = sum(
        result["status"] == "failed"
        for result in results
    )

    print("\n" + "=" * 70)
    print("Final Evaluation Results")
    print("=" * 70)
    print(f"Questions evaluated: {len(results)}")
    print(f"Retrieval Hit Rate: {retrieval_rate:.2f}%")
    print(f"Approval Compliance: {approval_rate:.2f}%")
    print(f"Average Latency: {average_latency:.2f} seconds")
    print(f"Technical Failures: {failed_count}")
    print(f"Results saved to: {RESULTS_PATH}")


async def main() -> None:
    questions = load_questions()

    if not questions:
        print("No evaluation questions were found.")
        return

    print("Loading query engine...")
    query_engine = load_query_engine()

    results: list[dict[str, Any]] = []

    print(f"\nStarting evaluation for {len(questions)} question(s)...")

    if WAIT_BEFORE_START > 0:
        print(
            f"Waiting {WAIT_BEFORE_START} seconds "
            "before the first question..."
        )
        await asyncio.sleep(WAIT_BEFORE_START)

    for index, item in enumerate(questions, start=1):
        question_id = item.get("id", f"q{index:03d}")
        question = item["question"]
        expected_source = item.get("expected_source")

        print("\n" + "=" * 70)
        print(f"Question {index}/{len(questions)}")
        print(f"Evaluating: {question_id}")
        print(question)

        retrieved_sources = get_retrieved_sources(
            query_engine=query_engine,
            question=question,
        )

        retrieval_hit = calculate_retrieval_hit(
            expected_source=expected_source,
            retrieved_sources=retrieved_sources,
        )

        status, error, latency = await run_agent(question)

        if status == "awaiting_approval":
            approval_compliance: bool | None = True
        elif status == "failed":
            approval_compliance = None
        else:
            approval_compliance = False

        result = {
            "id": question_id,
            "question": question,
            "expected_source": expected_source,
            "retrieval_hit": retrieval_hit,
            "approval_compliance": approval_compliance,
            "latency_seconds": round(latency, 2),
            "status": status,
            "retrieved_sources": retrieved_sources,
            "error": error,
        }

        results.append(result)

        save_results(results)

        print("\nResult:")
        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        if index < len(questions):
            print(
                f"\nWaiting {WAIT_BETWEEN_QUESTIONS} seconds "
                "before the next question..."
            )
            await asyncio.sleep(WAIT_BETWEEN_QUESTIONS)

    print_summary(results)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEvaluation stopped by the user.")
        print(
            "Completed results remain saved in "
            "evaluation/evaluation_results.jsonl"
        )