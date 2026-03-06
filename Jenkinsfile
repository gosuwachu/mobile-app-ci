pipeline {
    agent any
    stages {
        stage('Lint & Test') {
            parallel {
                stage('Python') {
                    steps {
                        sh './run-tests -v'
                    }
                }
                stage('Jenkinsfiles') {
                    steps {
                        sh './lint-jenkinsfiles'
                    }
                }
            }
        }
    }
}
