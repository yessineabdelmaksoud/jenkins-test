import requests
from requests.auth import HTTPBasicAuth
import json

# Fonction pour extraire la configuration des agents Jenkins

def extract_agents_config(jenkins_url, username, api_token, output_file):
    url = f"{jenkins_url}/computer/api/json"
    response = requests.get(url, auth=HTTPBasicAuth(username, api_token))
    if response.status_code != 200:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False
    data = response.json()
    agents = []
    for computer in data.get('computer', []):
        agent_info = {
            'displayName': computer.get('displayName'),
            'offline': computer.get('offline'),
            'numExecutors': computer.get('numExecutors'),
            'description': computer.get('description'),
            'type': computer.get('_class'),
            'assignedLabels': [label.get('name') for label in computer.get('assignedLabels', []) if 'name' in label],
            'resources': {
                'totalExecutors': computer.get('numExecutors'),
                'monitorData': computer.get('monitorData', {})
            }
        }
        agents.append(agent_info)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    print(f"✅ Configuration des agents sauvegardée dans {output_file}")
    return True

# Exemple d'utilisation
if __name__ == "__main__":
    import sys
    JENKINS_URL = "http://localhost:8080"
    USERNAME = "yessine"
    API_TOKEN = "11f9fd1c763a2051af553ee0b8aba3889d"
    OUTPUT_FILE = "jenkins_agents_config.json"
    extract_agents_config(JENKINS_URL, USERNAME, API_TOKEN, OUTPUT_FILE)
