pipeline {
    agent any


    environment {
        PYTHON_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"'
        PIP_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe"'
        scannerHome = tool 'SonarScanner'
        SONARQUBE_URL = 'http://localhost:9000'
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        SNYK_TOKEN = credentials('snyk-token')

    }

    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/vaddesaikiran/jenkins-poc.git', branch: 'main'
            }
        }


        stage('Set Build Info') {
            steps {
                script {
                    // Get short commit hash for display name
                    def commitHash = env.GIT_COMMIT?.take(7) ?: 'unknown'
                    currentBuild.displayName = "#${BUILD_NUMBER} (Commit: ${commitHash})"
                    
                    // Get the full commit message
                    def commitMsg = bat(script: 'git log -1 --pretty=%%B', returnStdout: true).trim()
                    if (commitMsg) {
                        currentBuild.description = "Commit Message: ${commitMsg}"
                    } else {
                        currentBuild.description = "No commit message available."
                    }
                    
                    echo "Build display name set to: ${currentBuild.displayName}"
                    echo "Build description set to: ${currentBuild.description}"
                }
            }
        }

        stage('Clean Old Reports') {
            steps {
                script {
                    echo 'Deleting old GitLeaks report files if any...'
                    bat 'if exist gitleaks-report.json del gitleaks-report.json'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                bat "${PIP_PATH} install -r requirements.txt"
            }
        }

        stage('Secret Scan with GitLeaks') {
            steps {
                script {
                    echo 'Running GitLeaks scan for secrets...'
                    bat '''
                        docker pull zricethezav/gitleaks:latest
                        docker run --rm -v "%cd%:/repo" zricethezav/gitleaks:latest detect \
                            --source=/repo \
                            --no-git \
                            --exit-code 1 \
                            --verbose
                    '''
                    if (currentBuild.resultIsWorseOrEqualTo('FAILURE')) {
                        error "❌ GitLeaks detected secrets. Failing the build."
                    } else {
                        echo "✅ GitLeaks scan passed. No secrets found."
                    }
                }
            }
        }

        stage('Snyk Scan') {
            steps {
                script {
                    echo 'Running Snyk scan for vulnerabilities...'
                    bat '''
                        docker pull snyk/snyk:gradle-8-jdk21-preview
                        docker run --rm -e SNYK_TOKEN=%SNYK_TOKEN% -v "%cd%:/app" snyk/snyk:gradle-8-jdk21-preview test --file=/app/requirements.txt
                    '''
                    if (currentBuild.resultIsWorseOrEqualTo('FAILURE')) {
                        error "❌ Snyk detected vulnerabilities. Failing the build."
                    } else {
                        echo "✅ Snyk scan passed. No vulnerabilities found."
                    }
                }
            }
        }

        i will add only this part is this fine


        // NEW: Qualys Container Security Scan
        stage('Qualys Container Security Scan') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'qualys-api-cred', usernameVariable: 'QUALYS_USERNAME', passwordVariable: 'QUALYS_PASSWORD')]) {
                    script {
                        echo 'Running Qualys Container Security Scan...'
                        bat """
                            docker pull qualys/secpod:cs-scanner
                            docker run --rm ^
                                -e QUALYS_USERNAME=%QUALYS_USERNAME% ^
                                -e QUALYS_PASSWORD=%QUALYS_PASSWORD% ^
                                -v "%cd%:/workspace" ^
                                qualys/secpod:cs-scanner ^
                                --image-name jenkins-poc-app ^
                                --source-type local ^
                                --local-path /workspace ^
                                --report-name qualys-scan-report.html ^
                                --report-format html
                        """
                    }
                }
            }
            post {
                always {
                    script {
                        if (fileExists('qualys-scan-report.html')) {
                            echo "✅ Qualys Container Security scan completed - report generated"
                            archiveArtifacts artifacts: 'qualys-scan-report.html', allowEmptyArchive: true
                        } else {
                            echo "⚠️ Qualys scan completed but no HTML report found"
                        }
                    }
                }
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                bat "${PYTHON_PATH} -m pytest --cov=. --cov-report=xml --cov-report=term-missing --junitxml=test-results.xml -v"
                junit '**/test-results.xml'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv(installationName: 'SonarScanner') {
                    bat """
                        ${scannerHome}\\bin\\sonar-scanner.bat ^
                        -Dsonar.projectKey=my_project ^
                        -Dsonar.sources=. ^
                        -Dsonar.tests=. ^
                        -Dsonar.test.inclusions=test_main.py ^
                        -Dsonar.python.coverage.reportPaths=coverage.xml ^
                        -Dsonar.python.xunit.reportPaths=test-results.xml ^
                        -Dsonar.host.url=${SONARQUBE_URL} ^
                        -Dsonar.token=${SONARQUBE_TOKEN}
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    def qg = waitForQualityGate()
                    if (qg.status != 'OK') {
                        error "❌ SonarQube quality gate failed: ${qg.status}"
                    } else {
                        echo "✅ SonarQube quality gate passed!"
                    }
                }
            }
        }
    }
}


