import re

# Essayer d'initialiser Presidio proprement ; tolérer son absence
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    try:
        _nlp_engine = NlpEngineProvider().create_engine()
        analyzer = AnalyzerEngine(nlp_engine=_nlp_engine, supported_languages=["en"])
    except Exception:
        # si l'initialisation échoue (pas de modèle spaCy, erreur d'environnement...), on désactive Presidio
        analyzer = None
except Exception:
    analyzer = None

# Mots sensibles internes
sensitive_terms = {"DB_PROD", "SECRET_KEY", "salary", "ssn"}

# Regex rapides (TOKEN compilé avec IGNORECASE au lieu d'un flag inline)
REGEX_PATTERNS = {
    "IP": re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "URL": re.compile(r"https?://[^\s]+"),
    "TOKEN": re.compile(r"(AKIA[0-9A-Z]{16}|password\s*=\s*.+)", re.IGNORECASE)
}


def mask(text, tag="[REDACTED]"):
    return tag


def process_line(line: str) -> str:
    # Supprimer la fin de ligne pour éviter des lignes vides en sortie
    original = line.rstrip('\r\n')
    proc = original

    # 1. Regex rapides
    for name, pattern in REGEX_PATTERNS.items():
        proc = pattern.sub(f"[{name}_REDACTED]", proc)

    # 2. Presidio (si disponible)
    if analyzer:
        try:
            results = analyzer.analyze(text=proc, language="en")
            # Appliquer les remplacements de la fin vers le début pour conserver la validité des indices
            for res in sorted(results, key=lambda r: r.start, reverse=True):
                start, end = res.start, res.end
                proc = proc[:start] + f"[{res.entity_type}_REDACTED]" + proc[end:]
        except Exception:
            # En cas d'erreur durant l'analyse, continuer sans Presidio
            pass

    # 3. Règles internes simples
    for term in sensitive_terms:
        if term in proc:
            proc = proc.replace(term, f"[{term}_REDACTED]")

    return proc


def sanitize_log(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as fin, \
         open(output_file, "w", encoding="utf-8") as fout:
        for line in fin:
            fout.write(process_line(line) + "\n")


# Exemple d'utilisation simple
if __name__ == "__main__":
    # Remplacer par vos fichiers si vous testez localement
    try:
        sanitize_log("build_yessine_1_console.log", "jenkinssanitized.log")
        print("Sanitisation terminée")
    except FileNotFoundError:
        print("Fichier d'entrée introuvable")
