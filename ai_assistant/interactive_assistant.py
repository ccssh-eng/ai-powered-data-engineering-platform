# ============================================================
# Interactive DevOps Assistant — Module 6 Étape 2
# Assistant conversationnel avec historique de conversation
# ============================================================

import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """Tu es un assistant DevOps expert spécialisé dans :
- Docker, Kubernetes, GitLab CI/CD
- Python, Bash, Terraform
- Monitoring, logs, incidents de production
- Data Engineering : Airflow, dbt, Kafka, PostgreSQL

Réponds toujours en français. Sois concis et fournis du code prêt à l'emploi.
Quand tu génères du code, utilise des blocs markdown avec le langage approprié.
"""

COMMANDS = {
    "/dockerfile": "Génère un Dockerfile pour : ",
    "/pipeline":  "Génère un pipeline GitLab CI pour : ",
    "/bash":      "Génère un script Bash pour : ",
    "/analyse":   "Analyse ces logs et propose des solutions : ",
    "/help":      None,
    "/quit":      None,
    "/history":   None,
}


def print_help():
    print("\n📖 Commandes disponibles :")
    print("  /dockerfile <description> — Génère un Dockerfile")
    print("  /pipeline   <stages>      — Génère un pipeline GitLab CI")
    print("  /bash       <tâche>       — Génère un script Bash")
    print("  /analyse    <logs>        — Analyse des logs")
    print("  /history                  — Affiche l'historique")
    print("  /quit                     — Quitter")
    print("  Ou posez simplement une question libre !\n")


def chat(history: list, user_message: str) -> str:
    """Envoie un message avec l'historique complet."""
    history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        temperature=0.3,
        max_tokens=800,
    )

    assistant_reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply


def save_session(history: list):
    """Sauvegarde la session dans un fichier."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_assistant/logs/session_{timestamp}.txt"
    os.makedirs("ai_assistant/logs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        for msg in history:
            role = " Vous" if msg["role"] == "user" else " Assistant"
            f.write(f"{role}:\n{msg['content']}\n\n{'─'*60}\n\n")
    print(f"\n Session sauvegardée : {filename}")


def main():
    history = []
    print("\n" + "=" * 60)
    print(" DevOps AI Assistant — Mode Interactif")
    print("=" * 60)
    print_help()

    while True:
        try:
            user_input = input("Vous > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input == "/quit":
            save_session(history)
            print("Au revoir !")
            break

        if user_input == "/help":
            print_help()
            continue

        if user_input == "/history":
            if not history:
                print("  (historique vide)\n")
            for msg in history:
                role = "Vous" if msg["role"] == "user" else "Assistant"
                print(f"  [{role}] {msg['content'][:100]}...")
            print()
            continue

        # Commandes raccourcies
        for cmd, prefix in COMMANDS.items():
            if user_input.startswith(cmd) and prefix:
                args = user_input[len(cmd):].strip()
                user_input = prefix + args
                break

        print("\n Assistant >\n")
        try:
            reply = chat(history, user_input)
            print(reply)
        except Exception as e:
            print(f" Erreur : {e}")
        print()


if __name__ == "__main__":
    main()
