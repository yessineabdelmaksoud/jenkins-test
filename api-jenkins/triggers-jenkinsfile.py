import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import os

# ==== CONFIG ====
JENKINS_URL = "http://localhost:8080"
JOB_NAME = "mini%20projet"   # ex: bot1 ou mini%20projet
USERNAME = "yessine"
API_TOKEN = "11f9fd1c763a2051af553ee0b8aba3889d"

# Fichier Jenkinsfile à sauvegarder
OUTPUT_FILE = "Jenkinsfile_extracted"

# ==== Télécharge le config.xml ====
config_url = f"{JENKINS_URL}/job/{JOB_NAME}/config.xml"
response = requests.get(config_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))

if response.status_code != 200:
    print(f"❌ Erreur {response.status_code} : {response.text}")
    exit(1)

xml_content = response.text

# ==== Analyse du XML ====
root = ET.fromstring(xml_content)

# Cas 1 : Jenkinsfile dans Git (CpsScmFlowDefinition)
scm_node = root.find(".//scm")
if scm_node is not None:
    github_url = scm_node.find(".//url").text
    branch = scm_node.find(".//name").text.replace("*/", "")
    script_path = root.find(".//scriptPath").text

    print(f"📂 Jenkinsfile trouvé dans GitHub : {github_url} (branche {branch}, chemin {script_path})")

    # Construire URL brute vers GitHub
    # Ex: https://raw.githubusercontent.com/<user>/<repo>/<branch>/<path>
    github_raw_url = github_url.replace("https://github.com/", "https://raw.githubusercontent.com/")
    if github_raw_url.endswith(".git"):
        github_raw_url = github_raw_url[:-4]
    github_raw_url += f"/{branch}/{script_path}"

    print(f"🔗 Téléchargement depuis : {github_raw_url}")
    git_response = requests.get(github_raw_url)
    if git_response.status_code == 200:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(git_response.text)
        print(f"✅ Jenkinsfile sauvegardé dans {OUTPUT_FILE}")
    else:
        print(f"❌ Erreur lors du téléchargement depuis GitHub : {git_response.status_code}")
    exit(0)

# Cas 2 : Jenkinsfile inline dans Jenkins (CpsFlowDefinition)
script_node = root.find(".//script")
if script_node is not None and script_node.text:
    print("📄 Jenkinsfile trouvé directement dans Jenkins (inline script)")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(script_node.text)
    print(f"✅ Jenkinsfile sauvegardé dans {OUTPUT_FILE}")
    exit(0)

print("❌ Aucun Jenkinsfile trouvé dans le XML.")
