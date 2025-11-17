pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/vaddesaikiran/jenkins-poc.git', branch: 'main'
            }
        }

        stage('Secret Scan with GitLeaks') {
            steps {
                script {
                    echo 'Running GitLeaks scan for secrets...'
                    bat '''
                        docker pull zricethezav/gitleaks:latest
                        docker run --rm -v "%cd%:/repo" zricethezav/gitleaks:latest detect --source=/repo --report-format=json --report-path=/repo/gitleaks-report.json --exit-code 1 --verbose
                    '''
                    
                    def gitleaksJson = readJSON file: 'gitleaks-report.json'
                    publishHTML([reportDir: '.', reportFiles: 'gitleaks-report.json', reportName: "GitLeaks Report"])

                    if (gitleaksJson.size() > 0) {
                        error "❌ GitLeaks detected secrets. Failing the build."
                    } else {
                        echo "✅ GitLeaks scan passed. No secrets found."
                    }
                    
                    bat 'del gitleaks-report.json'
                }
            }
        }




        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe" install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pytest -v'
            }
        }
    }
}
