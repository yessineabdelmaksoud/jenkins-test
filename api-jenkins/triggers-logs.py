import requests
from requests.auth import HTTPBasicAuth

# Configuration
jenkins_url = 'http://localhost:8080'
job_name = 'bot1'
build_number = 'lastBuild'
username = 'yessine'  # Remplace ici
api_token = '11f9fd1c763a2051af553ee0b8aba3889d'       # Remplace ici (pas ton mot de passe !)

# URL du log
log_url = f'{jenkins_url}/job/{job_name}/{build_number}/consoleText'

# Requête avec authentification
response = requests.get(log_url, auth=HTTPBasicAuth(username, api_token))

if response.status_code == 200:
    print(response.text)
    # Enregistrement du log dans un fichier local
    with open(f"build_{job_name}_{build_number}_console.log", "w", encoding="utf-8") as f:
        f.write(response.text)
else:
    print(f"❌ Failed to get log: {response.status_code} - {response.reason}")
