pipeline {
    agent any
    stages {
        stage('Android Deploy') {
            steps {
                script {
                    currentBuild.displayName = sh(script: './ci-cli build-name', returnStdout: true).trim()
                }
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    sh """./ci-cli android deploy \
                        --commit-sha ${env.COMMIT_SHA} \
                        --build-url ${env.BUILD_URL} \
                        --context-json '${env.CONTEXT_JSON}'"""
                }
            }
        }
    }
}
