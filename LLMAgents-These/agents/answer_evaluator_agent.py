from typing import Optional, List

from atomic_agents import BaseIOSchema, AtomicAgent, AgentConfig
from atomic_agents.context import SystemPromptGenerator, ChatHistory
from .mistral_client import get_mistral_client

class EvaluateRequestInput(BaseIOSchema):
    """
    Schema pour l'entrée de l'agent d'évaluation.
    Contient la question, la réponse attendue et la réponse de l'utilisateur.
    """
    question: str
    expected_answer: str
    user_answer: str

class AgentEvaluationResult(BaseIOSchema):
    """
    Contains the evaluation given by a LM to the answer. Also, with cos sim.
    """
    score: int  # Note de 1 à 10
    feedback: str  # Commentaire sur la réponse
    cosine_similarity: Optional[float]  # Similarité cosinus entre la question et la réponse

class ListAgentEvaluationResult(BaseIOSchema):
    """
    A list of evaluation results, meant to be summarized.
    """
    evaluations: List[AgentEvaluationResult]


evaluation_system_prompt_generator = SystemPromptGenerator(
    background=[
        "Cet agent est spécialisé dans l'évaluation des réponses des utilisateurs à des questions de compréhension.",
        "Il vérifie si la réponse de l'utilisateur correspond à la réponse attendue",

    ],
    steps=[
        "Analyser la question et la réponse attendue.",
        "Comparer la réponse de l'utilisateur avec la réponse attendue.",
        "Évaluer la pertinence de la réponse.",
        "Attribuer une note de 1 à 10 (1 = complètement incorrect, 10 = complet).",
        "Répondre à l'utilisateur de manière naturelle"
    ],
    output_instructions=[
        "La note doit être un entier entre 1 et 10.",
        "Le commentaire doit être clair, constructif et en français.",
        "L'évaluation doit être légère. Ne pas pénaliser si l'utilisateur donne une réponse cohérente."
        "Ne pas pénaliser si l'utilisateur rajoute du contexte si cela est pertinent.",
        "La réponse doit être rédigée. Pas de réponse en mots-clefs."
        "Ne pas mentionner la note dans la réponse rédigée."
    ],
)

final_evaluation_system_prompt_generator = SystemPromptGenerator(
    background=[
        "Cet agent est spécialisé dans la synthèse des évaluations fournies par plusieurs évaluateurs.",
        "Il reçoit les notes et commentaires de plusieurs évaluateurs et doit proposer une seule évaluation finale, avec une note sur 10.",
        "Il doit fournir un message final, écrit sur un ton naturel, qui sera affiché à l'utilisateur.",
    ],
    steps=[
        "Analyser les notes et commentaires de chaque évaluateur.",
        "Identifier les points communs et les divergences entre les évaluations.",
        "Calculer une note finale qui reflète le consensus des évaluateurs.",
        "Prendre en compte la cohérence globale des réponses et l'équité des évaluations.",
        "Rédiger un commentaire final qui synthétise les retours des évaluateurs.",
        "Rédiger le message qui sera donné à l'utilisateur"
    ],
    output_instructions=[
        "La note finale doit être un entier entre 1 et 10. Avec moins de 7, l'utilisateur doit recommencer.",
        "Le commentaire final doit être clair, concis, constructif et en français.",
        "Le message final doit rebondir sur la réponse de l'utilisateur. S'il a oublié des détails, alors ce sera précisé dans le message.",
        "Ne pas mentionner la note dans la réponse rédigée.",
        "Si l'utilisateur doit recommencer, alors on pourra lui suggérer, indirectement, ce qu'ils devrait rajouter."
    ],
)

def get_final_evaluator_agent(model: str = "mistral-medium"):
    client = get_mistral_client()
    final_evaluation_agent = AtomicAgent[ListAgentEvaluationResult, AgentEvaluationResult](
        config=AgentConfig(
            client=client,
            model=model,
            history=ChatHistory(),
            system_prompt_generator=final_evaluation_system_prompt_generator,
        )
    )
    return final_evaluation_agent

def get_evaluator_agent(model: str = "mistral-medium"):
    client = get_mistral_client(async_mode=True)
    evaluation_agent = AtomicAgent[EvaluateRequestInput, AgentEvaluationResult](
        config=AgentConfig(
            client=client,
            model=model,
            history=ChatHistory(),
            system_prompt_generator=evaluation_system_prompt_generator,
        )
    )
    return evaluation_agent