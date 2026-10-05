from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    risk: str
    requires_approval: bool


TOOLS = {
    tool.name: tool
    for tool in (
        ToolDefinition("file.read", "Lire un fichier texte autorisé", "READ", False),
        ToolDefinition("filesystem.list", "Lister un dossier autorisé", "READ", False),
        ToolDefinition("text.search", "Rechercher dans les fichiers autorisés", "READ", False),
        ToolDefinition("calculator", "Calcul arithmétique déterministe", "LOW_RISK", False),
        ToolDefinition(
            "quant.paper_trade", "Simuler un ordre sans exécution réelle", "CRITICAL", True
        ),
    )
}


def tool_catalog() -> list[dict[str, Any]]:
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "risk": tool.risk,
            "requires_approval": tool.requires_approval,
        }
        for tool in TOOLS.values()
    ]