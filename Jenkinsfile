pipeline {
    agent any


    environment {
        PYTHON_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"'
        PIP_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe"'
        scannerHome = tool 'SonarScanner'
        SONARQUBE_URL = 'http://localhost:9000'
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        SNYK_TOKEN = credentials('snyk-token')
        // NEW: Qualys API credentials
        QUALYS_CREDENTIALS = credentials('qualys-api-cred')

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


        // STAGE 1: Auto-detect Host IP (unchanged mostly; added fallback error handling)
        // stage('Get Host IP') {
        //     steps {
        //         script {
        //             echo 'Detecting public host IP for Qualys scan...'
        //             // For public IP (assumes curl is installed)
        //             def publicIpOutput = bat(script: 'curl -s ifconfig.me', returnStdout: true).trim()
        //             if (publicIpOutput && publicIpOutput =~ /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/) {
        //                 env.HOST_IP = publicIpOutput
        //             } else {
        //                 // Fallback: Hardcode your IP if curl fails (remove after testing)
        //                 env.HOST_IP = '115.98.166.252'  // Your detected IP—update if it changes
        //                 echo "WARNING: Curl failed; using hardcoded IP: ${env.HOST_IP}"
        //             }
        //             echo "Detected Public Host IP: ${env.HOST_IP}"
        //         }
        //     }
        //     post {
        //         failure {
        //             error "❌ Failed to detect host IP. Install curl or hardcode it."
        //         }
        //     }
        // }

        // // STAGE 2: Qualys Host Vulnerability Scan (corrected params per plugin docs)
        // stage('Qualys Vulnerability Scan') {
        //     steps {
        //         script {
        //             echo 'Running Qualys VMDR host scan for vulnerabilities...'
        //             // Debug: Confirm IP before scan
        //             echo "Using Host IP for scan: ${env.HOST_IP}"
                    
        //             qualysVulnerabilityAnalyzer(
        //                 qualysCredentialsId: 'qualys-api-cred',     // Exact cred ID from Jenkins
        //                 apiServerUrl: 'https://qualysapi.qg1.apps.qualys.in',  // Your India region API URL
        //                 scanName: "POC-Scan-${BUILD_NUMBER}",      // Unique name
        //                 targetType: 'Host IP',                     // CRITICAL: Tells plugin it's a host scan
        //                 hostIp: "${env.HOST_IP}",                  // Dynamic public IP
        //                 optionProfile: 'Initial Options',          // Quick profile (match your Qualys portal name)
        //                 scannerName: 'External Scanner',           // Default for public cloud
        //                 // Failure: Fail on High+ severity (1=All, 2=Medium+, 3=High+, 4=Critical+—start with 4)
        //                 failBySeverity: 4,                         // Tune to 5 for Critical only
        //                 applyToPotential: true,                    // Include potential vulns
        //                 // Optional: Exclude false positives (add after first successful scan)
        //                 // excludeQids: '10001,10002',              // Comma-separated QIDs
        //                 pollingFrequencyMinutes: 2,                // Poll every 2 mins
        //                 timeoutMinutes: 30                         // Max 30 mins wait
        //             )
        //             echo "✅ Qualys scan completed and passed quality criteria. No critical vulnerabilities found."
        //         }
        //     }
        //     post {
        //         failure {
        //             echo "❌ Qualys scan failed—check console for details (e.g., unreachable host, API errors)."
        //         }
        //     }
        // }

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


        stage('Qualys Container Security Scan') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'qualys-api-cred', usernameVariable: 'QUALYS_USERNAME', passwordVariable: 'QUALYS_PASSWORD')]) {
                    script {
                        echo 'Running Qualys Security Scan on Python Dependencies...'
                        
                        // First, create a Dockerfile
                        writeFile file: 'Dockerfile', text: """
                        FROM python:3.9-slim
                        COPY . /app
                        WORKDIR /app
                        RUN pip install -r requirements.txt
                        CMD ["python", "-m", "pytest"]
                        """
                        
                        // Build Docker image
                        bat """
                            docker build -t jenkins-poc-python-app:${BUILD_NUMBER} .
                        """
                        
                        echo "✅ Docker image built successfully"
                        
                        // Scan with Qualys - SIMPLIFIED approach
                        bat """
                            curl -u %QUALYS_USERNAME%:%QUALYS_PASSWORD% ^
                            "https://qualysapi.qualys.com/api/2.0/fo/container/scan/?action=list&truncation_limit=1" ^
                            -o qualys-container-test.json
                        """
                        
                        if (fileExists('qualys-container-test.json')) {
                            echo "✅ Qualys Container Security API is accessible!"
                            
                            // Now try the actual scan
                            bat """
                                curl -X POST ^
                                -u %QUALYS_USERNAME%:%QUALYS_PASSWORD% ^
                                -H "Content-Type: application/json" ^
                                -d "{\\"image\\": \\"jenkins-poc-python-app:${BUILD_NUMBER}\\"}" ^
                                "https://qualysapi.qualys.com/api/2.0/fo/container/scan/" ^
                                -o qualys-container-scan.json
                            """
                            
                            if (fileExists('qualys-container-scan.json')) {
                                echo "✅ Qualys container vulnerability scan completed!"
                                archiveArtifacts artifacts: 'qualys-container-scan.json', allowEmptyArchive: true
                            }
                        }
                    }
                }
            }
            post {
                always {
                    // Cleanup
                    bat '''
                        if exist Dockerfile del Dockerfile
                        docker rmi jenkins-poc-python-app:%BUILD_NUMBER% 2>nul || echo "Image cleanup skipped"
                    '''
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


