pipeline {
    agent any

    stages {
        stage('Install dependencies') {
            steps {
                bat 'pip install -r requirements.tx'
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
                // Ici tu pourrais lancer ton app avec gunicorn, docker, etc.
            }
        }
    }
}
