# AI-Powered Data Engineering Platform — Documentation Architecture

## Vue d'ensemble

Plateforme complète de data engineering avec IA générative, déployée sur Kubernetes et orchestrée par Apache Airflow.

---

## Modules

### Module 1-2 — Pipeline ETL Python
- **Source** : JSONPlaceholder API (clients fictifs)
- **Extraction** : `ingestion/extract.py`
- **Transformation** : `transformation/transform.py` (nettoyage, normalisation)
- **Chargement** : `database/load.py` → PostgreSQL 16
- **Tests** : pytest + SQLite in-memory (CI)

### Module 3 — Containerisation Docker
- `docker/Dockerfile` multi-stage Python 3.10
- `docker-compose.yml` : postgres, airflow-webserver, airflow-scheduler
- Healthcheck PostgreSQL avant démarrage Airflow

### Module 4 — Kubernetes / minikube
- Namespace : `ai-platform`
- CronJob `customer-etl-cronjob` (toutes les heures)
- ConfigMap + Secret pour la configuration
- Service ExternalName → PostgreSQL host (192.168.49.1:5432)

### Module 5 — CI/CD GitLab
- 4 stages : `test` → `lint` → `build` → `deploy`
- GitLab Agent (KAS) pour déploiement sur minikube local
- Registry : `registry.gitlab.com/ssh-group2/ai-powered-data-engineering-platform`
- Flake8 : max-line-length=120

### Module 6 — IA Générative (Groq API)
- Modèle : `qwen/qwen3.8-27b` (max_tokens=800)
- `devops_assistant.py` : génération Dockerfile, pipeline, bash, analyse logs
- `interactive_assistant.py` : chat avec historique de session
- `smart_devops_assistant.py` : diagnostic JSON + validation humaine

### Module 7 — RAG (Retrieval-Augmented Generation)
- ChromaDB v2 : `ai_assistant/rag/chroma_db_v2`
- SentenceTransformer : `all-MiniLM-L6-v2`
- 58 chunks indexés (section-based + word-based avec overlap)
- Filtre de pertinence : distance < 1.5
- Docs : `infrastructure.md`, `runbook.md`

### Module 8 — Industrialisation
- **Monitoring** : Prometheus v2.47.0 + Grafana 10.1.0 + postgres-exporter
- **Sécurisation** : network isolation (backend/monitoring), secrets forts, AI_API_TOKEN
- **Évaluation LLM** : 5 tests automatisés, score 91.5% EXCELLENT
- **Documentation** : ce fichier

---

## Stack technique

| Composant | Version |
|-----------|---------|
| Python | 3.10 |
| PostgreSQL | 16 |
| Apache Airflow | 2.10.5 |
| Docker | 24+ |
| Kubernetes | 1.28 (minikube) |
| GitLab CI/CD | Agent KAS |
| Groq API | qwen/qwen3.8-27b |
| ChromaDB | v2 |
| Prometheus | 2.47.0 |
| Grafana | 10.1.0 |

---

## Réseaux Docker

backend : postgres ←→ postgres-exporter
monitoring : prometheus ←→ grafana ←→ postgres-exporter


Grafana n'a pas accès direct à PostgreSQL (isolation réseau).

---

## Variables d'environnement (.env)

POSTGRES_PASSWORD=<token_urlsafe_32>
GRAFANA_PASSWORD=<token_urlsafe_16>
GROQ_API_KEY=<groq_api_key>
AI_API_TOKEN=<token_urlsafe_32>


---

## Lancer la plateforme

```bash
# 1. Démarrer les services
export $(grep -v '^#' .env | xargs)
docker compose up -d

# 2. Vérifier
docker compose ps

# 3. Accès
# Airflow   : http://localhost:8080
# Grafana   : http://localhost:3000
# Prometheus: http://localhost:9090

# 4. Lancer l'assistant IA
python3 ai_assistant/interactive_assistant.py

# 5. Lancer le RAG
python3 ai_assistant/rag/advanced_rag.py

# 6. Évaluation LLM
python3 ai_assistant/evaluation/llm_evaluator.py
```

