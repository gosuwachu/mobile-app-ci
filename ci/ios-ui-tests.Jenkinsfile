pipeline {
    agent any
    stages {
        stage('Checkout App') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: env.BRANCH_NAME ?: 'main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/gosuwachu/jenkinsfiles-test-app.git',
                        credentialsId: 'github-pat'
                    ]]
                ])
            }
        }
        stage('iOS UI Tests') {
            steps {
                echo 'Running iOS UI tests...'
            }
        }
    }
}
