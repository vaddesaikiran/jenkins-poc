pipeline {
    agent any

    environment {
        PYTHON_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"'
        PIP_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe"'
        SONARQUBE_URL = 'http://localhost:9000'
        SONARQUBE_TOKEN = credentials('sonarqube-token')  // Secure: Pulls from Jenkins Credentials
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        // Temp skip GitLeaks for POC - re-add later with custom config
        // stage('Secret Scan with GitLeaks') { ... }

        stage('Install Dependencies') {
            steps {
                bat "${PIP_PATH} install -r requirements.txt"
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                bat "${PYTHON_PATH} -m pytest --cov=. --cov-report=xml --cov-report=term-missing -v"
                junit '**/test-results/*.xml'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv(installationName: 'Local SonarQube') {
                        bat """
                            ${scannerHome}/bin/sonar-scanner.bat ^
                            -Dsonar.projectKey=Jenkins-POC ^
                            -Dsonar.sources=. ^
                            -Dsonar.tests=. ^
                            -Dsonar.python.coverage.reportPaths=coverage.xml ^
                            -Dsonar.test.reportPath=**/test-results/*.xml ^
                            -Dsonar.host.url=${SONARQUBE_URL} ^
                            -Dsonar.login=${SONARQUBE_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline green! Tests passed, coverage analyzed, quality gate cleared. Merge away! 🎉'
        }
        failure {
            echo 'Build failed—check tests or SonarQube issues.'
        }
    }
}