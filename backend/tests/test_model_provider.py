import os

import pytest
from app.models_provider.factory import get_model_provider


@pytest.mark.integration
def test_local_model_generates_a_real_response() -> None:
    if os.getenv("AGENTIA_RUN_MODEL_TESTS") != "1":
        pytest.skip("Activer AGENTIA_RUN_MODEL_TESTS=1 pour appeler le vrai modèle local")
    provider = get_model_provider()
    assert provider.health()["available"] is True
    response = provider.generate("Réponds avec une phrase courte en français.")
    assert response.provider == "ollama"
    assert response.text
    assert "<think>" not in response.text
    assert "</think>" not in response.text