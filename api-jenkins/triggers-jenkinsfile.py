import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import os

def extract_jenkinsfile(jenkins_url, job_name, username, api_token, output_file):
    config_url = f"{jenkins_url}/job/{job_name}/config.xml"
    response = requests.get(config_url, auth=HTTPBasicAuth(username, api_token))
    if response.status_code != 200:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False
    xml_content = response.text
    root = ET.fromstring(xml_content)
    # Cas 1 : Jenkinsfile dans Git (CpsScmFlowDefinition)
    scm_node = root.find(".//scm")
    if scm_node is not None:
        github_url = scm_node.find(".//url").text
        branch = scm_node.find(".//name").text.replace("*/", "")
        script_path = root.find(".//scriptPath").text
        print(f"📂 Jenkinsfile trouvé dans GitHub : {github_url} (branche {branch}, chemin {script_path})")
        github_raw_url = github_url.replace("https://github.com/", "https://raw.githubusercontent.com/")
        if github_raw_url.endswith(".git"):
            github_raw_url = github_raw_url[:-4]
        github_raw_url += f"/{branch}/{script_path}"
        print(f"🔗 Téléchargement depuis : {github_raw_url}")
        git_response = requests.get(github_raw_url)
        if git_response.status_code == 200:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(git_response.text)
            print(f"✅ Jenkinsfile sauvegardé dans {output_file}")
            return True
        else:
            print(f"❌ Erreur lors du téléchargement depuis GitHub : {git_response.status_code}")
            return False
    # Cas 2 : Jenkinsfile inline dans Jenkins (CpsFlowDefinition)
    script_node = root.find(".//script")
    if script_node is not None and script_node.text:
        print("📄 Jenkinsfile trouvé directement dans Jenkins (inline script)")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(script_node.text)
        print(f"✅ Jenkinsfile sauvegardé dans {output_file}")
        return True
    print("❌ Aucun Jenkinsfile trouvé dans le XML.")
    return False

# Exemple d'utilisation
if __name__ == "__main__":
    import sys
    JENKINS_URL = "http://localhost:8080"
    USERNAME = "yessine"
    API_TOKEN = "11f9fd1c763a2051af553ee0b8aba3889d"
    if len(sys.argv) >= 3:
        JOB_NAME = sys.argv[1]
        BUILD_NUMBER = sys.argv[2]
        OUTPUT_FILE = f"Jenkinsfile_extracted_{JOB_NAME}_{BUILD_NUMBER}"
        extract_jenkinsfile(JENKINS_URL, JOB_NAME, USERNAME, API_TOKEN, OUTPUT_FILE)
    else:
        print("Usage: python tiggers-jenkinsfile.py <job_name> <build_number>")