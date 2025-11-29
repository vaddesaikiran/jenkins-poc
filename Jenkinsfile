pipeline {
    agent any

    environment {
        PYTHON_PATH = '/usr/local/bin/python3'
        PIP_PATH = '/usr/local/bin/pip3'
        GOOGLE_CREDENTIALS = credentials('gcp-service-account')
        GCP_PROJECT_ID = 'gcppoc-477305'
        GCP_REGION = 'asia-south1'
        GCP_FUNCTION_NAME = 'jenkins-poc-function'
        GCP_ENTRY_POINT = 'multiply_http'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/vaddesaikiran/jenkins-poc.git', branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                python3 -m venv venv
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                """
            }
        }


        stage('Deploy to GCP Cloud Functions') {
            steps {
                withCredentials([file(credentialsId: 'gcp-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Deploying Python Cloud Function to GCP...'

                        // Ensure gcloud CLI is in PATH
                        sh """
                            export PATH=\$PATH:/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin
                            gcloud auth activate-service-account --key-file=\$GOOGLE_APPLICATION_CREDENTIALS --project=$GCP_PROJECT_ID
                        """

                        // Deploy Cloud Function
                        sh """
                            export PATH=\$PATH:/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin
                            gcloud functions deploy $GCP_FUNCTION_NAME \\
                                --runtime=python311 \\
                                --entry-point=$GCP_ENTRY_POINT \\
                                --trigger-http \\
                                --allow-unauthenticated \\
                                --region=$GCP_REGION \\
                                --source=. \\
                                --project=$GCP_PROJECT_ID \\
                                --quiet
                        """

                        echo "✅ Cloud Function '$GCP_FUNCTION_NAME' deployed successfully to GCP!"
                    }
                }
            }
        }
    }
}
