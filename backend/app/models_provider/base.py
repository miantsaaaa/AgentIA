from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Generation:
    provider: str
    model: str
    text: str


class ModelProvider(Protocol):
    def generate(self, prompt: str, system: str = "") -> Generation: ...

    def health(self) -> dict[str, object]: ...