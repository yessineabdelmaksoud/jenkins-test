pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                bat 'python --version'
                bat 'pip --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install flask pytest'
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Cette commande retournera un code 1 si un test échoue
                    def testExitCode = bat(script: 'python -m pytest test_app.py -v', returnStatus: true)
                    
                    if (testExitCode != 0) {
                        // Génère un échec Jenkins avec les logs
                        bat '''
                            echo "=== LOGS D'ÉCHEC ==="
                            echo "Dernier test exécuté : test_failure"
                            echo "Erreur : AssertionError: Échec simulé pour tester Jenkins"
                            echo "Stack trace :"
                            echo "  File \"test_app.py\", line 10, in test_failure"
                            echo "    assert False, \"Échec simulé pour tester Jenkins\""
                        '''
                        error("Les tests ont échoué avec le code ${testExitCode}")
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "=== NOTIFICATION D'ÉCHEC ==="
            archiveArtifacts artifacts: '**/test.log', allowEmptyArchive: true
        }
        always {
            bat 'taskkill /F /IM python.exe /T 2>NUL || exit 0'
        }
    }
}