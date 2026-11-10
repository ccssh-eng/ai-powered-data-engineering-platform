# Runbook — Procédures d'exploitation

## Démarrage de la plateforme

### Ordre de démarrage
1. Démarrer PostgreSQL : docker compose up -d postgres
2. Attendre healthy : docker compose ps (STATUS: healthy)
3. Démarrer Airflow : docker compose -f docker-compose.airflow.yaml up -d
4. Vérifier les DAGs : http://localhost:8080

### Démarrage Kubernetes
1. minikube start
2. kubectl get pods -n ai-platform
3. kubectl get pods -n gitlab-agent

## Arrêt propre

```bash
docker compose down
docker compose -f docker-compose.airflow.yaml down
minikube stop
```

## Vérifications quotidiennes

### Santé des services
```bash
docker compose ps
kubectl get pods -n ai-platform
kubectl get cronjob -n ai-platform
```

### Dernière exécution du pipeline
```bash
docker logs ai_platform_airflow_scheduler --tail=50
kubectl get jobs -n ai-platform
```

### Connexion PostgreSQL
```bash
docker exec ai_platform_postgres psql -U data_engineer -d ai_platform -c "SELECT COUNT(*) FROM customers;"
```

## Procédures de récupération

### Redémarrer un service Docker
```bash
docker compose restart airflow-webserver
docker compose restart airflow-scheduler
```

### Redémarrer un pod Kubernetes
```bash
kubectl rollout restart deployment/customer-etl -n ai-platform
kubectl delete pod -l app=customer-etl -n ai-platform
```

### Reconstruire l'image minikube
```bash
eval $(minikube docker-env)
docker build -f docker/Dockerfile -t customer-etl:1.0 .
kubectl rollout restart deployment/customer-etl -n ai-platform
```

### Réinitialiser la base de données
```bash
docker exec ai_platform_postgres psql -U data_engineer -d ai_platform -c "TRUNCATE customers;"
```

## Monitoring

### Logs en temps réel
```bash
docker logs -f ai_platform_airflow_webserver
docker logs -f ai_platform_airflow_scheduler
kubectl logs -f deployment/customer-etl -n ai-platform
```

### Ressources
```bash
docker stats --no-stream
kubectl top pods -n ai-platform
```
