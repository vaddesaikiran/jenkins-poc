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


        stage('Qualys Host Scanning') {
            steps {
                script {
                    echo 'Running Qualys Host Scan for vulnerabilities on 192.168.0.151...'
                    qualysVMScan(
                        credentialsId: 'qualys-vm-creds',
                        portalUrl: 'https://qualysguard.qg1.apps.qualys.in',  // Your India portal
                        targetHosts: '192.168.0.151',  // Your IP
                        scanType: 'Full Scan',  // Matches your manual test
                        failOnCritical: true,  // Fail on critical vulns
                        pollFrequency: 1,  // Poll every 1 min
                        timeout: 10  // 10 min max
                    )
                    echo "✅ Qualys scan complete. Vulns summary in console."
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'qualys-report.*', allowEmptyArchive: true
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


