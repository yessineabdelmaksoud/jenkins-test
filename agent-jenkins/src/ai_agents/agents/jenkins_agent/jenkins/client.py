"""Minimal Jenkins API client wrapper (skeleton)."""

import requests
from typing import Optional


class JenkinsClient:
    def __init__(self, base_url: str, username: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, token) if username and token else None

    def get_build(self, job_name: str, build_number: int):
        url = f"{self.base_url}/job/{job_name}/{build_number}/api/json"
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        return r.json()

    def get_build_logs(self, job_name: str, build_number: int):
        url = f"{self.base_url}/job/{job_name}/{build_number}/consoleText"
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        return r.text

    def trigger_build(self, job_name: str, params: dict = None):
        url = f"{self.base_url}/job/{job_name}/build"
        r = requests.post(url, auth=self.auth, params=params)
        r.raise_for_status()
        return r.status_code
