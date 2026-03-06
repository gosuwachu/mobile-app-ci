pipeline {
    agent any
    stages {
        stage('Android Linter') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    sh """./ci-cli android linter \
                        --commit-sha ${env.COMMIT_SHA} \
                        --gh-token \$GH_TOKEN \
                        --build-url ${env.BUILD_URL}"""
                }
            }
        }
    }
}
