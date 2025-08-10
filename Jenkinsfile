pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Clonage du repo...'
                checkout scm
            }
        }

        stage('Run Python App') {
            steps {
                echo '🚀 Lancement de app.py'
                bat 'python main.py'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline terminé avec succès.'
        }
        failure {
            echo '❌ Pipeline échoué à cause d’une erreur réelle dans le code.'
        }
    }
}