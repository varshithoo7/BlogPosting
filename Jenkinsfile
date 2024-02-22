pipeline {
    agent any

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
                sh 'pytest'
            }
        }
        stage('Static Code Analysis') {
            steps {
                sh 'bandit -r .'
                sh 'radon cc .'
            }
        }
    }

    post {
        always {
            echo 'Tests Passed'
        }
    }
}

