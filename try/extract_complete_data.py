import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import json
import sys
import os

def extract_complete_data(jenkins_url, job_name, build_number, username, api_token, output_file):
    """Extrait toutes les données Jenkins en un seul script et les sauvegarde dans un JSON"""
    
    # 1. Extraire le Jenkinsfile
    jenkinsfile_content = ""
    try:
        config_url = f"{jenkins_url}/job/{job_name}/config.xml"
        response = requests.get(config_url, auth=HTTPBasicAuth(username, api_token))
        if response.status_code == 200:
            xml_content = response.text
            root = ET.fromstring(xml_content)
            
            # Cas 1 : Jenkinsfile dans Git
            scm_node = root.find(".//scm")
            if scm_node is not None:
                github_url = scm_node.find(".//url").text
                branch = scm_node.find(".//name").text.replace("*/", "")
                script_path = root.find(".//scriptPath").text
                
                github_raw_url = github_url.replace("https://github.com/", "https://raw.githubusercontent.com/")
                if github_raw_url.endswith(".git"):
                    github_raw_url = github_raw_url[:-4]
                github_raw_url += f"/{branch}/{script_path}"
                
                git_response = requests.get(github_raw_url)
                if git_response.status_code == 200:
                    jenkinsfile_content = git_response.text
            
            # Cas 2 : Jenkinsfile inline
            script_node = root.find(".//script")
            if script_node is not None and script_node.text:
                jenkinsfile_content = script_node.text
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction du Jenkinsfile: {e}")

    # 2. Extraire les logs de build
    console_log_content = ""
    try:
        log_url = f'{jenkins_url}/job/{job_name}/{build_number}/consoleText'
        response = requests.get(log_url, auth=HTTPBasicAuth(username, api_token))
        if response.status_code == 200:
            console_log_content = response.text
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des logs: {e}")

    # 3. Extraire les métadonnées du build
    build_metadata = {}
    try:
        api_url = f"{jenkins_url}/job/{job_name}/{build_number}/api/json"
        response = requests.get(api_url, auth=HTTPBasicAuth(username, api_token))
        if response.status_code == 200:
            build_metadata = response.json()
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des métadonnées: {e}")

    # 4. Extraire les informations des agents/nodes
    agents_data = []
    try:
        url = f"{jenkins_url}/computer/api/json"
        response = requests.get(url, auth=HTTPBasicAuth(username, api_token))
        if response.status_code == 200:
            agents_data = response.json().get('computer', [])
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des agents: {e}")

    # 5. Construire le JSON final selon la structure demandée
    # Extraire les informations utilisateur
    user = ""
    git_repo = ""
    commit = ""
    
    for action in build_metadata.get("actions", []):
        if "causes" in action:
            for cause in action.get("causes", []):
                if "userName" in cause:
                    user = cause.get("userName", "")
        if "remoteUrls" in action:
            git_repo = action.get("remoteUrls", [""])[0]
        if "lastBuiltRevision" in action:
            commit = action.get("lastBuiltRevision", {}).get("SHA1", "")

    # Informations du premier agent/node
    first_agent = agents_data[0] if agents_data else {}
    monitor_data = first_agent.get("monitorData", {})
    
    # Extraire les données de mémoire et disque
    memory_data = {}
    disk_data = {}
    for key, value in monitor_data.items():
        if "Memory" in key and isinstance(value, dict):
            memory_data = value
        elif "Space" in key and isinstance(value, dict):
            disk_data = value

    final_data = {
        "build_number": build_metadata.get("number", build_number),
        "status": build_metadata.get("result", ""),
        "timestamp": build_metadata.get("timestamp", ""),
        "user": user,
        "git_repo": git_repo,
        "commit": commit,
        "jenkinsfile": jenkinsfile_content,
        "console_log": console_log_content,
        "node_name": first_agent.get("displayName", ""),
        "node_status": "offline" if first_agent.get("offline", False) else "online",
        "executors": first_agent.get("numExecutors", 0),
        "total_memory": memory_data.get("totalPhysicalMemory", 0),
        "available_memory": memory_data.get("availablePhysicalMemory", 0),
        "total_swap_space": memory_data.get("totalSwapSpace", 0),
        "available_swap_space": memory_data.get("availableSwapSpace", 0),
        "disk_space_temp": {
            "available": disk_data.get("size", 0),
            "total": disk_data.get("size", 0),
            "threshold": 0
        },
        "os": first_agent.get("description", "")
    }

    # 6. Sauvegarder dans le fichier JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Données complètes sauvegardées dans {output_file}")
    return True

# Exemple d'utilisation
if __name__ == "__main__":
    
    jenkins_url = "http://localhost:8080"
    job_name = "jenkins-fail-pipeline"
    build_number = 3
    username = "yessine"
    api_token = "11f9fd1c763a2051af553ee0b8aba3889d"
    output_file = f"complete_data_{job_name}_{build_number}.json"
    
    extract_complete_data(jenkins_url, job_name, build_number, username, api_token, output_file)

