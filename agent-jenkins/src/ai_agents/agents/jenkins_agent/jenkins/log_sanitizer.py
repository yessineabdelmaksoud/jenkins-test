"""
Jenkins Log Sanitizer - Masque les données sensibles dans les logs Jenkins.
Basé sur le preprocessing_pipeline avec optimisations pour Jenkins.
"""

import re
import logging
from typing import Dict, Set, Optional, List


class JenkinsLogSanitizer:
    """Sanitizer optimisé pour les logs Jenkins avec masquage des données sensibles."""
    
    def __init__(self, enable_advanced_pii: bool = False):
        self.enable_advanced_pii = enable_advanced_pii
        self.sensitive_patterns = {
            # 🔐 Secrets & Credentials
            'PASSWORD': r'(?i)(password\s*[:=]\s*[^\s\'"]+)',
            'TOKEN': r'(?i)(token\s*[:=]\s*[A-Za-z0-9_\-\.=]{20,})',
            'API_KEY': r'(?i)(api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-\.=]{20,})',
            'SECRET_KEY': r'(?i)(secret[_-]?key\s*[:=]\s*[A-Za-z0-9_\-\.=]{20,})',
            'AWS_ACCESS_KEY': r'(AKIA[0-9A-Z]{16})',
            'AWS_SECRET': r'(?i)(aws_secret_access_key\s*[:=]\s*[A-Za-z0-9/+=]{40})',
            'PRIVATE_KEY': r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----',
            
            # 🔧 Jenkins spécifique
            'JENKINS_TOKEN': r'(?i)(jenkins[_-]?token\s*[:=]\s*[A-Za-z0-9_\-\.=]+)',
            'BUILD_TOKEN': r'(?i)(build[_-]?token\s*[:=]\s*[A-Za-z0-9_\-\.=]+)',
            'WEBHOOK_SECRET': r'(?i)(webhook[_-]?secret\s*[:=]\s*[A-Za-z0-9_\-\.=]+)',
            'JENKINS_API_TOKEN': r'(?i)(jenkins_api_token\s*[:=]\s*[A-Za-z0-9_\-\.=]+)',
            
            # 🌐 Infrastructure
            'INTERNAL_IP': r'\b(?:10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.(?:[0-9]{1,3}\.)[0-9]{1,3}|192\.168\.(?:[0-9]{1,3}\.)[0-9]{1,3})\b',
            'PUBLIC_IP': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'INTERNAL_URL': r'(?i)(http[s]?://[a-zA-Z0-9\.\-]+\.(?:local|internal|corp)[^\s]*)',
            
            # 🗄️ Database
            'DB_PASSWORD': r'(?i)(db[_-]?password\s*[:=]\s*[^\s\'"]+)',
            'DATABASE_URL': r'(?i)(database[_-]?url\s*[:=]\s*[^\s\'"]+)',
            'MYSQL_ROOT_PASSWORD': r'(?i)(mysql_root_password\s*[:=]\s*[^\s\'"]+)',
            'POSTGRES_PASSWORD': r'(?i)(postgres_password\s*[:=]\s*[^\s\'"]+)',
            
            # 🔗 URLs avec credentials
            'URL_WITH_CREDS': r'(?i)(https?://[^:\s]+:[^@\s]+@[^\s]+)',
            
            # 🏠 Paths sensibles
            'HOME_PATH': r'(?i)(/home/[a-zA-Z0-9_\-]+|C:\\Users\\[a-zA-Z0-9_\-]+)',
            'SSH_KEY_PATH': r'(?i)(/\.ssh/[a-zA-Z0-9_\-]+|C:\\Users\\[^\\]+\\\.ssh\\[a-zA-Z0-9_\-]+)',
            
            # 💳 Données financières
            'CREDIT_CARD': r'\b(?:\d[ -]*?){13,16}\b',
            'IBAN': r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b',
            
            # 📱 Données personnelles
            'PHONE': r'\b\+?[1-9]\d{9,14}\b',
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            
            # 🔒 Hashes & Identifiants techniques (mais on garde les commits Git courts)
            'LONG_HEX_ID': r'\b[a-f0-9]{32,}\b',  # MD5, SHA256, etc. mais pas les commits courts
            'JWT_TOKEN': r'\beyJ[A-Za-z0-9_\-]*\.[A-Za-z0-9_\-]*\.[A-Za-z0-9_\-]*\b',
            
            # 🔧 Variables d'environnement sensibles
            'JWT_SECRET': r'(?i)(jwt[_-]?secret\s*[:=]\s*[^\s\'"]+)',
            'OPENAI_API_KEY': r'(?i)(openai_api_key\s*[:=]\s*sk-[A-Za-z0-9_\-]+)',
            'OPENROUTER_API_KEY': r'(?i)(openrouter_api_key\s*[:=]\s*sk-or-[A-Za-z0-9_\-]+)',
        }
        
        # Patterns Jenkins spéciaux (plus permissifs pour préserver le contexte)
        self.jenkins_context_patterns = {
            # On garde les noms de jobs, builds, etc. mais on masque les secrets
            'BUILD_NUMBER': r'(?i)(build[_\s]+#?\d+)',
            'JOB_NAME': r'(?i)(job[_\s]+[a-zA-Z0-9_\-/]+)',
        }
        
        # Compile les regex pour de meilleures performances
        self.compiled_patterns = {}
        for name, pattern in self.sensitive_patterns.items():
            if '(?i)' in pattern:
                self.compiled_patterns[name] = re.compile(pattern, re.DOTALL)
            else:
                self.compiled_patterns[name] = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        
        # Termes sensibles additionnels spécifiques à votre environnement
        self.sensitive_terms: Set[str] = {
            'production', 'prod', 'staging', 'dev-secret', 'admin-key'
        }
        
        # Initialize advanced PII processor if requested
        self.presidio_processor = None
        if enable_advanced_pii:
            self._init_presidio()
    
    def _init_presidio(self):
        """Initialize Presidio for advanced PII detection (optional)."""
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            
            nlp_engine = NlpEngineProvider().create_engine()
            self.presidio_processor = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
            logging.info("Presidio PII processor initialized")
        except ImportError:
            logging.warning("Presidio not available, advanced PII detection disabled")
        except Exception as e:
            logging.warning(f"Failed to initialize Presidio: {e}")
    
    def sanitize_line(self, line: str) -> str:
        """Masque les données sensibles dans une ligne de log."""
        if not line or not line.strip():
            return line
            
        processed_line = line
        
        # Étape 1: Regex patterns
        for pattern_name, compiled_pattern in self.compiled_patterns.items():
            if compiled_pattern.search(processed_line):
                processed_line = compiled_pattern.sub(f'[{pattern_name}_REDACTED]', processed_line)
        
        # Étape 2: Termes sensibles simples
        for term in self.sensitive_terms:
            if term.lower() in processed_line.lower():
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                processed_line = pattern.sub('[SENSITIVE_TERM_REDACTED]', processed_line)
        
        # Étape 3: Advanced PII (si activé)
        if self.presidio_processor:
            processed_line = self._apply_presidio(processed_line)
        
        return processed_line
    
    def _apply_presidio(self, line: str) -> str:
        """Applique Presidio pour la détection PII avancée."""
        try:
            results = self.presidio_processor.analyze(text=line, language='en')
            if results:
                # Applique les remplacements de la fin vers le début pour préserver les indices
                for res in sorted(results, key=lambda r: r.start, reverse=True):
                    start, end = res.start, res.end
                    line = line[:start] + f"[{res.entity_type}_PII_REDACTED]" + line[end:]
            return line
        except Exception as e:
            logging.warning(f"Presidio processing error: {e}")
            return line
    
    def sanitize_logs(self, logs: str, max_lines: Optional[int] = None) -> str:
        """
        Masque les données sensibles dans un texte de logs complet.
        
        Args:
            logs: Texte des logs à traiter
            max_lines: Limite du nombre de lignes à traiter (None = toutes)
            
        Returns:
            Logs avec données sensibles masquées
        """
        if not logs:
            return logs
        
        lines = logs.split('\n')
        if max_lines:
            lines = lines[:max_lines]
        
        sanitized_lines = []
        for line in lines:
            sanitized_line = self.sanitize_line(line)
            sanitized_lines.append(sanitized_line)
        
        return '\n'.join(sanitized_lines)
    
    def get_sanitization_summary(self, original: str, sanitized: str) -> Dict[str, int]:
        """Retourne un résumé des modifications appliquées."""
        original_lines = original.split('\n') if original else []
        sanitized_lines = sanitized.split('\n') if sanitized else []
        
        modified_lines = 0
        redacted_count = 0
        
        for orig, san in zip(original_lines, sanitized_lines):
            if orig != san:
                modified_lines += 1
                redacted_count += san.count('_REDACTED]')
        
        return {
            'total_lines': len(original_lines),
            'modified_lines': modified_lines,
            'redacted_items': redacted_count,
            'sanitization_ratio': modified_lines / max(len(original_lines), 1)
        }


def create_jenkins_sanitizer(enable_advanced_pii: bool = False) -> JenkinsLogSanitizer:
    """Factory function pour créer un sanitizer Jenkins configuré."""
    return JenkinsLogSanitizer(enable_advanced_pii=enable_advanced_pii)


# Fonction d'utilisation rapide
def sanitize_jenkins_logs(logs: str, enable_advanced_pii: bool = False, max_lines: Optional[int] = None) -> str:
    """
    Fonction utilitaire pour masquer rapidement les données sensibles dans les logs Jenkins.
    
    Args:
        logs: Texte des logs à traiter
        enable_advanced_pii: Active la détection PII avancée avec Presidio
        max_lines: Limite du nombre de lignes à traiter
        
    Returns:
        Logs avec données sensibles masquées
    """
    sanitizer = create_jenkins_sanitizer(enable_advanced_pii)
    return sanitizer.sanitize_logs(logs, max_lines)


if __name__ == "__main__":
    # Test rapide
    test_logs = """
    Starting build for job my-app
    Setting password=secret123
    API_KEY=sk-1234567890abcdef
    Database connection: mysql://user:password@localhost:3306/db
    Email notification sent to admin@company.com
    Build completed successfully
    """
    
    sanitizer = create_jenkins_sanitizer()
    cleaned = sanitizer.sanitize_logs(test_logs)
    print("Original:")
    print(test_logs)
    print("\nSanitized:")
    print(cleaned)
    
    summary = sanitizer.get_sanitization_summary(test_logs, cleaned)
    print(f"\nSummary: {summary}")
