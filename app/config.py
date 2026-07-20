import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    groq_api_key = os.getenv("GROQ_API_KEY")
    llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    embedding_model = os.getenv(
        "EMBEDDING_MODEL",
        "BAAI/bge-small-en-v1.5",
    )
    data_dir = os.getenv("DATA_DIR", "data")
    storage_dir = os.getenv("STORAGE_DIR", "storage")
    top_k = int(os.getenv("TOP_K", "4"))


config = Config()