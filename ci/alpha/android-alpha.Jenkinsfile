pipeline {
    agent any
    stages {
        stage('Resolve SHA') {
            when { expression { !env.COMMIT_SHA } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-pat',
                        usernameVariable: 'GH_USER', passwordVariable: 'GH_PAT')]) {
                    script {
                        def remote = "https://${GH_PAT}@github.com/gosuwachu/mobile-app.git"
                        env.COMMIT_SHA = sh(
                            script: "git ls-remote ${remote} refs/heads/${env.BRANCH_NAME} | cut -f1",
                            returnStdout: true
                        ).trim()
                        echo "Resolved COMMIT_SHA from branch ${env.BRANCH_NAME}: ${env.COMMIT_SHA}"
                    }
                }
            }
        }
        stage('Android Alpha Build') {
            steps {
                script {
                    currentBuild.displayName = sh(script: './ci-cli build-name', returnStdout: true).trim()
                }
                withCredentials([usernamePassword(credentialsId: 'github-app',
                        usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
                    script {
                        env.CONTEXT_JSON = sh(
                            script: """./ci-cli android alpha-build \
                                --commit-sha ${env.COMMIT_SHA} \
                                --build-url ${env.BUILD_URL} \
                                --no-status""",
                            returnStdout: true
                        ).trim()
                    }
                }
            }
        }
        stage('Trigger Android Alpha Deploy') {
            steps {
                build job: 'mobile-app-support/omnibus',
                      parameters: [
                          string(name: 'BRANCH_NAME', value: env.BRANCH_NAME),
                          string(name: 'COMMIT_SHA', value: env.COMMIT_SHA),
                          string(name: 'CHANGE_ID', value: ''),
                          string(name: 'JENKINSFILE', value: 'ci/alpha/android-alpha-deploy.Jenkinsfile'),
                          string(name: 'CI_BRANCH', value: env.CI_BRANCH ?: 'main'),
                          string(name: 'CONTEXT_JSON', value: env.CONTEXT_JSON)
                      ],
                      wait: true
            }
        }
    }
}
