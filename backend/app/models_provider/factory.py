from app.models_provider.base import ModelProvider
from app.models_provider.ollama import OllamaProvider


def get_model_provider() -> ModelProvider:
    return OllamaProvider()