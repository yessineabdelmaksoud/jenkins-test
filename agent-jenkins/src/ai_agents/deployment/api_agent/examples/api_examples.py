"""Exemples d'utilisation de l'API AI Agents."""

import requests
import json
import time
from typing import Dict, Any


class AgentAPIClient:
    """Client pour interagir avec l'API AI Agents."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def list_agents(self) -> Dict[str, Any]:
        """Liste tous les agents disponibles."""
        response = self.session.get(f"{self.base_url}/api/agents")
        response.raise_for_status()
        return response.json()
    
    def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """Obtient les détails d'un agent."""
        response = self.session.get(f"{self.base_url}/api/agents/{agent_id}")
        response.raise_for_status()
        return response.json()
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Obtient la configuration d'un agent."""
        response = self.session.get(f"{self.base_url}/api/agents/{agent_id}/config")
        response.raise_for_status()
        return response.json()
    
    def run_agent(
        self, 
        agent_id: str, 
        input_data: Dict[str, Any], 
        config_override: Dict[str, Any] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """Lance l'exécution d'un agent."""
        payload = {
            "input_data": input_data,
            "config_override": config_override,
            "timeout": timeout
        }
        # Supprimer les valeurs None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        response = self.session.post(
            f"{self.base_url}/api/agents/{agent_id}/run",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_agent_status(self, agent_id: str, run_id: str = None) -> Dict[str, Any]:
        """Obtient le statut d'un agent."""
        url = f"{self.base_url}/api/agents/{agent_id}/status"
        if run_id:
            url += f"?run_id={run_id}"
        
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def list_agent_runs(self, agent_id: str) -> Dict[str, Any]:
        """Liste toutes les exécutions d'un agent."""
        response = self.session.get(f"{self.base_url}/api/agents/{agent_id}/runs")
        response.raise_for_status()
        return response.json()

    def get_run_details(self, agent_id: str, run_id: str) -> Dict[str, Any]:
        """Obtient les détails d'une exécution."""
        response = self.session.get(f"{self.base_url}/api/agents/{agent_id}/runs/{run_id}")
        response.raise_for_status()
        return response.json()
    
    def cancel_run(self, agent_id: str, run_id: str) -> Dict[str, Any]:
        """Annule une exécution."""
        response = self.session.delete(f"{self.base_url}/api/agents/{agent_id}/runs/{run_id}")
        response.raise_for_status()
        return response.json()


def example_basic_usage():
    """Exemple d'utilisation basique de l'API."""
    print("🔍 Exemple d'utilisation basique de l'API")
    print("=" * 50)
    
    client = AgentAPIClient()
    
    try:
        # 1. Lister tous les agents
        print("\n1. Liste des agents disponibles:")
        agents = client.list_agents()
        print(f"   Nombre d'agents: {agents['total']}")
        for agent in agents['agents']:
            print(f"   - {agent['id']}: {agent['name']} ({agent['type']})")
        
        # 2. Obtenir les détails d'un agent spécifique
        agent_id = "sales_assistant"
        print(f"\n2. Détails de l'agent '{agent_id}':")
        details = client.get_agent_details(agent_id)
        print(f"   Nom: {details['name']}")
        print(f"   Type: {details['type']}")
        print(f"   Statut: {details['status']}")
        print(f"   Description: {details['description']}")
        
        # 3. Obtenir la configuration
        print(f"\n3. Configuration de l'agent '{agent_id}':")
        config = client.get_agent_config(agent_id)
        print(f"   Workflow: {config['workflow'].get('entrypoint', 'N/A')}")
        print(f"   Modèle: {config.get('model', {}).get('model_id', 'N/A')}")
        
        # 4. Lancer l'agent
        print(f"\n4. Lancement de l'agent '{agent_id}':")
        input_data = {
            "customer_query": "Je cherche des informations sur vos produits"
        }
        run_result = client.run_agent(agent_id, input_data)
        run_id = run_result['run_id']
        print(f"   Run ID: {run_id}")
        print(f"   Statut: {run_result['status']}")
        
        # 5. Surveiller l'exécution
        print(f"\n5. Surveillance de l'exécution:")
        max_attempts = 10
        final_status = None

        for attempt in range(max_attempts):
            status = client.get_agent_status(agent_id, run_id)
            current_status = status.get('status', 'unknown')
            print(f"   Tentative {attempt + 1}: {current_status}")

            # Vérifier s'il y a une exécution en cours
            if status.get('current_run'):
                current_run = status['current_run']
                print(f"      Run status: {current_run.get('status', 'unknown')}")
                if current_run.get('logs'):
                    print(f"      Logs: {len(current_run['logs'])} entrées")

                if current_run.get('status') in ['completed', 'failed', 'cancelled']:
                    final_status = current_run
                    break

            if current_status in ['completed', 'failed', 'cancelled']:
                break

            time.sleep(2)

        # 6. Obtenir les résultats finaux
        print(f"\n6. Résultats finaux:")

        # Essayer d'abord de lister toutes les exécutions
        try:
            all_runs = client.list_agent_runs(agent_id)
            print(f"   Nombre total d'exécutions: {len(all_runs)}")

            # Chercher notre exécution
            our_run = None
            for run in all_runs:
                if run['run_id'] == run_id:
                    our_run = run
                    break 

            if our_run:
                print(f"   ✅ Exécution trouvée dans la liste")
                print(f"   Statut final: {our_run['status']}")
                if our_run.get('result'):
                    print(f"   Résultat: {our_run['result']}")
                if our_run.get('error'):
                    print(f"   Erreur: {our_run['error']}")
                print(f"   Logs: {len(our_run.get('logs', []))} entrées")
            else:
                print(f"   ⚠️  Exécution {run_id} non trouvée dans la liste")

        except Exception as e:
            print(f"   ⚠️  Erreur lors de la récupération de la liste: {e}")

            # Fallback: essayer de récupérer directement
            try:
                final_details = client.get_run_details(agent_id, run_id)
                print(f"   ✅ Détails récupérés directement")
                print(f"   Statut final: {final_details['status']}")
                if final_details.get('result'):
                    print(f"   Résultat: {final_details['result']}")
                if final_details.get('error'):
                    print(f"   Erreur: {final_details['error']}")
                print(f"   Logs: {len(final_details.get('logs', []))} entrées")
            except Exception as e2:
                print(f"   ❌ Impossible de récupérer les détails: {e2}")
                if final_status:
                    print(f"   📊 Utilisation du dernier statut connu: {final_status.get('status')}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def example_advanced_usage():
    """Exemple d'utilisation avancée avec surcharge de configuration."""
    print("\n🚀 Exemple d'utilisation avancée")
    print("=" * 50)
    
    client = AgentAPIClient()
    
    try:
        agent_id = "sales_assistant"
        
        # Configuration personnalisée
        config_override = {
            "model": {
                "temperature": 0.9,
                "max_tokens": 500
            }
        }
        
        input_data = {
            "customer_query": "Quels sont vos meilleurs produits pour une startup ?",
            "customer_context": {
                "industry": "technology",
                "size": "startup",
                "budget": "limited"
            }
        }
        
        print(f"Lancement avec configuration personnalisée:")
        print(f"   Input: {input_data}")
        print(f"   Config override: {config_override}")
        
        # Lancer avec timeout personnalisé
        run_result = client.run_agent(
            agent_id, 
            input_data, 
            config_override=config_override,
            timeout=60
        )
        
        run_id = run_result['run_id']
        print(f"   Run ID: {run_id}")
        
        # Surveiller avec plus de détails
        while True:
            status = client.get_agent_status(agent_id, run_id)
            current_run = status.get('current_run')
            
            if current_run:
                print(f"   Statut: {current_run['status']}")
                if current_run.get('logs'):
                    print(f"   Derniers logs: {current_run['logs'][-1]}")
                
                if current_run['status'] in ['completed', 'failed', 'cancelled']:
                    break
            
            time.sleep(1)
        
        print("✅ Exécution terminée")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def example_error_handling():
    """Exemple de gestion d'erreurs."""
    print("\n⚠️  Exemple de gestion d'erreurs")
    print("=" * 50)
    
    client = AgentAPIClient()
    
    # Test avec un agent inexistant
    try:
        print("Test avec un agent inexistant:")
        client.get_agent_details("agent_inexistant")
    except requests.exceptions.HTTPError as e:
        print(f"   ✅ Erreur attendue: {e.response.status_code} - {e.response.text}")
    
    # Test avec des données invalides
    try:
        print("\nTest avec des données invalides:")
        client.run_agent("sales_assistant", "données_invalides")
    except requests.exceptions.HTTPError as e:
        print(f"   ✅ Erreur attendue: {e.response.status_code}")
    except Exception as e:
        print(f"   ✅ Erreur attendue: {e}")


if __name__ == "__main__":
    print("🤖 Exemples d'utilisation de l'API AI Agents")
    print("=" * 60)
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API accessible")
            
            example_basic_usage()
            example_advanced_usage()
            example_error_handling()
            
        else:
            print("❌ API non accessible")
    except requests.exceptions.RequestException:
        print("❌ Impossible de se connecter à l'API")
        print("   Assurez-vous que l'API est démarrée avec:")
        print("   python src/ai_agents/deployment/api_agent/start_api.py")
