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
                script {
                    // Cette commande va faire échouer le build
                    bat 'exit 1' 
                    // Alternative : bat 'python -c "exit(1)"'
                }
            }
        }
    }

    // Ceci force Jenkins à échouer si une étape échoue
    post {
        always {
            script {
                if (currentBuild.result == 'UNSTABLE' || currentBuild.result == 'FAILURE') {
                    echo 'Build a échoué comme prévu'
                }
            }
        }
    }
}