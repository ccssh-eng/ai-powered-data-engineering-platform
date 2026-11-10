"""
Module 8 - Part 3 : Évaluation des réponses du LLM
Teste la qualité, pertinence et format des réponses de l'assistant IA.
"""
import os
import json
import time
from datetime import datetime
from groq import Groq

# ── Client Groq ──────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "qwen/qwen3.8-27b"


def ask_llm(prompt: str) -> str:
    """Envoie une question au LLM et retourne la réponse."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def evaluate_response(question: str, response: str, expected_keywords: list) -> dict:
    """Évalue une réponse selon 3 critères."""
    # Critère 1 : mots-clés présents
    response_lower = response.lower()
    keywords_found = [kw for kw in expected_keywords if kw.lower() in response_lower]
    keyword_score = len(keywords_found) / len(expected_keywords) if expected_keywords else 0

    # Critère 2 : longueur minimale (réponse substantielle)
    length_score = min(len(response) / 200, 1.0)

    # Critère 3 : pas de réponse vide ou d'erreur
    quality_score = 0.0 if not response or "error" in response.lower()[:50] else 1.0

    total = round((keyword_score * 0.5 + length_score * 0.3 + quality_score * 0.2) * 100, 1)

    return {
        "keyword_score": round(keyword_score * 100, 1),
        "length_score": round(length_score * 100, 1),
        "quality_score": round(quality_score * 100, 1),
        "total_score": total,
        "keywords_found": keywords_found,
        "response_length": len(response),
    }


# ── Jeux de tests ─────────────────────────────────────────────
TEST_CASES = [
    {
        "id": "T01",
        "category": "Dockerfile",
        "question": "Génère un Dockerfile Python 3.10 pour une application Flask avec gunicorn.",
        "expected_keywords": ["FROM", "python", "COPY", "RUN", "pip", "CMD", "gunicorn"],
    },
    {
        "id": "T02",
        "category": "GitLab CI",
        "question": "Génère un pipeline GitLab CI avec les stages test, build et deploy.",
        "expected_keywords": ["stages", "test", "build", "deploy", "script", "image"],
    },
    {
        "id": "T03",
        "category": "Bash",
        "question": "Génère un script bash pour sauvegarder une base PostgreSQL avec pg_dump.",
        "expected_keywords": ["pg_dump", "bash", "PGPASSWORD", "backup", "date"],
    },
    {
        "id": "T04",
        "category": "Log Analysis",
        "question": (
            "Analyse ce log d'erreur et donne le diagnostic en JSON : "
            "'ERROR: connection refused to postgres:5432 after 3 retries'"
        ),
        "expected_keywords": ["postgres", "connection", "error", "fix"],
    },
    {
        "id": "T05",
        "category": "Kubernetes",
        "question": "Explique la différence entre un Deployment et un CronJob Kubernetes.",
        "expected_keywords": ["deployment", "cronjob", "pod", "schedule", "replica"],
    },
]


def run_evaluation():
    """Lance tous les tests et génère le rapport."""
    print("\n" + "=" * 60)
    print("  ÉVALUATION LLM — AI-Powered Data Engineering Platform")
    print("=" * 60)
    print(f"  Modèle : {MODEL}")
    print(f"  Date   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Tests  : {len(TEST_CASES)}")
    print("=" * 60 + "\n")

    results = []

    for tc in TEST_CASES:
        print(f"[{tc['id']}] {tc['category']} ... ", end="", flush=True)
        try:
            start = time.time()
            response = ask_llm(tc["question"])
            elapsed = round(time.time() - start, 2)
            metrics = evaluate_response(tc["question"], response, tc["expected_keywords"])
            metrics["elapsed_s"] = elapsed
            metrics["status"] = "OK"
            print(f"Score: {metrics['total_score']}% ({elapsed}s)")
        except Exception as e:
            metrics = {
                "keyword_score": 0, "length_score": 0, "quality_score": 0,
                "total_score": 0, "keywords_found": [], "response_length": 0,
                "elapsed_s": 0, "status": f"ERROR: {e}",
            }
            print(f"ERREUR: {e}")
            response = ""

        results.append({
            "id": tc["id"],
            "category": tc["category"],
            "question": tc["question"][:80] + "...",
            "metrics": metrics,
            "response_preview": response[:200] if response else "",
        })
        time.sleep(2)  # éviter rate limit

    # ── Rapport final ─────────────────────────────────────────
    scores = [r["metrics"]["total_score"] for r in results if r["metrics"]["status"] == "OK"]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    print("\n" + "=" * 60)
    print("  RAPPORT FINAL")
    print("=" * 60)
    for r in results:
        status = "✅" if r["metrics"]["total_score"] >= 60 else "⚠️"
        print(f"  {status} [{r['id']}] {r['category']:15s} → {r['metrics']['total_score']}%")
    print(f"\n  Score moyen : {avg_score}%")
    grade = "EXCELLENT" if avg_score >= 80 else "BON" if avg_score >= 60 else "À AMÉLIORER"
    print(f"  Résultat   : {grade}")
    print("=" * 60)

    # Sauvegarde JSON
    report = {
        "model": MODEL,
        "date": datetime.now().isoformat(),
        "average_score": avg_score,
        "grade": grade,
        "results": results,
    }
    os.makedirs("ai_assistant/evaluation/reports", exist_ok=True)
    report_path = f"ai_assistant/evaluation/reports/eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  Rapport sauvegardé : {report_path}\n")
    return avg_score


if __name__ == "__main__":
    run_evaluation()
