import asyncio

from app.orchestrator import run_research


async def main() -> None:
    print("EvidenceOps Agent - type 'exit' to stop")

    while True:
        question = input(
            "\nResearch question: "
        ).strip()

        if question.lower() in {"exit", "quit"}:
            break

        draft = await run_research(
            question,
            approved_to_save=False,
        )

        print(f"\nReport ID: {draft['report_id']}")
        print(f"Status: {draft['status']}")

        print("\n--- Draft ---\n")
        print(draft["result"])

        if draft["status"] == "failed":
            continue

        approval = input(
            "\nSave an approved final report? [y/N]: "
        ).strip().lower()

        if approval == "y":
            final_result = await run_research(
                question,
                approved_to_save=True,
            )

            print(
                f"\nReport ID: "
                f"{final_result['report_id']}"
            )
            print(
                f"Status: "
                f"{final_result['status']}"
            )

            print("\n--- Final Run ---\n")
            print(final_result["result"])


if __name__ == "__main__":
    asyncio.run(main())