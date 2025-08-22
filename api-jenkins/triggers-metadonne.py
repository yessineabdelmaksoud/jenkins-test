import requests
from requests.auth import HTTPBasicAuth
import json
import sys

def extract_build_metadata(jenkins_url, job_name, build_number, username, api_token, output_file):
    """Récupère les métadonnées détaillées d'un build Jenkins"""
    api_url = f"{jenkins_url}/job/{job_name}/{build_number}/api/json"
    response = requests.get(api_url, auth=HTTPBasicAuth(username, api_token))
    
    if response.status_code == 200:
        data = response.json()
        
        # On ne garde que les infos importantes
        metadata = {
            "build_number": data.get("number"),
            "status": data.get("result"),
            "duration_ms": data.get("duration"),
            "timestamp": data.get("timestamp"),
            "url": data.get("url"),
            "builtOn": data.get("builtOn"),
            "changeSet": data.get("changeSet", {}),
            "actions": data.get("actions", []),  # contient causes & paramètres
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        
        print(f"✅ Métadonnées du build sauvegardées dans {output_file}")
        return True
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False


def extract_job_history(jenkins_url, job_name, username, api_token, output_file):
    """Récupère l'historique des builds d'un job Jenkins"""
    api_url = f"{jenkins_url}/job/{job_name}/api/json"
    response = requests.get(api_url, auth=HTTPBasicAuth(username, api_token))
    
    if response.status_code == 200:
        data = response.json()
        
        # On extrait juste l'historique simple
        builds_info = [
            {
                "build_number": b.get("number"),
                "url": b.get("url")
            }
            for b in data.get("builds", [])
        ]
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(builds_info, f, indent=4)
        
        print(f"✅ Historique du job sauvegardé dans {output_file}")
        return True
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        jenkins_url = "http://localhost:8080"
        job_name = sys.argv[1]
        build_number = sys.argv[2]
        username = "yessine"
        api_token = "11f9fd1c763a2051af553ee0b8aba3889d"

        extract_build_metadata(jenkins_url, job_name, build_number, username, api_token,
                               f"metadata_{job_name}_{build_number}.json")

        extract_job_history(jenkins_url, job_name, username, api_token,
                            f"history_{job_name}.json")
    else:
        print("Usage: python extract_metadata.py <job_name> <build_number>")
