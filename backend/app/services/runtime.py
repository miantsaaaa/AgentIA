from app.models.agent import Agent
from app.models_provider.base import Generation
from app.models_provider.factory import get_model_provider


def run_agent(agent: Agent, prompt: str) -> Generation:
    skills = ", ".join(agent.skills) if agent.skills else "aucune compétence certifiée"
    system = (
        f"Tu es {agent.name}, spécialisé en {agent.domain}. {agent.description} "
        f"Compétences déclarées : {skills}. "
        "Réponds en français, n'invente pas de faits et ne demande jamais de mot de passe, "
        "jeton, clé privée ou autre secret."
    )
    return get_model_provider().generate(prompt, system)