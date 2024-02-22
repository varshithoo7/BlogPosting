pipeline {
    agent any

    environment {
        PATH = "$HOME/.local/bin:$PATH"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Linting') {
            steps {
                sh 'flake8 .'
            }
        }
        stage('Unit Testing') {
            steps {
		sh 'which pytest'
                sh ' $HOME/.local/bin/pytest'
            }
        }
        stage('Static Code Analysis - Bandit') {
            steps {
                sh 'bandit -r .'
            }
        }
        stage('Static Code Analysis - Radon') {
            steps {
                sh 'radon cc .'
            }
        }
        // Other stages...
    }

    post {
        success {
            echo 'Tests Passed'
        }
        failure {
            echo 'Tests Failed'
        }
    }
}

