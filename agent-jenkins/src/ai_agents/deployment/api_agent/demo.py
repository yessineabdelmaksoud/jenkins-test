#!/usr/bin/env python3
"""Démonstration complète de l'API AI Agents."""

import sys
import time
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from ai_agents.deployment.api_agent.examples.api_examples import AgentAPIClient


def demo_api_complete():
    """Démonstration complète de l'API."""
    print("🤖 Démonstration complète de l'API AI Agents")
    print("=" * 60)
    
    client = AgentAPIClient()
    
    try:
        # Vérifier que l'API est accessible
        print("🔍 Vérification de l'API...")
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                print("❌ API non accessible. Démarrez-la avec:")
                print("   python src/ai_agents/deployment/api_agent/start_api.py")
                return False
            print("✅ API accessible")
        except Exception:
            print("❌ Impossible de se connecter à l'API")
            print("   Démarrez l'API avec:")
            print("   python src/ai_agents/deployment/api_agent/start_api.py")
            return False
        
        # 1. Lister tous les agents
        print("\n📋 1. Liste des agents disponibles:")
        agents = client.list_agents()
        print(f"   Nombre d'agents: {agents['total']}")
        for agent in agents['agents']:
            print(f"   🤖 {agent['id']}: {agent['name']} ({agent['type']}) - {agent['status']}")
        
        # 2. Sélectionner un agent pour la démo
        agent_id = "sales_assistant"
        print(f"\n🔍 2. Détails de l'agent '{agent_id}':")
        details = client.get_agent_details(agent_id)
        print(f"   📝 Nom: {details['name']}")
        print(f"   🏷️  Type: {details['type']}")
        print(f"   📊 Statut: {details['status']}")
        print(f"   📄 Description: {details['description']}")
        print(f"   🔧 Workflow: {details['config']['workflow']['entrypoint']}")
        
        # 3. Obtenir la configuration
        print(f"\n⚙️  3. Configuration de l'agent '{agent_id}':")
        config = client.get_agent_config(agent_id)
        print(f"   🚀 Point d'entrée: {config['workflow'].get('entrypoint', 'N/A')}")
        print(f"   🧠 Modèle: {config.get('model', {}).get('model_id', 'N/A')}")
        print(f"   🌡️  Température: {config.get('model', {}).get('config', {}).get('temperature', 'N/A')}")
        print(f"   💾 Mémoire: {config.get('memory', {}).get('type', 'N/A') if config.get('memory') else 'Aucune'}")
        
        # 4. Préparer et lancer l'agent
        print(f"\n🚀 4. Lancement de l'agent '{agent_id}':")
        input_data = {
            "customer_query": "Bonjour, je cherche des informations sur vos produits pour une startup technologique. Quels sont vos meilleurs services ?",
            "customer_context": {
                "industry": "technology",
                "company_size": "startup",
                "budget": "limited"
            }
        }
        
        print(f"   📥 Données d'entrée:")
        print(f"      Query: {input_data['customer_query']}")
        print(f"      Context: {input_data['customer_context']}")
        
        run_result = client.run_agent(agent_id, input_data, timeout=60)
        run_id = run_result['run_id']
        print(f"   🆔 Run ID: {run_id}")
        print(f"   📊 Statut initial: {run_result['status']}")
        print(f"   ⏰ Démarré à: {run_result['started_at']}")
        
        # 5. Surveiller l'exécution en temps réel
        print(f"\n👀 5. Surveillance de l'exécution:")
        max_attempts = 15
        for attempt in range(max_attempts):
            try: 
                status = client.get_agent_status(agent_id, run_id)
                current_run = status.get('current_run')
                
                if current_run:
                    print(f"   📊 Tentative {attempt + 1:2d}: {current_run['status']}")
                    
                    # Afficher les logs s'il y en a
                    if current_run.get('logs'):
                        latest_log = current_run['logs'][-1]
                        print(f"      📝 Dernier log: {latest_log}")
                    
                    # Vérifier si terminé
                    if current_run['status'] in ['completed', 'failed', 'cancelled']:
                        print(f"   ✅ Exécution terminée avec le statut: {current_run['status']}")
                        break
                else:
                    print(f"   📊 Tentative {attempt + 1:2d}: Pas d'exécution en cours")
                    break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"   ⚠️  Erreur lors de la surveillance: {e}")
                break
        else:
            print(f"   ⏰ Timeout atteint après {max_attempts} tentatives")
        
        # 6. Obtenir les résultats finaux
        print(f"\n📊 6. Résultats finaux:")
        try:
            final_details = client.get_run_details(agent_id, run_id)
            if final_details:
                print(f"   📊 Statut final: {final_details['status']}")
                print(f"   ⏰ Démarré: {final_details['started_at']}")
                if final_details.get('completed_at'):
                    print(f"   🏁 Terminé: {final_details['completed_at']}")
                
                if final_details.get('result'):
                    print(f"   ✅ Résultat:")
                    result = final_details['result']
                    if isinstance(result, dict):
                        for key, value in result.items():
                            print(f"      {key}: {value}")
                    else:
                        print(f"      {result}")
                
                if final_details.get('error'):
                    print(f"   ❌ Erreur: {final_details['error']}")
                
                if final_details.get('logs'):
                    print(f"   📝 Logs ({len(final_details['logs'])} entrées):")
                    for i, log in enumerate(final_details['logs'][-3:], 1):  # Derniers 3 logs
                        print(f"      {i}. {log}")
            else:
                print(f"   ⚠️  Impossible de récupérer les détails de l'exécution")
                
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la récupération des résultats: {e}")
        
        # 7. Test d'un autre agent
        print(f"\n🔄 7. Test rapide d'un autre agent:")
        research_agent = "research"
        try:
            research_input = {
                "query": "Quelles sont les dernières tendances en IA pour 2024 ?",
                "topic": "artificial intelligence trends"
            }
            
            print(f"   🚀 Lancement de l'agent '{research_agent}'...")
            research_run = client.run_agent(research_agent, research_input, timeout=30)
            print(f"   🆔 Run ID: {research_run['run_id']}")
            
            # Attendre un peu et vérifier le statut
            time.sleep(3)
            research_status = client.get_agent_status(research_agent, research_run['run_id'])
            print(f"   📊 Statut: {research_status.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"   ⚠️  Erreur avec l'agent research: {e}")
        
        print(f"\n🎉 Démonstration terminée avec succès!")
        print(f"\n📚 Pour plus d'informations:")
        print(f"   - Documentation API: http://localhost:8000/docs")
        print(f"   - Documentation alternative: http://localhost:8000/redoc")
        print(f"   - README API: src/ai_agents/deployment/api_agent/README.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_api_complete()
    print(f"\n{'✅ Démonstration réussie' if success else '❌ Démonstration échouée'}")
    sys.exit(0 if success else 1)
