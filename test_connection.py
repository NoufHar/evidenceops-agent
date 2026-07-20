from app.services.llm import configure_models


def main():
    llm, embed_model = configure_models()

    response = llm.complete("Reply with exactly: Connection successful")

    embedding = embed_model.get_text_embedding("EvidenceOps test")

    print(response.text)
    print(f"Embedding length: {len(embedding)}")


if __name__ == "__main__":
    main()