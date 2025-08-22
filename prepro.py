import re

class LogSanitizer:
    def __init__(self):
        # Dictionnaire de regex -> placeholder
        self.patterns = {
            # 🔐 Identifiants & secrets
            r'(?i)(password\s*=\s*[\w!@#$%^&*()_+={}\[\]:;"\'<>?,./]+)': 'password=***SECRET***',
            r'(?i)(token\s*[:=]\s*[A-Za-z0-9_\-\.=]+)': 'token=***SECRET***',
            r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----': '***PRIVATE_KEY***',
            r'(AKIA[0-9A-Z]{16})': '***AWS_KEY***',
            r'(?i)(aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]+)': 'aws_secret_access_key=***SECRET***',

            # 📂 Variables d'environnement sensibles
            r'(?i)(DB_PASSWORD\s*=\s*\S+)': 'DB_PASSWORD=***SECRET***',
            r'(?i)(Authorization:\s*Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*)': 'Authorization: Bearer ***TOKEN***',

            # 🏦 Infrastructure
            r'(?:(?:\d{1,3}\.){3}\d{1,3})': '***IP_ADDRESS***',
            r'(http[s]?:\/\/[a-zA-Z0-9\.\-]+(?:\.local|\.internal)[^\s]*)': '***INTERNAL_URL***',

            # 👥 Données personnelles (PII)
            r'[\w\.-]+@[\w\.-]+\.\w+': '***EMAIL***',
            r'\+?\d{1,3}[-.\s]?\d{2,3}[-.\s]?\d{3}[-.\s]?\d{3,4}': '***PHONE***',
            r'user_id\s*=\s*[A-Za-z0-9_-]+': 'user_id=***USER***',

            # 💳 Données financières
            r'\b(?:\d[ -]*?){13,16}\b': '***CREDIT_CARD***',
            r'[A-Z]{2}\d{2}[A-Z0-9]{11,30}': '***IBAN***',

            # 🧩 Payload sensible
            r'("password"\s*:\s*".+?")': '"password":"***SECRET***"',
            r'(spring\.datasource\.password\s*=\s*.+)': 'spring.datasource.password=***SECRET***',
        }

    def sanitize_line(self, line: str) -> str:
        """Nettoie une seule ligne de log."""
        clean_line = line
        for pattern, replacement in self.patterns.items():
            clean_line = re.sub(pattern, replacement, clean_line, flags=re.IGNORECASE | re.DOTALL)
        return clean_line

    def sanitize_log(self, log: str) -> str:
        """Nettoie un log complet (multi-lignes)."""
        return "\n".join(self.sanitize_line(line) for line in log.splitlines())


# Exemple d'utilisation
if __name__ == "__main__":
    raw_log = """
    ERROR: Login failed with password=SuperSecret123
    Using token: ghp_abcd1234efgh5678ijkl
    Connecting to 10.0.0.5:5432
    Commit by John Doe <john.doe@company.com>
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    aws_access_key_id=AKIAIOSFODNN7EXAMPLE
    aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    """

    sanitizer = LogSanitizer()
    clean_log = sanitizer.sanitize_log(raw_log)

    print("=== LOG BRUT ===")
    print(raw_log)
    print("\n=== LOG NETTOYÉ ===")
    print(clean_log)
