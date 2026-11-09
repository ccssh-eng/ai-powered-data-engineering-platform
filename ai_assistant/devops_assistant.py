# ============================================================
# DevOps AI Assistant — Module 6 Étape 1
# Utilise Groq (LLaMA 3) pour assister les tâches DevOps
# ============================================================

import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """Tu es un assistant DevOps expert. Tu aides à :
- Générer des scripts Python et Bash
- Créer des Dockerfiles optimisés et sécurisés
- Générer des pipelines GitLab CI/CD
- Analyser des logs et identifier des erreurs

Réponds toujours en français. Fournis du code prêt à l'emploi avec des commentaires clairs.
"""


def ask_assistant(question: str, context: str = "") -> str:
    """Envoie une question à l'assistant DevOps."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        messages.append({
            "role": "user",
            "content": f"Contexte :\n{context}\n\nQuestion : {question}"
        })
    else:
        messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=800,
    )

    return response.choices[0].message.content


def generate_dockerfile(app_description: str) -> str:
    """Génère un Dockerfile optimisé."""
    prompt = f"Génère un Dockerfile production-ready pour : {app_description}. Utilise un utilisateur non-root et des layers optimisés."
    return ask_assistant(prompt)


def generate_gitlab_pipeline(stages: list) -> str:
    """Génère un pipeline GitLab CI."""
    prompt = f"Génère un fichier .gitlab-ci.yml avec ces stages : {', '.join(stages)}. Inclus des règles pour la branche main."
    return ask_assistant(prompt)


def generate_bash_script(task: str) -> str:
    """Génère un script Bash."""
    prompt = f"Génère un script Bash robuste pour : {task}. Inclus la gestion des erreurs avec set -euo pipefail."
    return ask_assistant(prompt)


def analyze_logs(log_content: str) -> str:
    """Analyse des logs et identifie les erreurs."""
    prompt = "Analyse ces logs, identifie les erreurs critiques et propose des solutions :"
    return ask_assistant(prompt, context=log_content)


def save_response(task_type: str, response: str):
    """Sauvegarde la réponse dans un fichier log."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_assistant/logs/{task_type}_{timestamp}.txt"
    os.makedirs("ai_assistant/logs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)
    print(f" Réponse sauvegardée : {filename}")


if __name__ == "__main__":
    print("=" * 60)
    print(" DevOps AI Assistant — Module 6 Étape 1")
    print("=" * 60)

    # Test 1 — Générer un Dockerfile
    print("\n Test 1 : Génération d'un Dockerfile")
    result = generate_dockerfile("API Flask avec MongoDB, Python 3.11")
    print(result[:500] + "...\n")
    save_response("dockerfile", result)

    # Test 2 — Analyser des logs fictifs
    print("\n Test 2 : Analyse de logs")
    sample_logs = """
    2026-11-09 10:32:11 ERROR - Connection refused: postgresql://localhost:5432/ai_platform
    2026-11-09 10:32:12 ERROR - Retrying... (1/3)
    2026-11-09 10:32:15 ERROR - Retrying... (2/3)
    2026-11-09 10:32:18 CRITICAL - Max retries exceeded. Pipeline aborted.
    """
    result = analyze_logs(sample_logs)
    print(result[:500] + "...\n")
    save_response("log_analysis", result)

    print("\n Module 6 Étape 1 — Tests terminés !")
