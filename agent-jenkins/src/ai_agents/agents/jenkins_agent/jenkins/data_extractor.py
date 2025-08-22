"""
Data extractor for Jenkins jobs.
Extracts build logs, Jenkinsfile content, and metadata from Jenkins API.
Basé sur le code fonctionnel de l'utilisateur.
Includes sensitive data sanitization for logs.
"""

import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import json
from typing import Dict, Any, Optional
from urllib.parse import quote
from .log_sanitizer import create_jenkins_sanitizer


def _normalize_job_path(job_name_or_path: str) -> str:
    """Convert a job name like 'foo' or 'folder/sub' into 'job/foo' or 'job/folder/job/sub'.
    If already contains 'job/' segments, keep as-is (trim leading/trailing slashes).
    URL-encode each segment to handle spaces and special chars.
    """
    s = (job_name_or_path or '').strip('/')
    if not s:
        return ''
    if s.startswith('job/') or '/job/' in s:
        return s.strip('/')
    parts = [quote(p) for p in s.split('/') if p]
    return 'job/' + '/job/'.join(parts)


def extract_complete_data(jenkins_url: str, job_name: str, build_number: int, 
                         username: Optional[str] = None, api_token: Optional[str] = None,
                         sanitize_logs: bool = True, enable_advanced_pii: bool = False) -> Dict[str, Any]:
    """
    Extrait toutes les données Jenkins et retourne un dictionnaire.
    
    Args:
        jenkins_url: URL de base Jenkins
        job_name: Nom du job Jenkins
        build_number: Numéro du build
        username: Nom d'utilisateur Jenkins (optionnel)
        api_token: Token API Jenkins (optionnel)
        sanitize_logs: Active le masquage des données sensibles dans les logs
        enable_advanced_pii: Active la détection PII avancée avec Presidio
    
    Returns:
        Dictionnaire avec toutes les données extraites
    """
    
    # Configuration d'authentification
    auth = HTTPBasicAuth(username, api_token) if username and api_token else None
    
    # Initialiser le sanitizer si demandé
    sanitizer = None
    if sanitize_logs:
        sanitizer = create_jenkins_sanitizer(enable_advanced_pii=enable_advanced_pii)
    
    base = jenkins_url.rstrip('/')
    job_path = _normalize_job_path(job_name)

    # 1. Extraire le Jenkinsfile
    jenkinsfile_content = ""
    try:
        config_url = f"{base}/{job_path}/config.xml"
        response = requests.get(config_url, auth=auth, timeout=30)
        if response.status_code == 200:
            xml_content = response.text
            root = ET.fromstring(xml_content)

            # Cas 1 : Jenkinsfile dans Git (Pipeline from SCM)
            scm_node = root.find('.//scm')
            if scm_node is not None:
                # URL du repo (Git plugin)
                url_node = (
                    root.find('.//scm//userRemoteConfigs//hudson.plugins.git.UserRemoteConfig//url')
                    or root.find('.//scm//url')
                )
                # Branche (BranchSpec)
                branch_node = root.find('.//scm//branches//hudson.plugins.git.BranchSpec//name')
                # Chemin du Jenkinsfile
                script_path_node = root.find('.//definition//scriptPath') or root.find('.//scriptPath')

                repo_url = url_node.text.strip() if (url_node is not None and url_node.text) else ''
                branch = branch_node.text.strip() if (branch_node is not None and branch_node.text) else 'main'
                if branch.startswith('*/'):
                    branch = branch[2:]
                script_path = script_path_node.text.strip() if (script_path_node is not None and script_path_node.text) else 'Jenkinsfile'

                # Support GitHub raw URL; for other providers skip (optionnel: ajouter mapping GitLab/Bitbucket)
                if repo_url.startswith('https://github.com/'):
                    github_raw_url = repo_url.replace('https://github.com/', 'https://raw.githubusercontent.com/')
                    if github_raw_url.endswith('.git'):
                        github_raw_url = github_raw_url[:-4]
                    file_url = f"{github_raw_url}/{branch}/{script_path}"
                    git_response = requests.get(file_url, timeout=30)
                    if git_response.status_code == 200:
                        jenkinsfile_content = git_response.text

            # Cas 2 : Jenkinsfile inline (Pipeline script)
            if not jenkinsfile_content:
                script_node = root.find('.//definition//script') or root.find('.//script')
                if script_node is not None and script_node.text:
                    jenkinsfile_content = script_node.text

    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction du Jenkinsfile: {e}")

    # 2. Extraire les logs de build
    console_log_content = ""
    sanitized_console_log = ""
    try:
        log_url = f"{base}/{job_path}/{build_number}/consoleText"
        response = requests.get(log_url, auth=auth, timeout=30)
        if response.status_code == 200:
            console_log_content = response.text
            # Appliquer la sanitization si demandée
            if sanitizer:
                sanitized_console_log = sanitizer.sanitize_logs(console_log_content)
                print(f"🔒 Logs sanitized - Original: {len(console_log_content)} chars, Sanitized: {len(sanitized_console_log)} chars")
            else:
                sanitized_console_log = console_log_content
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des logs: {e}")

    # 3. Extraire les métadonnées du build
    build_metadata = {}
    try:
        api_url = f"{base}/{job_path}/{build_number}/api/json"
        response = requests.get(api_url, auth=auth, timeout=30)
        if response.status_code == 200:
            build_metadata = response.json()
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des métadonnées: {e}")

    # 4. Extraire les informations des agents/nodes
    agents_data = []
    try:
        url = f"{jenkins_url}/computer/api/json"
        response = requests.get(url, auth=auth, timeout=30)
        if response.status_code == 200:
            agents_data = response.json().get('computer', [])
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des agents: {e}")

    # 5. Construire le dictionnaire final selon la structure demandée
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
        "console_log": sanitized_console_log,  # Logs sanitized (or original if sanitization disabled)
        "console_log_raw": console_log_content if sanitize_logs else "",  # Original logs kept only if sanitization is enabled
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
        "os": first_agent.get("description", ""),
        "metadata": build_metadata
    }

    # Ajouter des informations de sanitization si activée
    if sanitizer and sanitize_logs:
        sanitization_summary = sanitizer.get_sanitization_summary(console_log_content, sanitized_console_log)
        final_data["sanitization_info"] = {
            "enabled": True,
            "advanced_pii": enable_advanced_pii,
            "summary": sanitization_summary
        }
        print(f"🔒 Sanitization summary: {sanitization_summary['modified_lines']} lines modified, {sanitization_summary['redacted_items']} items redacted")
    else:
        final_data["sanitization_info"] = {"enabled": False}

    print(f"✅ Extraction terminée - Status: {final_data['status']}, Console log: {len(sanitized_console_log)} chars")
    return final_data
