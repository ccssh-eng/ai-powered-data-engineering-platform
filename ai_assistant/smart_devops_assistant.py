# ============================================================
# Smart DevOps Assistant — Module 6 Étape 4
# Analyse automatique des logs CI/CD + corrections validées
# ============================================================

import os
import json
from datetime import datetime
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """Tu es un assistant DevOps expert en analyse d'incidents.
Pour chaque log analysé, tu dois répondre en JSON strict avec ce format :
{
  "severity": "critical|warning|info",
  "errors": ["liste des erreurs détectées"],
  "root_cause": "cause racine probable",
  "fix": "correction recommandée en une phrase",
  "code_fix": "commande ou code à exécuter (optionnel)"
}
Ne réponds qu'avec le JSON, sans texte autour.
"""


def analyze_pipeline_log(log_content: str) -> dict:
    """Analyse un log de pipeline et retourne un diagnostic structuré."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyse ce log :\n\n{log_content}"}
        ],
        temperature=0.1,
        max_tokens=600,
    )
    raw = response.choices[0].message.content.strip()

    # Extraire le JSON même si entouré de markdown
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "severity": "warning",
            "errors": ["Réponse non parseable"],
            "root_cause": raw[:200],
            "fix": "Vérifiez manuellement le log",
            "code_fix": ""
        }


def print_diagnostic(diag: dict, log_source: str = ""):
    """Affiche le diagnostic de façon lisible."""
    severity_icons = {"critical": "🔴", "warning": "🟡", "info": "🟢"}
    icon = severity_icons.get(diag.get("severity", "info"), "⚪")

    print(f"\n{icon} Diagnostic — {diag.get('severity', '?').upper()}")
    if log_source:
        print(f"   Source : {log_source}")
    print("\n   🔍 Erreurs détectées :")
    for err in diag.get("errors", []):
        print(f"      • {err}")
    print(f"\n Cause racine : {diag.get('root_cause', '?')}")
    print(f"\n Correction : {diag.get('fix', '?')}")
    if diag.get("code_fix"):
        print("\n   📋 Commande :")
        print(f"      {diag['code_fix']}")


def human_validation(diag: dict) -> bool:
    """Demande validation humaine avant d'appliquer une correction."""
    if diag.get("severity") != "critical":
        return False

    print("\n" + "─" * 50)
    print("  VALIDATION HUMAINE REQUISE !!")
    print("─" * 50)
    print(f"Correction proposée : {diag.get('fix')}")
    if diag.get("code_fix"):
        print(f"Commande : {diag.get('code_fix')}")

    while True:
        choice = input("\nAppliquer cette correction ? [o/n] > ").strip().lower()
        if choice in ("o", "oui", "y", "yes"):
            return True
        if choice in ("n", "non", "no"):
            return False
        print("Répondez par o (oui) ou n (non)")


def apply_fix(code_fix: str):
    """Simule l'application d'une correction (mode démo)."""
    print("\n✅ Correction appliquée (simulation) :")
    print(f"   $ {code_fix}")
    # En production : subprocess.run(code_fix, shell=True)


def save_report(results: list):
    """Sauvegarde le rapport d'analyse."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_assistant/logs/report_{timestamp}.json"
    os.makedirs("ai_assistant/logs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n Rapport sauvegardé : {filename}")


def scan_log_files(log_dir: str = "ai_assistant/logs") -> list:
    """Scanne les fichiers de logs existants."""
    log_path = Path(log_dir)
    logs = []
    for f in sorted(log_path.glob("*.txt")):
        content = f.read_text(encoding="utf-8", errors="ignore")
        if content.strip():
            logs.append((str(f), content[:1500]))
    return logs


def main():
    print("\n" + "=" * 60)
    print(" Smart DevOps Assistant — Analyse automatique CI/CD")
    print("=" * 60)

    # Logs de démonstration si aucun log réel
    demo_logs = [
        (
            "pipeline_demo_1",
            """
            ERROR: Job failed: exit code 1
            $ pytest tests/ -v
            FAILED tests/test_database.py::test_insert - sqlalchemy.exc.OperationalError
            (psycopg.OperationalError) connection refused postgresql://localhost:5432
            collected 4 items / 1 error
            """
        ),
        (
            "pipeline_demo_2",
            """
            $ docker build -f docker/Dockerfile -t registry.gitlab.com/project:abc123 .
            ERROR: failed to solve: failed to read dockerfile:
            open /var/lib/docker/tmp/Dockerfile: no such file or directory
            ERROR: Job failed: exit code 1
            """
        ),
        (
            "pipeline_demo_3",
            """
            $ flake8 . --max-line-length=120
            ./main.py:15:1: F401 'os' imported but unused
            ./database/load.py:42:121: E501 line too long (135 > 120 characters)
            ERROR: Job failed: exit code 1
            """
        ),
    ]

    # Utiliser les vrais logs s'ils existent
    real_logs = scan_log_files()
    logs_to_analyze = real_logs if real_logs else demo_logs

    print(f"\n {len(logs_to_analyze)} log(s) à analyser\n")

    results = []
    for source, content in logs_to_analyze:
        print(f" Analyse : {source}")
        diag = analyze_pipeline_log(content)
        print_diagnostic(diag, source)

        # Validation humaine pour les erreurs critiques
        if diag.get("severity") == "critical" and diag.get("code_fix"):
            if human_validation(diag):
                apply_fix(diag["code_fix"])
            else:
                print("    Correction ignorée.")

        results.append({"source": source, "diagnostic": diag})

    save_report(results)

    # Résumé final
    critical = sum(1 for r in results if r["diagnostic"].get("severity") == "critical")
    warnings = sum(1 for r in results if r["diagnostic"].get("severity") == "warning")
    print(f"\n Résumé : {critical} critique(s), {warnings} warning(s), "
          f"{len(results) - critical - warnings} info(s)")
    print("\n Analyse terminée !")


if __name__ == "__main__":
    main()
