from app.models.agent import Agent
from app.models.system_agent import SystemAgent
from app.models_provider.base import Generation
from app.models_provider.factory import get_model_provider


def run_agent(
    agent: Agent,
    prompt: str,
    history: list[dict[str, str]] | None = None,
) -> Generation:
    skills = ", ".join(agent.skills) if agent.skills else "aucune compétence certifiée"
    system = (
        f"Tu es {agent.name}, spécialisé en {agent.domain}. {agent.description} "
        f"Compétences déclarées : {skills}. "
        "Réponds en français, n'invente pas de faits et ne demande jamais de mot de passe, "
        "jeton, clé privée ou autre secret."
    )
    return get_model_provider().generate(prompt, system, history)


def run_system_agent(
    agent: SystemAgent,
    prompt: str,
    history: list[dict[str, str]] | None = None,
) -> Generation:
    system = (
        f"Tu es {agent.name}, chef d'orchestre de la plateforme AgentIA. "
        f"{agent.description}\n\nMéthode de travail obligatoire :\n"
        f"{agent.operating_instructions}\n\n"
        "Réponds en français. Ne prétends jamais avoir modifié ou testé un fichier sans preuve. "
        "Tu n'as aucun accès implicite au PC ni aux tools ; "
        "les actions sont contrôlées séparément. "
        "Ne demande, ne reçois et ne répète jamais de PIN Windows ou de mot de passe."
    )
    return get_model_provider().generate(prompt, system, history)