# AI Agents API

API REST pour gérer et exécuter des agents IA basés sur LangGraph.

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```bash
# Installer les dépendances avec Poetry
poetry install

# Ou avec pip
pip install fastapi uvicorn pydantic-settings
```

### 2. Configuration

Créez un fichier `.env` dans le répertoire racine :

```env
PYTHONPATH=src
OPENAI_API_KEY=your-openai-api-key-here

# Configuration API (optionnel)
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### 3. Démarrage du serveur

```bash
# Méthode 1: Démarrage rapide avec démonstration
python src/ai_agents/deployment/api_agent/quick_start.py

# Méthode 2: Script de démarrage simple
python src/ai_agents/deployment/api_agent/start_api.py

# Méthode 3: Test de configuration
python src/ai_agents/deployment/api_agent/test_config.py

# Méthode 4: Uvicorn direct
uvicorn ai_agents.deployment.api_agent.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Accès à la documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 Endpoints disponibles

### Gestion des agents

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/agents` | Liste tous les agents disponibles |
| `GET` | `/api/agents/{agent_id}` | Informations détaillées sur un agent |
| `GET` | `/api/agents/{agent_id}/config` | Configuration actuelle d'un agent |
| `POST` | `/api/agents/{agent_id}/run` | Lance l'exécution d'un agent |
| `GET` | `/api/agents/{agent_id}/status` | Statut actuel d'un agent |

### Gestion des exécutions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/agents/{agent_id}/runs/{run_id}` | Détails d'une exécution spécifique |
| `DELETE` | `/api/agents/{agent_id}/runs/{run_id}` | Annule une exécution en cours |

## 🔧 Exemples d'utilisation

### 1. Lister les agents

```bash
curl -X GET "http://localhost:8000/api/agents"
```

```json
{
  "agents": [
    {
      "id": "sales_assistant",
      "name": "Sales Assistant",
      "type": "sales_assistant",
      "description": "Agent sales_assistant for specialized tasks",
      "version": "1.0.0",
      "status": "idle"
    }
  ],
  "total": 1
}
```

### 2. Obtenir les détails d'un agent

```bash
curl -X GET "http://localhost:8000/api/agents/sales_assistant"
```

### 3. Lancer un agent

```bash
curl -X POST "http://localhost:8000/api/agents/sales_assistant/run" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "customer_query": "Je cherche des informations sur vos produits"
    },
    "timeout": 60
  }'
```

```json
{
  "run_id": "123e4567-e89b-12d3-a456-426614174000",
  "agent_id": "sales_assistant",
  "status": "running",
  "started_at": "2024-01-15T10:30:00Z",
  "logs": []
}
```

### 4. Vérifier le statut

```bash
curl -X GET "http://localhost:8000/api/agents/sales_assistant/status?run_id=123e4567-e89b-12d3-a456-426614174000"
```

## 🛠️ Scripts utilitaires

### Scripts de démarrage et test

| Script | Description |
|--------|-------------|
| `quick_start.py` | Démarrage rapide avec vérifications et démonstration |
| `start_api.py` | Démarrage simple du serveur API |
| `test_config.py` | Test de la configuration sans démarrer le serveur |
| `demo.py` | Démonstration complète des fonctionnalités API |

### Utilisation des scripts

```bash
# Démarrage rapide recommandé (avec démo)
python src/ai_agents/deployment/api_agent/quick_start.py

# Démonstration seule (serveur doit être déjà démarré)
python src/ai_agents/deployment/api_agent/demo.py

# Test de configuration
python src/ai_agents/deployment/api_agent/test_config.py
```

## 🐍 Client Python

Utilisez le client Python fourni pour une intégration facile :

```python
from ai_agents.deployment.api_agent.examples.api_examples import AgentAPIClient

# Initialiser le client
client = AgentAPIClient("http://localhost:8000")

# Lister les agents
agents = client.list_agents()
print(f"Agents disponibles: {len(agents['agents'])}")

# Lancer un agent
result = client.run_agent(
    "sales_assistant",
    {"customer_query": "Bonjour, j'ai besoin d'aide"}
)

# Surveiller l'exécution
status = client.get_agent_status("sales_assistant", result['run_id'])
print(f"Statut: {status['status']}")
```

## 📊 Modèles de données

### AgentRunRequest

```json
{
  "input_data": {
    "customer_query": "string",
    "additional_context": {}
  },
  "config_override": {
    "model": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  },
  "timeout": 300
}
```

### AgentRunResponse

```json
{
  "run_id": "uuid",
  "agent_id": "string",
  "status": "running|completed|failed|cancelled",
  "started_at": "datetime",
  "completed_at": "datetime|null",
  "result": {},
  "error": "string|null",
  "logs": ["string"]
}
```

## ⚙️ Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `HOST` | Adresse d'écoute | `0.0.0.0` |
| `PORT` | Port d'écoute | `8000` |
| `DEBUG` | Mode debug | `false` |
| `LOG_LEVEL` | Niveau de log | `INFO` |
| `MAX_EXECUTION_TIME` | Timeout max (secondes) | `300` |
| `ALLOWED_HOSTS` | Hosts CORS autorisés | `["*"]` |

### Configuration des agents

Les agents sont automatiquement découverts depuis le registre `AGENT_REGISTRY`. Chaque agent doit :

1. Être enregistré dans `ai_agents.agents.registry`
2. Hériter de `AgentBase` ou `WorkflowAgent`
3. Avoir un fichier de configuration YAML valide

## 🔍 Monitoring et logs

### Logs structurés

L'API génère des logs structurés pour :
- Démarrage/arrêt du serveur
- Exécutions d'agents
- Erreurs et exceptions
- Requêtes HTTP

### Health check

```bash
curl -X GET "http://localhost:8000/health"
```

```json
{
  "status": "healthy"
}
```

## 🚨 Gestion d'erreurs

### Codes d'erreur HTTP

| Code | Description |
|------|-------------|
| `200` | Succès |
| `400` | Requête invalide |
| `404` | Agent/Run non trouvé |
| `500` | Erreur serveur |

### Format des erreurs

```json
{
  "error": "Message d'erreur principal",
  "detail": "Détails supplémentaires",
  "code": "ERROR_CODE"
}
```

## 🔧 Développement

### Structure du projet

```
api_agent/
├── main.py              # Application FastAPI principale
├── start_api.py         # Script de démarrage
├── core/                # Configuration et utilitaires
│   ├── config.py        # Settings Pydantic
│   └── logging.py       # Configuration des logs
├── api/                 # Routes et modèles API
│   ├── models/          # Modèles Pydantic
│   └── routes/          # Endpoints FastAPI
├── services/            # Logique métier
│   └── agent_service.py # Service de gestion des agents
└── examples/            # Exemples d'utilisation
    └── api_examples.py  # Client Python et exemples
```

### Tests

```bash
# Lancer les exemples
python src/ai_agents/deployment/api_agent/examples/api_examples.py

# Tests manuels avec curl
curl -X GET "http://localhost:8000/api/agents"
```

## 📝 TODO

- [ ] Authentification et autorisation
- [ ] Persistance des exécutions en base de données
- [ ] Streaming des logs en temps réel
- [ ] Métriques et monitoring avancé
- [ ] Tests unitaires et d'intégration
- [ ] Documentation OpenAPI enrichie
- [ ] Support WebSocket pour les notifications
- [ ] Rate limiting et throttling
