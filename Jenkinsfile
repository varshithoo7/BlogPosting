pipeline {
    agent any
    environment {
        MYSQL_PASSWORD = credentials('MYSQL_PASSWORD')
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
	stage('Print Environment') {
 	   steps {
        	sh 'printenv'
   	    }		
	}
        stage('Linting') {
            steps {
                sh 'flake8 .'
            }
        }
        stage('Unit Testing') {
            steps {
                sh '~/.local/bin/pytest'
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
        failure {
            echo 'Tests Failed'
        }
	success {
	    echo 'Tests Passed'
    }
}
}
