#!/usr/bin/env python3
"""
Script de test pour la pipeline de preprocessing des logs Jenkins.
"""

import tempfile
import os
from prepor.preprocessing_pipeline import preprocess_logs

def create_test_log():
    """Crée un fichier de log de test avec des données sensibles."""
    test_log_content = """
[2025-01-15 10:30:15] INFO: Starting build for project_alpha
[2025-01-15 10:30:16] DEBUG: Connecting to database at 192.168.1.100:5432
[2025-01-15 10:30:17] ERROR: Authentication failed with password=SuperSecret123
[2025-01-15 10:30:18] INFO: Using API key: sk-abcd1234efgh5678ijkl
[2025-01-15 10:30:19] DEBUG: JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
[2025-01-15 10:30:20] INFO: User john.doe@company.com started deployment
[2025-01-15 10:30:21] DEBUG: Internal URL: http://internal.corp/api/v1/deploy
[2025-01-15 10:30:22] ERROR: Failed to connect to PROD_DB_HOST
[2025-01-15 10:30:23] INFO: Credit card transaction: 4532-1234-5678-9012
[2025-01-15 10:30:24] DEBUG: Employee SSN: 123-45-6789
[2025-01-15 10:30:25] INFO: Phone contact: +1-555-123-4567
[2025-01-15 10:30:26] ERROR: Database password leaked: db_password=MySecretPass
[2025-01-15 10:30:27] INFO: AWS credentials: AKIAIOSFODNN7EXAMPLE
[2025-01-15 10:30:28] DEBUG: Secret key: aws_secret_access_key=wJalrXUtnFEMI/K7MDENG
[2025-01-15 10:30:29] INFO: Jenkins token: jenkins_token=abc123def456ghi789
[2025-01-15 10:30:30] ERROR: Salary information leaked: salary=75000
[2025-01-15 10:30:31] INFO: Build completed successfully
"""
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(test_log_content)
        return f.name

def test_preprocessing():
    """Test de la pipeline de preprocessing."""
    print("🧪 Test de la pipeline de preprocessing des logs")
    
    # Créer un log de test
    input_file = create_test_log()
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='_cleaned.log').name
    sensitive_terms_file = "sensitive_terms.json"
    
    try:
        print(f"📝 Fichier d'entrée: {input_file}")
        print(f"📄 Fichier de sortie: {output_file}")
        print(f"📚 Termes sensibles: {sensitive_terms_file}")
        
        # Exécuter le preprocessing
        stats = preprocess_logs(input_file, output_file, sensitive_terms_file)
        
        print("\n📊 Statistiques du traitement:")
        print(f"  - Lignes traitées: {stats['lines_processed']}")
        print(f"  - Lignes modifiées: {stats['lines_modified']}")
        print(f"  - Taille d'entrée: {stats['file_size_input']} bytes")
        print(f"  - Taille de sortie: {stats['file_size_output']} bytes")
        
        # Afficher le résultat
        print("\n🔍 Comparaison des logs:")
        
        print("\n--- LOG ORIGINAL ---")
        with open(input_file, 'r') as f:
            original_lines = f.readlines()[:10]  # Premières 10 lignes
            for i, line in enumerate(original_lines, 1):
                print(f"{i:2d}: {line.strip()}")
        
        print("\n--- LOG NETTOYÉ ---")
        with open(output_file, 'r') as f:
            cleaned_lines = f.readlines()[:10]  # Premières 10 lignes
            for i, line in enumerate(cleaned_lines, 1):
                print(f"{i:2d}: {line.strip()}")
        
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
    
    finally:
        # Nettoyer les fichiers temporaires
        try:
            os.unlink(input_file)
            os.unlink(output_file)
        except:
            pass

if __name__ == "__main__":
    test_preprocessing()
