from app.services.index_service import load_query_engine


def main():
    engine = load_query_engine()

    response = engine.query(
        "What controls should govern consequential agent actions?"
    )

    print("\n===== Answer =====\n")
    print(response)

    print("\n===== Sources =====\n")

    for node in response.source_nodes:
        print(node.metadata.get("file_name"))
        print("-" * 40)


if __name__ == "__main__":
    main()