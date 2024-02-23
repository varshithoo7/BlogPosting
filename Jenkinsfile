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
               sh '~/.local/bin/pytest'
            }
        }
        stage('Static Code Analysis - Bandit') {
    steps {
        script {
            def banditOutput = sh(script: '/var/lib/jenkins/.local/bin/bandit -r .', returnStdout: true).trim()

            // Extract the section of Bandit output related to severity issues
            def severitySection = banditOutput =~ /Total issues \(by severity\):(.*?)Total issues \(by confidence\)/s
            def highSeverityIssuesFound = severitySection[0][1].contains("High: 0")

            if (highSeverityIssuesFound) {
                echo "No high severity issues found. Proceeding to next stage (Radon)."
            } else {
                echo "High severity issues found. Cancelling subsequent stages."
                currentBuild.result = 'FAILURE' // Set the build result to FAILURE
                error("High severity issues found. Cancelling subsequent stages.")
            }
        }
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
	}
