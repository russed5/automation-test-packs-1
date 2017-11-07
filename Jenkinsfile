// Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
properties(getBuildProperties())

pipeline {
    agent {
        node {
            label 'maven-builder'
        }
    }
    options { 
        skipDefaultCheckout()
        timestamps()
    }
    tools {
        maven 'linux-maven-3.3.9'
        jdk 'linux-jdk1.8.0_102'
    }
    stages {
        stage('Checkout') {
            steps {
                doCheckout()
            }
        }
        /*stage('Run pytest Scanner') {
            steps {
                runPyTestScanner()
            }
        }*/
    }
    post {
        always {
            cleanWorkspace()   
        }
        success {
            successEmail()
        }
        failure {
            failureEmail()
        }
    }
}
