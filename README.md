```
#  AI-Powered Data Engineering Platform

Plateforme complète de data engineering avec IA générative, déployée sur Kubernetes et orchestrée par Apache Airflow.

##  Modules

| Module    | Contenu                 | Technologies                                   |
|-----------|-------------------------|------------------------------------------------|
| 1-2       | Pipeline ETL Python     | Python, PostgreSQL, JSONPlaceholder API        |
| 3         | Containerisation        | Docker, Docker Compose                         |
| 4         | Orchestration           | Kubernetes, minikube, CronJob                  |
| 5         | CI/CD                   | GitLab CI/CD, GitLab Agent (KAS)               |
| 6         | IA Générative           | Groq API, qwen/qwen3.8-27b                     |
| 7         | RAG                     | ChromaDB, SentenceTransformer                  |
| 8         | Industrialisation       | Prometheus, Grafana, Sécurisation              |

##  Architecture

```
GitLab CI/CD (test → lint → build → deploy)
        ↓
Docker Compose (postgres, airflow, prometheus, grafana)
        ↓
Pipeline ETL : JSONPlaceholder API → Extract → Transform → Load → PostgreSQL
        ↓
Kubernetes / minikube : CronJob customer-etl (toutes les heures)
        ↓
IA Générative : Groq API + RAG ChromaDB (58 chunks)
        ↓
Monitoring : Prometheus + Grafana dashboard PostgreSQL
```

##  Démarrage rapide

```bash
# 1. Cloner le projet

git clone git@gitlab.com:ssh-group2/ai-powered-data-engineering-platform.git
cd ai-powered-data-engineering-platform

# 2. Configurer les variables

cp .env.example .env

# Éditer .env avec vos clés

# 3. Démarrer la plateforme

export $(grep -v '^#' .env | xargs)
docker compose up -d

# 4. Vérifier

docker compose ps
```

##  Accès aux services

| Service    | URL                   |
|------------|-----------------------|
| Airflow    | http://localhost:8080 |
| Grafana    | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| PostgreSQL | localhost:5432        |

##  Assistant IA

```bash
# Assistant interactif
python3 ai_assistant/interactive_assistant.py

# Assistant RAG
python3 ai_assistant/rag/advanced_rag.py

# Assistant intelligent (diagnostic logs)
python3 ai_assistant/smart_devops_assistant.py

# Évaluation LLM
python3 ai_assistant/evaluation/llm_evaluator.py
```

##  Tests

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
flake8 . --max-line-length=120 --exclude=.venv,__pycache__,.git,airflow/logs
```

##  Démonstration complète

```bash
export $(grep -v '^#' .env | xargs)
python3 demo.py
```

Résultat attendu : **7/7 composants opérationnels **

##  Évaluation LLM

Score : **91.5% — EXCELLENT**

| Test | Catégorie   | Score |
|------|-------------|-------|
| T01 | Dockerfile   | 100%  |
| T02 | GitLab CI    | 100%  |
| T03 | Bash         | 90%   |
| T04 | Log Analysis | 67.5% |
| T05 | Kubernetes   | 100%  |

##  Sécurité

- Mots de passe forts générés avec `secrets.token_urlsafe`
- Network isolation Docker : `backend` / `monitoring`
- `.env` protégé par `.gitignore`
- Token API pour l'assistant IA

##  Structure du projet

```
├── ingestion/          # Extraction des données
├── transformation/     # Nettoyage et normalisation
├── database/           # Connexion et chargement PostgreSQL
├── airflow/            # DAGs Airflow
├── docker/             # Dockerfile
├── k8s/                # Manifests Kubernetes
├── ai_assistant/       # Assistants IA + RAG + Évaluation
├── monitoring/         # Prometheus + Grafana
├── tests/              # Tests pytest
├── demo.py             # Démonstration complète
└── ARCHITECTURE.md     # Documentation architecture
```

##  Auteur : Cédric SH — DevOps Data Engineer
```
