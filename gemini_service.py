import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-2.5-flash-lite"

client = genai.GenerativeModel(MODEL)

SYSTEM_PROMPT = """
Tu es le moteur d'intelligence artificielle de l'application
"Super Student AI", un assistant de gestion de projet destiné aux étudiants.

À partir de la description d'un projet fournie par un étudiant, tu dois produire
une analyse complète et structurée pour l'aider à organiser son travail.

Tu DOIS répondre UNIQUEMENT avec un objet JSON valide, sans texte avant ou après,
sans balises markdown.

Le JSON doit respecter exactement cette structure :

{
  "complexite": {
    "score": 0,
    "niveau": "Faible | Moyenne | Élevée",
    "justification": "Explication courte du score de complexité."
  },
  "analyse": "Texte d'analyse générale du projet.",
  "taches": [
    {
      "nom": "Nom court de la tâche",
      "description": "Description détaillée de la tâche",
      "priorite": "Haute | Moyenne | Basse",
      "duree_estimee": "Estimation en jours ou semaines"
    }
  ],
  "planning": [
    {
      "semaine": 1,
      "titre": "Titre de la semaine",
      "taches": ["Nom de tâche 1", "Nom de tâche 2"]
    }
  ],
  "risques": [
    {
      "risque": "Description du risque",
      "impact": "Élevé | Moyen | Faible",
      "probabilite": "Élevée | Moyenne | Faible",
      "mitigation": "Action recommandée pour réduire ce risque"
    }
  ],
  "feedback": "Conseils personnalisés pour l'étudiant."
}

Règles importantes :
- Calcule un score de complexité entre 1 et 10.
- Le niveau de complexité doit être : Faible, Moyenne ou Élevée.
- Justifie le score en 1 à 2 phrases.
- Génère entre 5 et 10 tâches pertinentes.
- Construis un planning réaliste.
- Identifie entre 3 et 6 risques.
- Réponds uniquement en français.
- Le résultat doit être un JSON valide.
"""


def build_prompt(nom_projet, description, duree, contraintes):
    parts = [
        f"Nom du projet : {nom_projet}",
        f"Description du projet : {description}",
    ]

    if duree:
        parts.append(f"Durée disponible : {duree}")

    if contraintes:
        parts.append(f"Contraintes : {contraintes}")

    parts.append(
        "Analyse ce projet étudiant et renvoie uniquement le JSON demandé."
    )

    return "\n".join(parts)


def _extract_json(texte):
    texte = texte.strip()

    texte = re.sub(
        r"^```(json)?",
        "",
        texte,
        flags=re.IGNORECASE
    ).strip()

    texte = re.sub(
        r"```$",
        "",
        texte
    ).strip()

    if not texte.startswith("{"):
        match = re.search(r"\{.*\}", texte, re.DOTALL)

        if match:
            texte = match.group(0)

    return json.loads(texte)


def analyser_projet(nom_projet, description, duree="", contraintes=""):
    prompt = build_prompt(
        nom_projet,
        description,
        duree,
        contraintes
    )

    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

    response = client.generate_content(full_prompt)

    texte_brut = response.text

    try:
        resultat = _extract_json(texte_brut)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "La réponse générée n'est pas un JSON valide.\n\n"
            f"Réponse brute : {texte_brut[:500]}"
        ) from exc

    for cle, defaut in [
        ("complexite", {
            "score": 0,
            "niveau": "Non évaluée",
            "justification": ""
        }),
        ("analyse", ""),
        ("taches", []),
        ("planning", []),
        ("risques", []),
        ("feedback", ""),
    ]:
        resultat.setdefault(cle, defaut)

    return resultat