pipeline {
    agent any


    environment {
        PYTHON_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"'
        PIP_PATH = '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe"'
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

        stage('Install Dependencies') {
            steps {
                bat "${PIP_PATH} install -r requirements.txt"
            }
        }



        // stage('Install Dependencies') {
        //     steps {
        //         bat '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe" install -r requirements.txt'
        //     }
        // }

        // stage('Run Tests') {
        //     steps {
        //         bat '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pytest -v'
        //     }
        // }

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

    }
}
