pipeline {
    agent any

    environment {
        AWS_REGION      = "ap-south-1"
        AWS_ACCOUNT_ID  = "447407244516"
        ECR_REPO        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/optic-booking"
        IMAGE_TAG       = "build-${BUILD_NUMBER}"

        AWS_CREDS       = credentials('aws-jenkins-user')
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Ezioraz/optic-booking-platform.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t optic-booking:${IMAGE_TAG} -f docker/Dockerfile .
                """
            }
        }

        stage('Login to ECR') {
            steps {
                withEnv([
                    "AWS_ACCESS_KEY_ID=${AWS_CREDS_USR}",
                    "AWS_SECRET_ACCESS_KEY=${AWS_CREDS_PSW}",
                    "AWS_DEFAULT_REGION=${AWS_REGION}"
                ]) {
                    sh """
                    aws ecr get-login-password --region ${AWS_REGION} \
                        | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    """
                }
            }
        }

        stage('Push to ECR') {
            steps {
                sh """
                docker tag optic-booking:${IMAGE_TAG} ${ECR_REPO}:${IMAGE_TAG}
                docker push ${ECR_REPO}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy to EKS') {
            steps {
                withEnv([
                    "AWS_ACCESS_KEY_ID=${AWS_CREDS_USR}",
                    "AWS_SECRET_ACCESS_KEY=${AWS_CREDS_PSW}",
                    "AWS_DEFAULT_REGION=${AWS_REGION}"
                ]) {

                    withCredentials([file(credentialsId: 'eks-kubeconfig', variable: 'KUBECONFIG')]) {

                        sh '''
                        echo "================= DEBUG: PRINTING KUBECONFIG ================="
                        head -n 25 $KUBECONFIG
                        echo "=============================================================="
                        '''

                        sh """
                        export KUBECONFIG=${KUBECONFIG}

                        echo "Updating deployment image..."
                        sed -i "s|image: .*|image: ${ECR_REPO}:${IMAGE_TAG}|" k8s/deployment.yaml

                        echo "Applying manifests..."
                        kubectl apply -f k8s/deployment.yaml --validate=false
                        kubectl apply -f k8s/service.yaml --validate=false

                        echo "Waiting for rollout..."
                        kubectl rollout status deployment/optic-booking-deployment --timeout=120s
                        """
                    }
                }
            }
        }
    }
}
