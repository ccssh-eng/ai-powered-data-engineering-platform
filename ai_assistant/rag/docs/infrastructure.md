# Documentation Infrastructure — AI-Powered Data Engineering Platform

## Architecture globale

La plateforme est composée de 4 couches :
1. **Ingestion** : extraction des données depuis JSONPlaceholder API
2. **Transformation** : nettoyage et validation des données clients
3. **Stockage** : PostgreSQL 16 avec schéma optimisé
4. **Orchestration** : Apache Airflow 2.10.5 avec DAG customer_etl_pipeline

## Services Docker Compose

### PostgreSQL
- Image : postgres:16
- Port : 5432
- Base de données : ai_platform
- Utilisateur : data_engineer
- Health check : pg_isready toutes les 5 secondes

### Airflow Webserver
- Image : apache/airflow:2.10.5-python3.10
- Port : 8080
- Mémoire limite : 1024m
- URL : http://localhost:8080

### Airflow Scheduler
- Image : apache/airflow:2.10.5-python3.10
- Mémoire limite : 896m
- DAGs montés depuis : ./airflow/dags/

## Pipeline ETL

### Étapes du pipeline
1. check_database — vérifie la connectivité PostgreSQL
2. create_tables — crée les tables si inexistantes
3. extract — récupère 10 clients depuis JSONPlaceholder
4. transform — valide emails, normalise les noms
5. load — upsert idempotent dans PostgreSQL
6. end — confirmation de fin

### Règles de transformation
- Email manquant → enregistrement rejeté
- Nom avec espaces → strip()
- Email en majuscules → lower()
- Enregistrements None/invalides → filtrés

## Kubernetes (minikube)

### Namespace
- Nom : ai-platform

### Ressources déployées
- Deployment : customer-etl (image locale minikube)
- CronJob : customer-etl-cronjob (schedule: 0 * * * *)
- ConfigMap : etl-config (POSTGRES_HOST, PORT, DB, USER)
- Secret : etl-secret (POSTGRES_PASSWORD en base64)
- Service : postgres-service → Endpoints 192.168.49.1:5432

### GitLab Agent
- Nom : minikube-agent
- Namespace : gitlab-agent
- Connexion : wss://kas.gitlab.com

## CI/CD GitLab

### Stages
1. test — pytest avec SQLite in-memory
2. lint — flake8 max-line-length=120
3. build — Docker image vers registry.gitlab.com
4. deploy — kubectl via GitLab Agent

### Variables CI/CD
- CI_REGISTRY_USER / CI_REGISTRY_PASSWORD : automatiques
- GROQ_API_KEY : clé API Groq (masquée)

## Incidents connus et solutions

### PostgreSQL non accessible depuis K8s
- Cause : minikube utilise un réseau isolé
- Solution : Service + Endpoints pointant vers 192.168.49.1 (IP hôte minikube)

### Airflow DAG non visible
- Cause : permissions dossier dags/ (propriétaire 50000)
- Solution : sudo chown 50000:0 airflow/dags/ && chmod 775 airflow/dags/

### Airflow crash après 2 minutes
- Cause : mem_limit trop bas (768m)
- Solution : augmenter à 1024m webserver, 896m scheduler

### flake8 F401 import inutilisé
- Cause : import os ou json non utilisé
- Solution : supprimer la ligne d'import

### Docker build Dockerfile not found
- Cause : Dockerfile dans docker/ et non à la racine
- Solution : docker build -f docker/Dockerfile ...
