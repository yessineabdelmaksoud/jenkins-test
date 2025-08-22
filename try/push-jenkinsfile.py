import requests
from requests.auth import HTTPBasicAuth
import sys
import xml.etree.ElementTree as ET

# Fonction pour modifier le Jenkinsfile d'un job et relancer le job

def update_jenkinsfile_and_trigger(jenkins_url, job_name, username, api_token, new_jenkinsfile_content):
    # 1. Récupérer le config.xml du job
    config_url = f"{jenkins_url}/job/{job_name}/config.xml"
    response = requests.get(config_url, auth=HTTPBasicAuth(username, api_token))
    if response.status_code != 200:
        print(f"❌ Erreur récupération config.xml : {response.status_code} - {response.text}")
        return False
    xml_content = response.text
    root = ET.fromstring(xml_content)
    # 2. Détecter si le Jenkinsfile est dans GitHub ou inline
    scm_node = root.find(".//scm")
    if scm_node is not None:
        github_url = scm_node.find(".//url").text if scm_node.find(".//url") is not None else ""
        print(f"❌ Jenkinsfile pour ce job est stocké dans GitHub : {github_url}\nModifiez le Jenkinsfile directement dans le dépôt GitHub.")
        return False
    script_node = root.find(".//script")
    if script_node is not None:
        script_node.text = new_jenkinsfile_content
        new_xml = ET.tostring(root, encoding="utf-8")
        # 3. Pousser le nouveau config.xml
        headers = {"Content-Type": "application/xml"}
        put_response = requests.post(config_url, data=new_xml, headers=headers, auth=HTTPBasicAuth(username, api_token))
        if put_response.status_code not in [200, 201]:
            print(f"❌ Erreur push config.xml : {put_response.status_code} - {put_response.text}")
            return False
        print("✅ Jenkinsfile modifié avec succès !")
    else:
        print("❌ Jenkinsfile inline non trouvé dans le job.")
        return False
    # 4. Relancer le job
    build_url = f"{jenkins_url}/job/{job_name}/build"
    build_response = requests.post(build_url, auth=HTTPBasicAuth(username, api_token))
    if build_response.status_code in [201, 200]:
        print(f"✅ Job '{job_name}' relancé avec succès !")
        return True
    else:
        print(f"❌ Erreur relance job : {build_response.status_code} - {build_response.text}")
        return False

# Exemple d'utilisation
if __name__ == "__main__":
    jenkins_url = "http://localhost:8080"
    username = "yessine"
    api_token = "11f9fd1c763a2051af553ee0b8aba3889d"
    if len(sys.argv) >= 3:
        job_name = sys.argv[1]
        jenkinsfile_path = sys.argv[2]
        with open(jenkinsfile_path, "r", encoding="utf-8") as f:
            new_jenkinsfile_content = f.read()
        update_jenkinsfile_and_trigger(jenkins_url, job_name, username, api_token, new_jenkinsfile_content)
    else:
        print("Usage: python push-jenkinsfile.py <job_name> <jenkinsfile_path>")
