pipeline {
    agent any

    environment {
        GCP_PROJECT_ID    = 'gcppoc-477305'
        GCP_REGION        = 'asia-south1'
        GCP_FUNCTION_NAME = 'jenkins-poc-function-two'
        GCP_ENTRY_POINT   = 'multiply_http'
        TARGET_SA         = 'wif-jenkins-sa@gcppoc-477305.iam.gserviceaccount.com'
        JENKINS_URL       = 'https://fransisca-unsummable-subspirally.ngrok-free.dev'
        CRED_ID           = 'jenkins-oidc-local'   // ← your OIDC credential ID
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
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                pip install "pyjwt[crypto]"   # needed for JWT signing
                """
            }
        }

        stage('Prepare Deployment Package') {
            steps {
                sh """
                DEPLOY_DIR=deploy_temp
                rm -rf \$DEPLOY_DIR
                mkdir \$DEPLOY_DIR
                cp main.py requirements.txt \$DEPLOY_DIR/
                """
            }
        }

        stage('Keyless Deploy to GCP Cloud Functions') {
            steps {
                sh '''
                set -e

                # Generate persistent RSA key (only once)
                [ -f private_key.pem ] || openssl genrsa -out private_key.pem 2048

                # Create and sign the JWT (this also populates the public JWKS endpoint)
                JWT=$(python3 - <<PY
import jwt, time
payload = {
  "iss": "${JENKINS_URL}/oidc/credential/${CRED_ID}",
  "aud": "https://iam.googleapis.com/",
  "sub": "${JENKINS_URL}/job/${JOB_NAME}/${BUILD_NUMBER}",
  "iat": int(time.time()),
  "exp": int(time.time()) + 1800
}
print(jwt.encode(payload, open("private_key.pem").read(), algorithm="RS256", headers={"kid": "${CRED_ID}"}))
PY
                )

                # Exchange JWT → short-lived GCP access token
                TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
                  -d '{"jwt":"'"$JWT"'"}' \
                  "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${TARGET_SA}:generateAccessToken" \
                  | jq -r .accessToken)

                # Use the token for gcloud
                gcloud config set auth/access_token "$TOKEN" --quiet

                # Deploy exactly like you did before
                gcloud functions deploy ${GCP_FUNCTION_NAME} \
                    --runtime=python311 \
                    --entry-point=${GCP_ENTRY_POINT} \
                    --trigger-http \
                    --allow-unauthenticated \
                    --region=${GCP_REGION} \
                    --source=deploy_temp \
                    --project=${GCP_PROJECT_ID} \
                    --service-account=${TARGET_SA} \
                    --quiet

                echo "KEYLESS DEPLOYMENT SUCCESSFUL!"
                echo "Function URL: https://${GCP_REGION}-${GCP_PROJECT_ID}.cloudfunctions.net/${GCP_FUNCTION_NAME}"
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}