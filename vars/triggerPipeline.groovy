// Shared library: orchestrates pipeline jobs (multibranch variant)
// Pure orchestrator — child jobs publish their own commit statuses
// No publishChecks here; each child job handles its own GitHub status reporting
// PR diff filtering: only triggers iOS or Android jobs based on changed files

import groovy.transform.Field

@Field GITHUB_OWNER = 'gosuwachu'
@Field GITHUB_REPO = 'jenkinsfiles-test-app'

@Field IOS_CONTEXTS = [
    'ci/ios-build',
    'ci/ios-unit-tests',
    'ci/ios-linter',
    'ci/ios-deploy',
]

@Field ANDROID_CONTEXTS = [
    'ci/android-build',
    'ci/android-unit-tests',
    'ci/android-linter',
    'ci/android-deploy',
]

def checkCollaborator() {
    if (!env.CHANGE_ID) {
        return // not a PR build — allow
    }
    def author = env.CHANGE_AUTHOR
    if (!author) {
        echo 'WARNING: Could not determine PR author — allowing build'
        return
    }
    echo "PR #${env.CHANGE_ID} by ${author} — checking collaborator status"
    try {
        def statusCode = 0
        withCredentials([usernamePassword(credentialsId: 'github-app',
                usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
            statusCode = sh(
                script: """curl -s -o /dev/null -w '%{http_code}' \
                    -H "Authorization: token \$GH_TOKEN" \
                    -H "Accept: application/vnd.github+json" \
                    "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/collaborators/${author}" """,
                returnStdout: true
            ).trim().toInteger()
        }
        if (statusCode == 204) {
            echo "${author} is a collaborator — CI allowed"
            return
        }
        echo "${author} is NOT a collaborator — checking for approved reviews"
        def approved = false
        withCredentials([usernamePassword(credentialsId: 'github-app',
                usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
            def reviews = sh(
                script: """curl -s \
                    -H "Authorization: token \$GH_TOKEN" \
                    -H "Accept: application/vnd.github+json" \
                    "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/pulls/${env.CHANGE_ID}/reviews" """,
                returnStdout: true
            ).trim()
            approved = reviews.contains('"state":"APPROVED"') || reviews.contains('"state": "APPROVED"')
        }
        if (approved) {
            echo "PR has an approved review — CI allowed for non-collaborator ${author}"
        } else {
            echo "PR has no approved reviews — aborting CI for non-collaborator ${author}"
            currentBuild.result = 'NOT_BUILT'
            error("PR from non-collaborator ${author} requires an approved review before CI runs")
        }
    } catch (e) {
        if (currentBuild.result == 'NOT_BUILT') {
            throw e
        }
        echo "WARNING: Failed to check collaborator status: ${e.message} — allowing build"
    }
}

def detectPlatforms() {
    if (!env.CHANGE_TARGET) {
        echo 'Not a PR build — running all platforms'
        return [ios: true, android: true]
    }

    try {
        def ciCli = sh(script: "ls ${env.WORKSPACE}@libs/*/ci-cli", returnStdout: true).trim()
        def output = ''
        withCredentials([usernamePassword(credentialsId: 'github-app',
                usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
            output = sh(
                script: "${ciCli} detect-changes --target-branch ${env.CHANGE_TARGET} --gh-token \$GH_TOKEN",
                returnStdout: true
            ).trim()
        }
        // readJSON parses the last line (JSON); preceding lines are diagnostic output
        def lastLine = output.split('\n').last()
        def platforms = readJSON text: lastLine
        echo "Platform detection: iOS=${platforms.ios}, Android=${platforms.android}"
        return platforms
    } catch (e) {
        echo "WARNING: Failed to detect changes: ${e.message}. Running all platforms."
        return [ios: true, android: true]
    }
}

def publishSkippedStatuses(List<String> contexts, String platform) {
    def sha = env.GIT_COMMIT ?: sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
    withCredentials([usernamePassword(credentialsId: 'github-app',
            usernameVariable: 'GH_APP', passwordVariable: 'GH_TOKEN')]) {
        contexts.each { context ->
            echo "Publishing skipped status for: ${context}"
            sh """curl -s -X POST \
                -H "Authorization: token \$GH_TOKEN" \
                -H "Accept: application/vnd.github+json" \
                "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/statuses/${sha}" \
                -d '{"state":"success","context":"${context}","description":"Skipped — no ${platform} changes","target_url":"${env.BUILD_URL}"}'"""
        }
    }
}

def call() {
    pipeline {
        agent any

        parameters {
            string(name: 'CI_BRANCH', defaultValue: 'main', description: 'CI repo branch to checkout Jenkinsfiles from')
        }

        environment {
            BRANCH_TO_BUILD = "${env.CHANGE_BRANCH ?: env.BRANCH_NAME}"
        }

        stages {
            stage('Start') {
                steps {
                    script {
                        echo "Starting Mobile CI/CD Pipeline on branch: ${env.BRANCH_TO_BUILD}"

                        checkCollaborator()

                        def platforms = detectPlatforms()
                        env.RUN_IOS = platforms.ios.toString()
                        env.RUN_ANDROID = platforms.android.toString()

                        echo "Will run — iOS: ${env.RUN_IOS}, Android: ${env.RUN_ANDROID}"

                        if (env.RUN_IOS != 'true') {
                            publishSkippedStatuses(IOS_CONTEXTS, 'iOS')
                        }
                        if (env.RUN_ANDROID != 'true') {
                            publishSkippedStatuses(ANDROID_CONTEXTS, 'Android')
                        }
                    }
                }
            }

            stage('Build & Quality') {
                parallel {
                    stage('iOS Build') {
                        when { expression { env.RUN_IOS == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/ios/ios-build.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                    stage('Android Build') {
                        when { expression { env.RUN_ANDROID == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/android/android-build.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                    stage('iOS Tests') {
                        when { expression { env.RUN_IOS == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/ios/ios-unit-tests.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                    stage('Android Tests') {
                        when { expression { env.RUN_ANDROID == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/android/android-unit-tests.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                    stage('iOS Lint') {
                        when { expression { env.RUN_IOS == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/ios/ios-linter.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                    stage('Android Lint') {
                        when { expression { env.RUN_ANDROID == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/android/android-linter.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                }
            }

            stage('Deploy') {
                parallel {
                    stage('iOS Deploy') {
                        when { expression { env.RUN_IOS == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/ios/ios-deploy.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                    stage('Android Deploy') {
                        when { expression { env.RUN_ANDROID == 'true' } }
                        steps {
                            build job: 'pipeline/omnibus',
                                  parameters: [
                                      string(name: 'BRANCH_NAME', value: env.BRANCH_TO_BUILD),
                                      string(name: 'COMMIT_SHA', value: env.GIT_COMMIT),
                                      string(name: 'PR_NUMBER', value: env.CHANGE_ID ?: ''),
                                      string(name: 'JENKINSFILE', value: 'ci/android/android-deploy.Jenkinsfile'),
                                      string(name: 'CI_BRANCH', value: params.CI_BRANCH)
                                  ],
                                  wait: true
                        }
                    }
                }
            }
        }
    }
}
