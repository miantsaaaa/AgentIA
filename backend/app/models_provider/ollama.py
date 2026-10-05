import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.models_provider.base import Generation


class ModelProviderError(RuntimeError):
    pass


class OllamaProvider:
    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (
            base_url or os.getenv("AGENTIA_OLLAMA_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.model = model or os.getenv("AGENTIA_MODEL_NAME", "qwen3:4b")

    def _request(self, path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"} if data is not None else {},
        )
        try:
            with urlopen(request, timeout=180) as response:
                return json.loads(response.read())
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ModelProviderError(f"Ollama local indisponible : {error}") from error

    def health(self) -> dict[str, object]:
        response = self._request("/api/tags")
        model_names = [item["name"] for item in response.get("models", [])]
        available = self.model in model_names or f"{self.model}:latest" in model_names
        return {"provider": "ollama", "model": self.model, "available": available}

    def generate(
        self,
        prompt: str,
        system: str = "",
        history: list[dict[str, str]] | None = None,
    ) -> Generation:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        for turn in history or []:
            if turn.get("role") not in {"user", "assistant"}:
                raise ValueError("Rôle conversationnel non autorisé")
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": prompt})
        response = self._request(
            "/api/chat",
            {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "think": False,
                "options": {"temperature": 0.2, "num_predict": 1600, "seed": 42},
            },
        )
        message = response.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ModelProviderError("Ollama a retourné une réponse sans contenu exploitable")
        text = message["content"]
        while "</think>" in text:
            start = text.find("<think>")
            end = text.find("</think>")
            if start < 0 or start > end:
                text = text[end + len("</think>") :]
            else:
                text = text[:start] + text[end + len("</think>") :]
        if "<think>" in text:
            raise ModelProviderError("Ollama n'a pas terminé le raisonnement avant la limite")
        text = text.strip()
        if not text:
            raise ModelProviderError("Ollama n'a retourné aucun texte final")
        return Generation(provider="ollama", model=self.model, text=text)