pipeline {
    agent any

    triggers {
        // This makes Jenkins trigger only when changes are pushed to "main"
        pollSCM('H/2 * * * *') 
        // (or use webhook → recommended)
    }

    stages {
        stage('Run only on main after PR merge') {
            when {
                branch "main"
            }
            steps {
                echo "Changes detected on main branch — PR merged. Running pipeline..."
            }
        }

        stage('Checkout Code') {
            when {
                branch "main"
            }
            steps {
                git url: 'https://github.com/vaddesaikiran/jenkins-poc.git', branch: 'main'
            }
        }

        stage('Install Dependencies') {
            when {
                branch "main"
            }
            steps {
                bat '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe" install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            when {
                branch "main"
            }
            steps {
                bat '"C:\\Users\\saiki\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pytest -v'
            }
        }
    }
}
