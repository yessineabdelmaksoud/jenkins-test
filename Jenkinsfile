pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                echo 'Setting up Python environment...'
                bat 'python --version'
                bat 'pip --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                bat 'pip install flask pytest'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                script {
                    try {
                        // Exécution des tests
                        bat 'python -m pytest test_app.py -v'
                        
                        // Simulation d'échec (optionnel)
                        bat '''
                            echo Simulating a test failure...
                            echo These would be your test logs showing what went wrong
                            echo ERROR: Test "test_expected_failure" failed
                            echo AssertionError: Expected "Wrong Text" but got "Hello, Jenkins Pipeline!"
                            exit /b 1
                        '''
                    } catch (Exception e) {
                        echo "Caught exception: ${e}"
                        currentBuild.result = 'FAILURE'
                        error('Tests failed - check logs for details')
                    }
                }
            }
        }

        stage('Run Application') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                echo 'Starting application...'
                bat 'start /B python app.py'
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed - sending notifications...'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        always {
            echo 'Cleaning up...'
            bat 'taskkill /F /IM python.exe /T || exit 0'
        }
    }
}