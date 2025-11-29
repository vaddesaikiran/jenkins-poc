pipeline {
    agent any

    environment {
        PYTHON_PATH = '/usr/local/bin/python3'
        PIP_PATH = '/usr/local/bin/pip3'
        GOOGLE_CREDENTIALS = credentials('gcp-service-account')
        GCP_PROJECT_ID = 'gcppoc-477305'
        GCP_REGION = 'asia-south1'
        GCP_FUNCTION_NAME = 'jenkins-poc-function-two'
        GCP_ENTRY_POINT = 'multiply_http'
        PATH = "/usr/local/share/google-cloud-sdk/bin:${env.PATH}"
        CLOUDSDK_PYTHON = '/usr/local/bin/python3'
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
                ./venv/bin/pip install --upgrade pip
                ./venv/bin/pip install -r requirements.txt
                """
            }
        }

        stage('Prepare Deployment Package') {
            steps {
                sh """
                # Create a temporary directory for deployment
                DEPLOY_DIR=deploy_temp
                rm -rf \$DEPLOY_DIR
                mkdir \$DEPLOY_DIR

                # Copy only main.py and requirements.txt
                cp main.py requirements.txt \$DEPLOY_DIR/
                """
            }
        }

        stage('Deploy to GCP Cloud Functions') {
            steps {
                withCredentials([file(credentialsId: 'gcp-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                        export CLOUDSDK_PYTHON=$PYTHON_PATH
                        export PATH=/usr/local/share/google-cloud-sdk/bin:\$PATH

                        # Authenticate with service account
                        gcloud auth activate-service-account --key-file=\$GOOGLE_APPLICATION_CREDENTIALS --project=$GCP_PROJECT_ID

                        # Deploy only the files inside the temporary directory
                        gcloud functions deploy $GCP_FUNCTION_NAME \\
                            --runtime=python311 \\
                            --entry-point=$GCP_ENTRY_POINT \\
                            --trigger-http \\
                            --allow-unauthenticated \\
                            --region=$GCP_REGION \\
                            --source=deploy_temp \\
                            --project=$GCP_PROJECT_ID \\
                            --quiet
                    """
                }
            }
        }
    }
}
