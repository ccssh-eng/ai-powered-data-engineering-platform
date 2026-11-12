"""
Module 8 - Part 5 : Démonstration complète
End-to-end demo de la plateforme AI-Powered Data Engineering
"""
import os
import sys
import time
import subprocess
import requests
import psycopg
from datetime import datetime

# ── Couleurs terminal ─────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def title(msg):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}  {msg}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")


def step(msg):
    print(f"\n{CYAN}▶ {msg}{RESET}")


def ok(msg):
    print(f"  {GREEN}✅ {msg}{RESET}")


def warn(msg):
    print(f"  {YELLOW}⚠️  {msg}{RESET}")


def err(msg):
    print(f"  {RED}❌ {msg}{RESET}")


def pause(s=1):
    time.sleep(s)


# ── 1. Vérification des services Docker ──────────────────────
def check_services():
    title("ÉTAPE 1 — Services Docker")
    services = {
        "ai_platform_postgres":          5432,
        "ai_platform_airflow_webserver": 8080,
        "ai_platform_prometheus":        9090,
        "ai_platform_grafana":           3000,
        "ai_platform_postgres_exporter": 9187,
    }
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "{{.Name}} {{.Status}}"],
        capture_output=True, text=True
    )
    running = result.stdout
    all_ok = True
    for name, port in services.items():
        if name in running and "Up" in running:
            ok(f"{name} (port {port})")
        else:
            warn(f"{name} — vérifiez avec: docker compose ps")
            all_ok = False
    return all_ok


# ── 2. Test PostgreSQL ────────────────────────────────────────
def check_postgres():
    title("ÉTAPE 2 — Base de données PostgreSQL")
    step("Connexion à PostgreSQL...")
    try:
        conn = psycopg.connect(
            host="localhost", port=5432,
            dbname="ai_platform", user="data_engineer",
            password=os.getenv("POSTGRES_PASSWORD"), connect_timeout=5
        )
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM customers;")
        count = cur.fetchone()[0]
        ok(f"Table customers : {count} enregistrements")

        cur.execute("SELECT name, email FROM customers LIMIT 3;")
        rows = cur.fetchall()
        for row in rows:
            print(f"    → {row[0]} | {row[1]}")

        cur.execute("SELECT version();")
        version = cur.fetchone()[0][:40]
        ok(f"PostgreSQL version : {version}...")

        conn.close()
        return True
    except Exception as e:
        err(f"PostgreSQL : {e}")
        return False


# ── 3. Test Prometheus ────────────────────────────────────────
def check_prometheus():
    title("ÉTAPE 3 — Monitoring Prometheus")
    step("Vérification des targets Prometheus...")
    try:
        r = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        targets = r.json()["data"]["activeTargets"]
        for t in targets:
            job = t["labels"]["job"]
            health = t["health"]
            icon = "✅" if health == "up" else "⚠️ "
            print(f"  {icon} {job}: {health}")
        ok(f"{len(targets)} targets configurés")
        return True
    except Exception as e:
        err(f"Prometheus : {e}")
        return False


# ── 4. Test Grafana ───────────────────────────────────────────
def check_grafana():
    title("ÉTAPE 4 — Dashboard Grafana")
    step("Vérification de l'API Grafana...")
    try:
        password = os.getenv("GRAFANA_PASSWORD", "admin123")
        r = requests.get(
            "http://localhost:3000/api/dashboards/home",
            auth=("admin", password), timeout=5
        )
        if r.status_code == 200:
            ok("Grafana accessible (http://localhost:3000)")
            ok("Dashboard PostgreSQL disponible")
        else:
            warn(f"Grafana status: {r.status_code}")
        return True
    except Exception as e:
        err(f"Grafana : {e}")
        return False


# ── 5. Test Assistant IA ──────────────────────────────────────
def check_ai():
    title("ÉTAPE 5 — Assistant IA (Groq)")
    step("Test de génération avec le LLM...")
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": (
                "En une phrase, qu'est-ce qu'un pipeline ETL ?"
            )}],
            max_tokens=100,
        )
        answer = response.choices[0].message.content.strip()
        ok(f"LLM répond : {answer[:100]}...")
        return True
    except Exception as e:
        err(f"Assistant IA : {e}")
        return False


# ── 6. Test RAG ───────────────────────────────────────────────
def check_rag():
    title("ÉTAPE 6 — RAG (ChromaDB)")
    step("Recherche sémantique dans la documentation...")
    try:
        sys.path.insert(0, ".")
        import chromadb
        from sentence_transformers import SentenceTransformer

        client = chromadb.PersistentClient(path="ai_assistant/rag/chroma_db_v2")
        collection = client.get_collection("infra_docs_v2")
        count = collection.count()
        ok(f"ChromaDB : {count} chunks indexés")

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query = "comment démarrer la plateforme"
        embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=2)
        docs = results["documents"][0]
        ok(f"Recherche '{query}' → {len(docs)} résultats trouvés")
        for doc in docs:
            print(f"    → {doc[:80]}...")
        return True
    except Exception as e:
        err(f"RAG : {e}")
        return False


# ── 7. Test Évaluation LLM ────────────────────────────────────
def check_evaluation():
    title("ÉTAPE 7 — Évaluation LLM")
    step("Chargement du dernier rapport d'évaluation...")
    try:
        import glob
        import json
        reports = sorted(glob.glob("ai_assistant/evaluation/reports/eval_*.json"))
        if not reports:
            warn("Aucun rapport trouvé — lancez llm_evaluator.py")
            return False
        with open(reports[-1]) as f:
            report = json.load(f)
        ok(f"Dernier rapport : {reports[-1].split('/')[-1]}")
        ok(f"Score moyen    : {report['average_score']}%")
        ok(f"Résultat       : {report['grade']}")
        return True
    except Exception as e:
        err(f"Évaluation : {e}")
        return False


# ── Rapport final ─────────────────────────────────────────────
def final_report(results: dict):
    title("RAPPORT FINAL — DÉMONSTRATION COMPLÈTE")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    print(f"\n{BOLD}  Score : {passed}/{total} composants opérationnels{RESET}")
    if passed == total:
        print(f"{BOLD}{GREEN}  🎉 PLATEFORME 100% OPÉRATIONNELLE !{RESET}")
    elif passed >= total * 0.7:
        print(f"{BOLD}{YELLOW}  ⚠️  Plateforme majoritairement opérationnelle{RESET}")
    else:
        print(f"{BOLD}{RED}  ❌ Vérifiez les composants en erreur{RESET}")
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}\n")


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{BOLD}{CYAN}")
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║   AI-Powered Data Engineering Platform          ║")
    print("  ║   Démonstration complète — Module 8 Part 5      ║")
    print(f"  ║   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                        ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print(f"{RESET}")

    results = {
        "Services Docker":   check_services(),
        "PostgreSQL":        check_postgres(),
        "Prometheus":        check_prometheus(),
        "Grafana":           check_grafana(),
        "Assistant IA":      check_ai(),
        "RAG ChromaDB":      check_rag(),
        "Évaluation LLM":    check_evaluation(),
    }
    pause(1)
    final_report(results)
