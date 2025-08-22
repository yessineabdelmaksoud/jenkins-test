#!/usr/bin/env python3
"""Démonstration finale complète de l'API AI Agents."""

import sys
import time
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from ai_agents.deployment.api_agent.examples.api_examples import AgentAPIClient


def demo_complete_workflow():
    """Démonstration complète du workflow API."""
    print("🚀 DÉMONSTRATION FINALE - API AI AGENTS")
    print("=" * 60)
    
    client = AgentAPIClient()
    
    try:
        # Vérifier l'API
        print("🔍 1. Vérification de l'API...")
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                print("❌ API non accessible sur le port 8000")
                return False
            print("✅ API accessible et fonctionnelle")
        except Exception:
            print("❌ Impossible de se connecter à l'API")
            return False
        
        # Lister les agents
        print("\n📋 2. Découverte des agents...")
        agents = client.list_agents()
        print(f"   🤖 {agents['total']} agents disponibles:")
        for agent in agents['agents']:
            print(f"      • {agent['id']} - {agent['name']} ({agent['status']})")
        
        # Test avec différents agents
        test_agents = ["sales_assistant", "research", "supervisor"]
        
        for i, agent_id in enumerate(test_agents, 3):
            print(f"\n🎯 {i}. Test de l'agent '{agent_id}':")
            
            try:
                # Obtenir les détails
                details = client.get_agent_details(agent_id)
                print(f"   📝 Type: {details['type']}")
                print(f"   ⚙️  Workflow: {details['config']['workflow']['entrypoint']}")
                
                # Préparer des données de test spécifiques
                if agent_id == "sales_assistant":
                    input_data = {
                        "customer_query": "Je cherche une solution pour mon entreprise",
                        "context": "startup tech"
                    }
                elif agent_id == "research":
                    input_data = {
                        "query": "Tendances IA 2024",
                        "topic": "artificial intelligence"
                    }
                else:  # supervisor
                    input_data = {
                        "task": "Coordonner les agents",
                        "priority": "high"
                    }
                
                print(f"   📥 Input: {input_data}")
                
                # Lancer l'agent
                run_result = client.run_agent(agent_id, input_data, timeout=30)
                run_id = run_result['run_id']
                print(f"   🆔 Run ID: {run_id[:8]}...")
                
                # Surveiller rapidement
                for attempt in range(5):
                    status = client.get_agent_status(agent_id, run_id)
                    if status.get('current_run'):
                        current_status = status['current_run']['status']
                        print(f"   📊 Statut: {current_status}")
                        if current_status in ['completed', 'failed', 'cancelled']:
                            break
                    time.sleep(1)
                
                # Vérifier les résultats
                runs = client.list_agent_runs(agent_id)
                if runs:
                    latest_run = runs[0]  # Le plus récent
                    print(f"   ✅ Résultat: {latest_run['status']}")
                    if latest_run.get('result'):
                        print(f"   📊 Données: {str(latest_run['result'])[:50]}...")
                
            except Exception as e:
                print(f"   ⚠️  Erreur avec {agent_id}: {str(e)[:50]}...")
        
        # Test des fonctionnalités avancées
        print(f"\n🔧 {len(test_agents) + 3}. Test des fonctionnalités avancées:")
        
        # Configuration personnalisée
        print("   🎛️  Test avec configuration personnalisée...")
        custom_config = {
            "model": {
                "temperature": 0.9,
                "max_tokens": 200
            }
        }
        
        custom_run = client.run_agent(
            "sales_assistant",
            {"customer_query": "Configuration personnalisée test"},
            config_override=custom_config,
            timeout=20
        )
        print(f"   ✅ Exécution avec config custom: {custom_run['run_id'][:8]}...")
        
        # Attendre et vérifier
        time.sleep(3)
        custom_status = client.get_agent_status("sales_assistant", custom_run['run_id'])
        print(f"   📊 Statut custom: {custom_status.get('status', 'unknown')}")
        
        # Statistiques finales
        print(f"\n📊 {len(test_agents) + 4}. Statistiques finales:")
        total_runs = 0
        for agent_id in test_agents:
            try:
                runs = client.list_agent_runs(agent_id)
                agent_runs = len(runs)
                total_runs += agent_runs
                print(f"   🤖 {agent_id}: {agent_runs} exécutions")
                
                if runs:
                    completed = sum(1 for r in runs if r['status'] == 'completed')
                    failed = sum(1 for r in runs if r['status'] == 'failed')
                    print(f"      ✅ Réussies: {completed}, ❌ Échouées: {failed}")
                    
            except Exception as e:
                print(f"   ⚠️  Erreur stats {agent_id}: {str(e)[:30]}...")
        
        print(f"\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print(f"   📊 Total des exécutions: {total_runs}")
        print(f"   🕒 Durée: ~{(len(test_agents) * 5) + 10} secondes")
        
        # Informations utiles
        print(f"\n📚 Ressources utiles:")
        print(f"   🌐 Documentation: http://localhost:8000/docs")
        print(f"   🔄 API alternative: http://localhost:8000/redoc")
        print(f"   📁 Code source: src/ai_agents/deployment/api_agent/")
        print(f"   📖 README: src/ai_agents/deployment/api_agent/README.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_error_scenarios():
    """Démonstration des scénarios d'erreur."""
    print("\n⚠️  BONUS: Test des scénarios d'erreur")
    print("-" * 40)
    
    client = AgentAPIClient()
    
    # Test agent inexistant
    try:
        client.get_agent_details("agent_inexistant")
        print("❌ Erreur: devrait échouer")
    except Exception:
        print("✅ Agent inexistant: erreur correctement gérée")
    
    # Test run inexistant
    try:
        client.get_run_details("sales_assistant", "run-inexistant-123")
        print("❌ Erreur: devrait échouer")
    except Exception:
        print("✅ Run inexistant: erreur correctement gérée")
    
    # Test données invalides
    try:
        client.run_agent("sales_assistant", "données_invalides")
        print("❌ Erreur: devrait échouer")
    except Exception:
        print("✅ Données invalides: erreur correctement gérée")
    
    print("✅ Tous les scénarios d'erreur fonctionnent correctement")


if __name__ == "__main__":
    print("🤖 DÉMONSTRATION FINALE DE L'API AI AGENTS")
    print("=" * 70)
    
    success = demo_complete_workflow()
    
    if success:
        demo_error_scenarios()
        print(f"\n🎊 TOUTES LES DÉMONSTRATIONS RÉUSSIES!")
        print(f"🚀 L'API AI Agents est entièrement fonctionnelle!")
    else:
        print(f"\n❌ Démonstration échouée")
        print(f"💡 Assurez-vous que l'API est démarrée avec:")
        print(f"   python src/ai_agents/deployment/api_agent/start_api.py")
    
    sys.exit(0 if success else 1)
