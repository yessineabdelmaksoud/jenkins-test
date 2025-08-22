#!/usr/bin/env python3
"""Démonstration de l'agent Calculator via l'API."""

import sys
import time
import json 
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from ai_agents.deployment.api_agent.examples.api_examples import AgentAPIClient


def demo_calculator_showcase():
    """Démonstration complète de l'agent Calculator."""
    print("🧮 DÉMONSTRATION DE L'AGENT CALCULATOR")
    print("=" * 60)
    print("Agent simple sans OpenAI - Calculs mathématiques")
    print("=" * 60)
    
    client = AgentAPIClient()
    
    try:
        # Vérifier l'API
        print("🔍 1. Vérification de l'API...")
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                print("❌ API non accessible. Démarrez-la avec:")
                print("   python src/ai_agents/deployment/api_agent/start_api.py")
                return False
            print("✅ API accessible et fonctionnelle")
        except Exception:
            print("❌ Impossible de se connecter à l'API")
            return False
        
        # Présentation de l'agent
        print("\n🤖 2. Présentation de l'agent Calculator...")
        details = client.get_agent_details("calculator")
        print(f"   📝 Nom: {details['name']}")
        print(f"   🏷️  Type: {details['type']}")
        print(f"   🔧 Workflow: {details['config']['workflow']['entrypoint']}")
        print(f"   🧠 Modèle: {details['config'].get('model', 'Aucun - Pas d\'OpenAI requis!')}")
        print(f"   💾 Mémoire: {details['config'].get('memory', 'Aucune - Calculs stateless')}")
        print(f"   ⚡ Avantage: Fonctionne sans clé API OpenAI!")
        
        # Démonstrations par catégorie
        demos = [
            {
                "title": "🔢 Calculs arithmétiques de base",
                "expressions": [
                    "2 + 3",
                    "15 - 7", 
                    "4 * 6",
                    "20 / 4",
                    "2 + 3 * 4",  # Priorité des opérateurs
                    "(2 + 3) * 4"  # Parenthèses
                ]
            }, 
            {
                "title": "🔬 Calculs avancés",
                "expressions": [
                    "2^3",  # Puissance
                    "sqrt(16)",  # Racine carrée
                    "sqrt(25) + 2^3",  # Combinaison
                    "abs(-10)",  # Valeur absolue
                    "(10 + 5) * 2 - sqrt(16)"  # Expression complexe
                ]
            },
            {
                "title": "🔢 Calculs avec décimales",
                "expressions": [
                    "3.14 * 2",
                    "22 / 7",  # Approximation de π
                    "sqrt(2)",  # Nombre irrationnel
                    "10.5 + 2.3 * 1.2"
                ]
            }
        ]
        
        total_tests = 0
        successful_tests = 0
        
        for demo_category in demos:
            print(f"\n{demo_category['title']}")
            print("-" * 40)
            
            for expression in demo_category['expressions']:
                total_tests += 1
                print(f"\n   📝 Expression: {expression}")
                
                try:
                    # Lancer le calcul
                    input_data = {"expression": expression}
                    run_result = client.run_agent("calculator", input_data, timeout=30)
                    run_id = run_result['run_id']
                    
                    # Attendre le résultat (l'agent Calculator est très rapide)
                    time.sleep(1)
                    
                    # Récupérer le résultat
                    run_details = client.get_run_details("calculator", run_id)
                    
                    if run_details and run_details['status'] == 'completed':
                        result = run_details.get('result', {})
                        formatted_result = result.get('formatted_result', 'N/A')
                        calculation_result = result.get('calculation_result')
                        operation_type = result.get('operation_type', 'unknown')
                        
                        print(f"   ✅ {formatted_result}")
                        print(f"   📊 Valeur numérique: {calculation_result}")
                        print(f"   🏷️  Type: {operation_type}")
                        successful_tests += 1
                        
                    elif run_details and run_details['status'] == 'failed':
                        error = run_details.get('error', 'Unknown error')
                        print(f"   ❌ Erreur: {error}")
                        
                    else:
                        print(f"   ⏰ Timeout ou statut inconnu")
                        
                except Exception as e:
                    print(f"   ❌ Exception: {str(e)[:50]}...")
        
        # Tests de gestion d'erreurs
        print(f"\n⚠️  Gestion d'erreurs")
        print("-" * 40)
        
        error_cases = [
            ("Division par zéro", "10 / 0"),
            ("Expression invalide", "2 + + 3"),
            ("Caractères interdits", "2 + abc"),
            ("Expression vide", "")
        ]
        
        for error_name, expression in error_cases:
            print(f"\n   🧪 Test: {error_name}")
            print(f"   📝 Expression: '{expression}'")
            
            try:
                input_data = {"expression": expression}
                run_result = client.run_agent("calculator", input_data, timeout=30)
                run_id = run_result['run_id']
                
                time.sleep(1)
                run_details = client.get_run_details("calculator", run_id)
                
                if run_details:
                    result = run_details.get('result', {})
                    if 'Error' in str(result) or run_details['status'] == 'failed':
                        print(f"   ✅ Erreur correctement gérée")
                    else:
                        print(f"   ⚠️  Erreur non détectée: {result}")
                        
            except Exception as e:
                print(f"   ✅ Exception correctement levée: {str(e)[:30]}...")
        
        # Statistiques finales
        print(f"\n📊 Statistiques de la démonstration")
        print("=" * 40)
        print(f"   🧮 Total des calculs: {total_tests}")
        print(f"   ✅ Calculs réussis: {successful_tests}")
        print(f"   ❌ Calculs échoués: {total_tests - successful_tests}")
        print(f"   📈 Taux de réussite: {(successful_tests / total_tests * 100):.1f}%")
        
        # Historique des exécutions
        print(f"\n📋 Historique des exécutions")
        print("-" * 40)
        try:
            runs = client.list_agent_runs("calculator")
            print(f"   📊 Nombre total d'exécutions: {len(runs)}")
            
            if runs:
                print("   🕒 Dernières exécutions:")
                for i, run in enumerate(runs[:5], 1):
                    status_icon = "✅" if run['status'] == 'completed' else "❌" if run['status'] == 'failed' else "⏳"
                    duration = "N/A"
                    if run.get('started_at') and run.get('completed_at'):
                        from datetime import datetime
                        start = datetime.fromisoformat(run['started_at'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(run['completed_at'].replace('Z', '+00:00'))
                        duration = f"{(end - start).total_seconds():.3f}s"
                    
                    print(f"      {i}. {status_icon} {run['run_id'][:8]} - {run['status']} ({duration})")
                    
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la récupération: {e}")
        
        # Avantages de l'agent Calculator
        print(f"\n🌟 Avantages de l'agent Calculator")
        print("=" * 40)
        print("   ⚡ Rapide: Calculs instantanés sans appel API externe")
        print("   🔒 Sécurisé: Pas de clé API requise")
        print("   💰 Gratuit: Aucun coût d'utilisation")
        print("   🌐 Offline: Fonctionne sans connexion internet")
        print("   🔧 Simple: Facile à comprendre et maintenir")
        print("   📊 Fiable: Résultats mathématiques précis")
        print("   🛡️  Sûr: Validation des expressions d'entrée")
        
        print(f"\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print(f"🧮 L'agent Calculator est un excellent exemple d'agent")
        print(f"   simple et efficace sans dépendance OpenAI!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧮 DÉMONSTRATION DE L'AGENT CALCULATOR")
    print("=" * 70)
    print("Agent mathématique simple - Sans OpenAI requis")
    print("=" * 70)
    
    success = demo_calculator_showcase()
    
    if success:
        print(f"\n🎊 DÉMONSTRATION RÉUSSIE!")
        print(f"💡 Cet agent montre qu'on peut créer des agents utiles")
        print(f"   sans dépendre d'APIs externes coûteuses!")
    else:
        print(f"\n❌ Démonstration échouée")
        print(f"💡 Assurez-vous que l'API est démarrée avec:")
        print(f"   python src/ai_agents/deployment/api_agent/start_api.py")
    
    sys.exit(0 if success else 1)
