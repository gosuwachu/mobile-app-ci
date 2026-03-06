pipeline {
    agent any
    stages {
        stage('Checkout App') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: env.BRANCH_NAME]],
                    userRemoteConfigs: [[
                        url: 'https://github.com/gosuwachu/jenkinsfiles-test-app.git',
                        credentialsId: 'github-pat'
                    ]]
                ])
            }
        }
        stage('iOS Unit Tests') {
            steps {
                echo 'Running iOS unit tests...'
            }
        }
    }
}
