#!/usr/bin/env python3
"""Script de démarrage rapide pour l'API AI Agents."""

import sys
import os
import time
import subprocess
import signal
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))


def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    print("🔍 Vérification des dépendances...")
    
    try:
        import fastapi
        import uvicorn
        import pydantic_settings
        print("   ✅ FastAPI et dépendances installées")
        return True
    except ImportError as e:
        print(f"   ❌ Dépendances manquantes: {e}")
        print("   💡 Installez avec: poetry install")
        return False


def check_env_file():
    """Vérifie que le fichier .env existe et contient les variables nécessaires."""
    print("🔍 Vérification du fichier .env...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("   ❌ Fichier .env manquant")
        print("   💡 Copiez .env.example vers .env et configurez OPENAI_API_KEY")
        return False
    
    # Lire le fichier .env
    env_content = env_path.read_text()
    if "OPENAI_API_KEY=" not in env_content:
        print("   ❌ OPENAI_API_KEY manquant dans .env")
        print("   💡 Ajoutez OPENAI_API_KEY=sk-your-key-here dans .env")
        return False
    
    # Vérifier que la clé n'est pas vide
    for line in env_content.split('\n'):
        if line.startswith('OPENAI_API_KEY='):
            key = line.split('=', 1)[1].strip()
            if not key or key == 'sk-your-openai-api-key-here':
                print("   ❌ OPENAI_API_KEY non configurée")
                print("   💡 Remplacez par votre vraie clé OpenAI dans .env")
                return False
            print("   ✅ OPENAI_API_KEY configurée")
            return True
    
    return False


def test_configuration():
    """Teste la configuration de l'API."""
    print("🔧 Test de la configuration...")
    
    try:
        from ai_agents.deployment.api_agent.core.config import get_settings
        settings = get_settings()
        print("   ✅ Configuration chargée")
        return True
    except Exception as e:
        print(f"   ❌ Erreur de configuration: {e}")
        return False


def start_api_server():
    """Démarre le serveur API."""
    print("🚀 Démarrage du serveur API...")
    
    try:
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([
            sys.executable, 
            "src/ai_agents/deployment/api_agent/start_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(5)
        
        # Vérifier que le serveur répond
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Serveur API démarré avec succès")
                print("   📍 URL: http://localhost:8000")
                print("   📚 Documentation: http://localhost:8000/docs")
                return process
            else:
                print(f"   ❌ Serveur répond avec le code {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("   ❌ Serveur ne répond pas")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur lors du démarrage: {e}")
        return None


def run_demo():
    """Lance la démonstration."""
    print("🎬 Lancement de la démonstration...")
    
    try:
        # Importer et lancer la démo
        from ai_agents.deployment.api_agent.demo import demo_api_complete
        return demo_api_complete()
    except Exception as e:
        print(f"   ❌ Erreur durant la démonstration: {e}")
        return False


def main():
    """Fonction principale du démarrage rapide."""
    print("🤖 Démarrage rapide de l'API AI Agents")
    print("=" * 50)
    
    # Étape 1: Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Échec: Dépendances manquantes")
        return False
    
    # Étape 2: Vérifier le fichier .env
    if not check_env_file():
        print("\n❌ Échec: Configuration .env incorrecte")
        return False
    
    # Étape 3: Tester la configuration
    if not test_configuration():
        print("\n❌ Échec: Erreur de configuration")
        return False
    
    print("\n✅ Toutes les vérifications passées!")
    
    # Demander à l'utilisateur s'il veut continuer
    print("\n🚀 Prêt à démarrer l'API et lancer la démonstration")
    response = input("Continuer ? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes', 'o', 'oui']:
        print("   ⏹️  Arrêt demandé par l'utilisateur")
        return True
    
    # Étape 4: Démarrer le serveur API
    server_process = start_api_server()
    if not server_process:
        print("\n❌ Échec: Impossible de démarrer le serveur API")
        return False
    
    try:
        # Étape 5: Lancer la démonstration
        print("\n" + "="*50)
        demo_success = run_demo()
        
        if demo_success: 
            print("\n🎉 Démonstration terminée avec succès!")
        else:
            print("\n⚠️  Démonstration terminée avec des erreurs")
        
        # Demander si on veut garder le serveur ouvert
        print(f"\n🖥️  Le serveur API est toujours en cours d'exécution")
        print(f"   📍 URL: http://localhost:8000")
        print(f"   📚 Documentation: http://localhost:8000/docs")
        
        keep_running = input("\nGarder le serveur ouvert ? (Y/n): ").strip().lower()
        
        if keep_running in ['n', 'no', 'non']:
            print("   ⏹️  Arrêt du serveur...")
            server_process.terminate()
            server_process.wait()
            print("   ✅ Serveur arrêté")
        else:
            print("   🔄 Serveur maintenu ouvert")
            print("   💡 Appuyez sur Ctrl+C pour l'arrêter")
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n   ⏹️  Arrêt du serveur...")
                server_process.terminate()
                server_process.wait()
                print("   ✅ Serveur arrêté")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Interruption par l'utilisateur")
        if server_process:
            server_process.terminate()
            server_process.wait()
        return True
    
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        if server_process:
            server_process.terminate()
            server_process.wait()
        return False


if __name__ == "__main__":
    try:
        success = main()
        print(f"\n{'✅ Démarrage rapide réussi' if success else '❌ Démarrage rapide échoué'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé par l'utilisateur")
        sys.exit(0)
