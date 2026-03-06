pipeline {
    agent any
    stages {
        stage('iOS Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    sh """./ci-cli ios deploy \
                        --commit-sha ${env.COMMIT_SHA} \
                        --gh-token \$GH_TOKEN \
                        --build-url ${env.BUILD_URL}"""
                }
            }
        }
    }
}
