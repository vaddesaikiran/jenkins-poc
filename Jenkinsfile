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
                        docker run --rm -v "%cd%:/repo" zricethezav/gitleaks:latest sh -c "gitleaks detect --source=/repo --report-path=/tmp/gitleaks-report.json --exit-code 1 && cp /tmp/gitleaks-report.json /repo/gitleaks-report.json"
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'gitleaks-report.json', allowEmptyArchive: true
                }
                failure {
                    echo 'GitLeaks found potential secrets. Please review gitleaks-report.json.'
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
