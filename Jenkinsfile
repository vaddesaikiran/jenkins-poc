pipeline {
    agent any

    environment {
        PYTHON_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"'
        PIP_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe"'
        SONARQUBE_URL = 'http://localhost:9000'
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        GITLEAKS_VERSION = '8.28.0'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Secret Scan with GitLeaks') {
            steps {
                script {
                    bat """
                        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_windows_x64.zip' -OutFile 'gitleaks.zip'"
                        powershell -Command "Expand-Archive -Path 'gitleaks.zip' -DestinationPath '.' -Force"
                        powershell -Command ".\\gitleaks.exe detect --source . --no-git --report-format json --report-path gitleaks-report.json"
                    """
                    if (fileExists('gitleaks-report.json')) {
                        def leaksReport = readJSON file: 'gitleaks-report.json'
                        if (leaksReport.findings?.size() > 0) {
                            echo "GitLeaks found ${leaksReport.findings.size()} potential leaks (review report)—continuing for POC."
                        } else {
                            echo "No secrets detected. 🔒"
                        }
                    } else {
                        error "GitLeaks report not generated."
                    }
                    archiveArtifacts artifacts: 'gitleaks-report.json', allowEmptyArchive: true
                }
            }
            post {
                always {
                    bat """
                        if exist gitleaks.zip del gitleaks.zip
                        if exist gitleaks.exe del gitleaks.exe
                        if exist LICENSE del LICENSE
                        if exist README.md del README.md
                    """
                }
            }
        }

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
            echo 'Build failed—check tests, leaks, or SonarQube issues.'
        }
    }
}