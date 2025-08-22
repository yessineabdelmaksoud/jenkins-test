import requests
from requests.auth import HTTPBasicAuth

def extract_build_log(jenkins_url, job_name, build_number, username, api_token):
    log_url = f'{jenkins_url}/job/{job_name}/{build_number}/consoleText'
    response = requests.get(log_url, auth=HTTPBasicAuth(username, api_token))
    if response.status_code == 200:
        print(response.text)
        with open(f"build_{job_name}_{build_number}_console.log", "w", encoding="utf-8") as f:
            f.write(response.text)
        return True
    else:
        print(f"❌ Failed to get log: {response.status_code} - {response.reason}")
        return False

# Exemple d'utilisation
if __name__ == "__main__":
    import sys
    
    jenkins_url = 'http://localhost:8080'
    job_name = "yessine"
    build_number = 1
    username = 'yessine'
    api_token = '11f9fd1c763a2051af553ee0b8aba3889d'
    extract_build_log(jenkins_url, job_name, build_number, username, api_token)

    print("Usage: python triggers-logs.py <job_name> <build_number>")