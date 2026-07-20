from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

from app.config import config


def configure_models():
    if not config.groq_api_key:
        raise ValueError("GROQ_API_KEY is missing from the .env file")

    Settings.llm = OpenAILike(
        model=config.llm_model,
        api_key=config.groq_api_key,
        api_base="https://api.groq.com/openai/v1",
        is_chat_model=True,
        is_function_calling_model=True,
        temperature=0,
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=config.embedding_model,
    )

    return Settings.llm, Settings.embed_model