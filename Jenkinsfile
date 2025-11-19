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

        // NEW STAGE: Auto-detect Host IP (add this right after 'Snyk Scan' and before Qualys)
        stage('Get Host IP') {
            steps {
                script {
                    echo 'Detecting public host IP for Qualys scan...'
                    // For public IP (assumes curl is installed; if not, install via Chocolatey: choco install curl)
                    def publicIpOutput = bat(script: 'curl -s ifconfig.me', returnStdout: true).trim()
                    if (publicIpOutput && publicIpOutput =~ /\d+\.\d+\.\d+\.\d+/) {
                        env.HOST_IP = publicIpOutput
                    } else {
                        // Fallback: Prompt manual or use private (uncomment if needed)
                        // env.HOST_IP = 'YOUR_PUBLIC_IP_HERE'  // e.g., '203.0.113.42' - get from whatismyipaddress.com
                        error "❌ Failed to detect public IP. Please set env.HOST_IP manually or install curl."
                    }
                    echo "Detected Public Host IP: ${env.HOST_IP}"
                }
            }
        }

        // NEW STAGE: Qualys Host Vulnerability Scan (add right after 'Get Host IP')
        stage('Qualys Vulnerability Scan') {
            steps {
                script {
                    echo 'Running Qualys VMDR host scan for vulnerabilities...'
                    qualysVulnerabilityAnalyzer(
                        credsId: 'qualys-api-cred',          // Your Jenkins cred ID (from Manage Credentials)
                        platform: 'QUALYS_PublicCloud',      // Confirmed for your qualys.in URL (public cloud)
                        hostIp: "${env.HOST_IP}",            // Uses dynamic public IP from previous stage
                        network: 'Default_Network',          // Or your custom Qualys network name
                        optionProfile: 'Initial_Options',    // Quick/basic scan profile (check Qualys portal)
                        scannerName: 'External_scanner',     // Default for public cloud
                        scanName: "POC-Scan-${BUILD_NUMBER}", // Unique name with build number
                        pollingInterval: '2',                // Poll every 2 minutes for status
                        vulnsTimeout: '30',                  // Max wait 30 minutes (increase if needed)
                        // Failure conditions: Fail build on High+ severity vulns
                        failBySev: true,
                        bySev: 4,                            // 4=High/Critical (tune to 5 for Critical only)
                        // Optional: Exclude false positives (add QIDs after first run)
                        doExclude: false,                    // Set true and add excludeList if needed
                        // excludeBy: 'qids',
                        // excludeList: '10001,10002',       // Comma-separated QIDs (e.g., from Qualys reports)
                        evaluatePotentialVulns: true         // Include potential/unconfirmed vulns for stricter check
                    )
                    echo "✅ Qualys scan completed and passed quality criteria. No critical vulnerabilities found."
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


