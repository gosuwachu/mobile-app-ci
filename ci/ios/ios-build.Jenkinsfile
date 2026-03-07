pipeline {
    agent any
    stages {
        stage('iOS Build') {
            steps {
                script {
                    currentBuild.displayName = sh(script: './ci-cli build-name', returnStdout: true).trim()
                }
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    script {
                        env.CONTEXT_JSON = sh(
                            script: """./ci-cli ios build \
                                --commit-sha ${env.COMMIT_SHA} \
                                --build-url ${env.BUILD_URL}""",
                            returnStdout: true
                        ).trim()
                    }
                }
            }
        }
        stage('Trigger iOS Deploy') {
            steps {
                build job: 'pipeline/omnibus',
                      parameters: [
                          string(name: 'BRANCH_NAME', value: env.BRANCH_NAME),
                          string(name: 'COMMIT_SHA', value: env.COMMIT_SHA),
                          string(name: 'CHANGE_ID', value: env.CHANGE_ID ?: ''),
                          string(name: 'JENKINSFILE', value: 'ci/ios/ios-deploy.Jenkinsfile'),
                          string(name: 'CI_BRANCH', value: env.CI_BRANCH ?: 'main'),
                          string(name: 'CONTEXT_JSON', value: env.CONTEXT_JSON)
                      ],
                      wait: true
            }
        }
    }
}
