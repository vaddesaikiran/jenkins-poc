pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/vaddesaikiran/jenkins-poc.git', branch: 'main'
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
