import requests
from requests.auth import HTTPBasicAuth
import sys

# Fonction pour lancer un job Jenkins

def trigger_jenkins_job(jenkins_url, job_name, username, api_token, params=None):
    build_url = f"{jenkins_url}/job/{job_name}/build"
    if params:
        build_url += "WithParameters"
    response = requests.post(build_url, auth=HTTPBasicAuth(username, api_token), params=params)
    if response.status_code in [201, 200]:
        print(f"✅ Job '{job_name}' lancé avec succès !")
        return True
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False

# Exemple d'utilisation
if __name__ == "__main__":
    # Paramètres Jenkins
    jenkins_url = "http://localhost:8080"
    username = "yessine"
    api_token = "11f9fd1c763a2051af553ee0b8aba3889d"
    if len(sys.argv) >= 2:
        job_name = sys.argv[1]
        # Pour lancer avec paramètres, ajouter un dict params={...}
        trigger_jenkins_job(jenkins_url, job_name, username, api_token)
    else:
        print("Usage: python lunch-job.py <job_name>")
