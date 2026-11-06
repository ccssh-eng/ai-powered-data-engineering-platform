# ============================================================
# Dockerfile — Customer ETL Pipeline
# Module 4 – Docker et Kubernetes
# Auteur : Cédric SH
# ============================================================

# ── Étape 1 : image de base légère ──────────────────────────
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="Cédric SH"
LABEL description="Customer ETL Pipeline — JSONPlaceholder → PostgreSQL"
LABEL version="1.0"

# ── Étape 2 : variables d'environnement ─────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# ── Étape 3 : répertoire de travail ─────────────────────────
WORKDIR /app

# ── Étape 4 : installation des dépendances ──────────────────
# Copier uniquement requirements.txt d'abord (cache Docker)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Étape 5 : copie du code source ──────────────────────────
COPY ingestion/   ./ingestion/
COPY transformation/ ./transformation/
COPY database/    ./database/
COPY main.py      .

# ── Étape 6 : utilisateur non-root (sécurité) ───────────────
RUN useradd --create-home --shell /bin/bash etl_user && \
    chown -R etl_user:etl_user /app

USER etl_user

# ── Étape 7 : commande de démarrage ─────────────────────────
CMD ["python", "main.py"]
