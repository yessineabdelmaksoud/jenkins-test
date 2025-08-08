pipeline {
    agent any

    stages {
        stage('Install dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                bat 'pytest'
            }
        }
        
        stage('Deploy') {
            steps {
                bat 'echo "Déploiement de l\'application..."'
            }
        }
        
        stage('Fail Me') {
            steps {
                // Méthode 1 : Exit code 1 + errorHandler
                bat 'exit 1' 
                // OU Méthode 2 : Commande qui échoue
                bat 'python -c "raise Exception(\'Erreur simulée!\')"'
            }
        }
    }
    
    // Optionnel : Comportement en cas d'échec
    post {
        failure {
            echo 'Le build a échoué (comme prévu pour le test).'
        }
    }
}