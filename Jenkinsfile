pipeline {
    agent any
    environment {
        MYSQL_PASSWORD = credentials('MYSQL_PASSWORD')
	FLASK_SECRET_KEY = credentials('FLASK_SECRET_KEY')
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
               script {
                    def banditOutput = sh(script: '/var/lib/jenkins/.local/bin/bandit -r .', returnStdout: true).trim()

                    // Parse Bandit output to check for high severity issues
                    def highSeverityIssuesFound = banditOutput.contains("High: ")

                    if (highSeverityIssuesFound) {
                        echo "High severity issues found. Cancelling subsequent stages."
                        currentBuild.result = 'FAILURE' // Set the build result to FAILURE
                        error("High severity issues found. Cancelling subsequent stages.")
                    } else {
                        echo "No high severity issues found. Proceeding with subsequent stages."
                    }
                }
            }
            }
        }
        stage('Static Code Analysis - Bandit') {
            steps {
                sh '~/.local/bin/bandit -r .'
            }
        }
        stage('Static Code Analysis - Radon') {
            steps {
                sh '~/.local/bin/radon cc .'
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
