import re
import json
import logging
from typing import Iterator, Dict, Set, Optional
from pathlib import Path

class StreamingLogReader:
    """Lecteur de logs en streaming pour traiter ligne par ligne."""
    
    def __init__(self, file_path: str, chunk_size: int = 8192):
        self.file_path = file_path
        self.chunk_size = chunk_size
    
    def read_lines(self) -> Iterator[str]:
        """Générateur qui lit le fichier ligne par ligne."""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    yield line.rstrip('\n\r')
        except FileNotFoundError:
            logging.error(f"Fichier non trouvé: {self.file_path}")
            raise
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du fichier: {e}")
            raise

class RegexFilters:
    """Étape 1: Filtres regex rapides pour détecter les données sensibles."""
    
    def __init__(self):
        self.patterns = {
            # 🔐 Identifiants & secrets
            'PASSWORD': r'(?i)(password\s*[:=]\s*[^\s\'"]+)',
            'TOKEN': r'(?i)(token\s*[:=]\s*[A-Za-z0-9_\-\.=]{20,})',
            'API_KEY': r'(?i)(api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-\.=]{20,})',
            'SECRET_KEY': r'(?i)(secret[_-]?key\s*[:=]\s*[A-Za-z0-9_\-\.=]{20,})',
            'AWS_ACCESS_KEY': r'(AKIA[0-9A-Z]{16})',
            'AWS_SECRET': r'(?i)(aws_secret_access_key\s*[:=]\s*[A-Za-z0-9/+=]{40})',
            'PRIVATE_KEY': r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----',
            
            # 🌐 Infrastructure
            'IP_ADDRESS': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'URL': r'https?://[^\s<>"\']+',
            'INTERNAL_URL': r'(?i)(http[s]?://[a-zA-Z0-9\.\-]+\.(?:local|internal|corp)[^\s]*)',
            
            # 💳 Données financières
            'CREDIT_CARD': r'\b(?:\d[ -]*?){13,16}\b',
            'IBAN': r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b',
            
            # 📱 Données personnelles
            'PHONE': r'\b\+?[1-9]\d{9,14}\b',  # Au moins 10 chiffres pour un vrai téléphone
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            
            # 🔒 Hashes & Identifiants techniques
            'GIT_COMMIT': r'\b[a-f0-9]{40}\b',  # Hash Git SHA-1 (40 caractères hexadécimaux)
            'MD5_HASH': r'\b[a-f0-9]{32}\b',    # Hash MD5 (32 caractères hexadécimaux)
            'SHA256_HASH': r'\b[a-f0-9]{64}\b', # Hash SHA-256 (64 caractères hexadécimaux)
            'HEX_ID': r'\b[a-f0-9]{16,}\b',     # Identifiants hexadécimaux longs (16+ caractères)
            
            # 🔧 Variables d'environnement
            'DB_PASSWORD': r'(?i)(db[_-]?password\s*[:=]\s*[^\s\'"]+)',
            'DATABASE_URL': r'(?i)(database[_-]?url\s*[:=]\s*[^\s\'"]+)',
            'JWT_SECRET': r'(?i)(jwt[_-]?secret\s*[:=]\s*[^\s\'"]+)',
            
            # 🏢 Jenkins spécifique
            'JENKINS_TOKEN': r'(?i)(jenkins[_-]?token\s*[:=]\s*[A-Za-z0-9_\-\.=]+)',
            'BUILD_TOKEN': r'(?i)(build[_-]?token\s*[:=]\s*[A-Za-z0-9_\-\.=]+)',
        }
        
        # Compile les regex pour de meilleures performances
        # Note: certains patterns ont déjà (?i) donc pas besoin de re.IGNORECASE pour tous
        self.compiled_patterns = {}
        for name, pattern in self.patterns.items():
            # Si le pattern contient déjà (?i), on compile sans IGNORECASE
            if '(?i)' in pattern:
                self.compiled_patterns[name] = re.compile(pattern, re.DOTALL)
            else:
                self.compiled_patterns[name] = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    
    def process_line(self, line: str) -> str:
        """Applique les filtres regex sur une ligne."""
        processed_line = line
        
        for pattern_name, compiled_pattern in self.compiled_patterns.items():
            if compiled_pattern.search(processed_line):
                processed_line = compiled_pattern.sub(f'[{pattern_name}_REDACTED]', processed_line)
        
        return processed_line

class PresidioProcessor:
    """Étape 2: Détection PII avancée avec Presidio (optionnel)."""
    
    def __init__(self):
        self.analyzer = None
        self.anonymizer = None
        self._init_presidio()
    
    def _init_presidio(self):
        """Initialize Presidio (si disponible) avec initialisation correcte."""
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            from presidio_anonymizer import AnonymizerEngine
            
            try:
                # Initialisation correcte via NlpEngineProvider
                nlp_engine = NlpEngineProvider().create_engine()
                self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
                self.anonymizer = AnonymizerEngine()
                logging.info("Presidio initialisé avec succès")
            except Exception as e:
                logging.warning(f"Impossible d'initialiser Presidio (NLP/model): {e}")
                self.analyzer = None
                self.anonymizer = None
        except ImportError:
            logging.warning("Presidio non disponible, étape PII avancée ignorée")
    
    def process_line(self, line: str) -> str:
        """Traite une ligne avec Presidio si disponible."""
        if not self.analyzer or not self.anonymizer:
            return line
        
        try:
            # Analyse des entités PII
            results = self.analyzer.analyze(text=line, language='en')
            
            # Anonymisation - appliquer les remplacements de la fin vers le début
            # pour préserver les indices
            if results:
                for res in sorted(results, key=lambda r: r.start, reverse=True):
                    start, end = res.start, res.end
                    line = line[:start] + f"[{res.entity_type}_REDACTED]" + line[end:]
                return line
            else:
                return line
        except Exception as e:
            logging.warning(f"Erreur Presidio: {e}")
            return line

class BusinessRulesProcessor:
    """Étape 3: Règles métier et dictionnaire interne."""
    
    def __init__(self, sensitive_terms_file: Optional[str] = None):
        self.sensitive_terms: Set[str] = set()
        self.case_sensitive_terms: Set[str] = set()
        
        if sensitive_terms_file:
            self.load_sensitive_terms(sensitive_terms_file)
    
    def load_sensitive_terms(self, file_path: str):
        """Charge le dictionnaire des termes sensibles."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Termes insensibles à la casse
            self.sensitive_terms.update(
                term.lower() for term in data.get('case_insensitive', [])
            )
            
            # Termes sensibles à la casse
            self.case_sensitive_terms.update(data.get('case_sensitive', []))
            
            logging.info(f"Chargé {len(self.sensitive_terms)} termes insensibles à la casse")
            logging.info(f"Chargé {len(self.case_sensitive_terms)} termes sensibles à la casse")
            
        except FileNotFoundError:
            logging.warning(f"Fichier de termes sensibles non trouvé: {file_path}")
        except json.JSONDecodeError as e:
            logging.error(f"Erreur parsing JSON: {e}")
    
    def process_line(self, line: str) -> str:
        """Applique les règles métier sur une ligne."""
        processed_line = line
        
        # Recherche des termes sensibles à la casse
        for term in self.case_sensitive_terms:
            if term in processed_line:
                processed_line = processed_line.replace(term, '[REDACTED]')
        
        # Recherche des termes insensibles à la casse
        line_lower = processed_line.lower()
        for term in self.sensitive_terms:
            if term in line_lower:
                # Recherche et remplacement avec préservation de la casse
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                processed_line = pattern.sub('[REDACTED]', processed_line)
        
        return processed_line

class LogPreprocessingPipeline:
    """Pipeline principal de préprocessing des logs."""
    
    def __init__(self, sensitive_terms_file: Optional[str] = None):
        self.regex_filters = RegexFilters()
        self.presidio_processor = PresidioProcessor()
        self.business_rules = BusinessRulesProcessor(sensitive_terms_file)
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def process_line(self, line: str) -> str:
        """Traite une ligne à travers toute la pipeline."""
        # Étape 1: Filtres regex
        processed_line = self.regex_filters.process_line(line)
        
        # Étape 2: Presidio (PII avancée)
        processed_line = self.presidio_processor.process_line(processed_line)
        
        # Étape 3: Règles métier
        processed_line = self.business_rules.process_line(processed_line)
        
        return processed_line
    
    def preprocess_logs(self, input_file: str, output_file: str) -> Dict[str, int]:
        """
        Préprocesse un fichier de logs complet.
        
        Args:
            input_file: Chemin vers le fichier de logs d'entrée
            output_file: Chemin vers le fichier de logs nettoyé
            
        Returns:
            Statistiques du traitement
        """
        stats = {
            'lines_processed': 0,
            'lines_modified': 0,
            'file_size_input': 0,
            'file_size_output': 0
        }
        
        try:
            # Taille du fichier d'entrée
            stats['file_size_input'] = Path(input_file).stat().st_size
            
            # Traitement streaming
            reader = StreamingLogReader(input_file)
            
            with open(output_file, 'w', encoding='utf-8') as output:
                for original_line in reader.read_lines():
                    processed_line = self.process_line(original_line)
                    
                    # Écriture de la ligne traitée
                    output.write(processed_line + '\n')
                    
                    # Statistiques
                    stats['lines_processed'] += 1
                    if processed_line != original_line:
                        stats['lines_modified'] += 1
                    
                    # Log de progression (chaque 10000 lignes)
                    if stats['lines_processed'] % 10000 == 0:
                        logging.info(f"Traité {stats['lines_processed']} lignes")
            
            # Taille du fichier de sortie
            stats['file_size_output'] = Path(output_file).stat().st_size
            
            logging.info(f"Préprocessing terminé: {stats}")
            return stats
            
        except Exception as e:
            logging.error(f"Erreur durant le préprocessing: {e}")
            raise

# Fonction principale d'utilisation
def preprocess_logs(input_file: str, output_file: str, sensitive_terms_file: Optional[str] = None) -> Dict[str, int]:
    """
    Fonction principale pour préprocesser les logs Jenkins.
    
    Args:
        input_file: Chemin vers le fichier de logs d'entrée
        output_file: Chemin vers le fichier de logs nettoyé
        sensitive_terms_file: Chemin vers le fichier JSON des termes sensibles (optionnel)
        
    Returns:
        Statistiques du traitement
    """
    pipeline = LogPreprocessingPipeline(sensitive_terms_file)
    return pipeline.preprocess_logs(input_file, output_file)

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple d'utilisation
    input_log = "build_yessine_1_console.log"
    output_log = "jenkins_build_cleaned.log"
    sensitive_terms = "sensitive_terms.json"
    
    try:
        stats = preprocess_logs(input_log, output_log, sensitive_terms)
        print(f"Traitement terminé avec succès: {stats}")
    except Exception as e:
        print(f"Erreur: {e}")
