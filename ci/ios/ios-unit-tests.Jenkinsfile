pipeline {
    agent any
    stages {
        stage('iOS Unit Tests') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    sh """./ci-cli ios unit-tests \
                        --commit-sha ${env.COMMIT_SHA} \
                        --gh-token \$GH_TOKEN \
                        --build-url ${env.BUILD_URL}"""
                }
            }
        }
    }
}
