pipeline {
    agent any
    stages {
        stage('iOS UI Tests') {
            steps {
                script {
                    currentBuild.displayName = sh(
                        script: './ci-cli build-name --name ios-ui-tests',
                        returnStdout: true,
                    ).trim()
                }
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    sh """./ci-cli ios ui-tests \
                        --pr-number ${env.CHANGE_ID} \
                        --comment-author ${env.COMMENT_AUTHOR} \
                        --build-url ${env.BUILD_URL}"""
                }
            }
        }
    }
}
