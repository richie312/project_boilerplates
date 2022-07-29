pipeline
{
    agent any
    environment
    {
        VERSION = 'latest'
        PROJECT = 'inv_analysis'
        IMAGE = 'inv_analysis:latest'
        ECRURL = '733112759328.dkr.ecr.us-east-1.amazonaws.com/inv_analysis:latest'
        AWSURL = 'http://733112759328.dkr.ecr.us-east-1.amazonaws.com'
        REPO_URL = 'https://innersource.accenture.com/projects/ATCIMEXR/repos/inventoryanalysispandas_v1.0/'
        ECRCRED = 'ecr:us-east-1:5fa0fae9-2ab8-448d-a98e-c7822f051be3'
    }
    stages
    {
        stage("Checkout"){
            steps{
            checkout([$class: 'GitSCM', branches: [[name: 'Develop']], extensions: [], userRemoteConfigs: [[credentialsId: 'f1920e3b-38c3-48a0-a30d-ee3c4f148aa4', url: 'https://innersource.accenture.com/scm/atcimexr/inventoryanalysispandas_v1.0.git']]])
             }
        }
        stage('Build preparations')
        {
             when {
                  expression { return params.branch == "Develop" && params.state == "MERGED" }
              }
            steps
            {
                script
                {
                    // calculate GIT lastest commit short-hash
                    gitCommitHash = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    shortCommitHash = gitCommitHash.take(7)
                    // calculate a sample version tag
                    VERSION = shortCommitHash
                    // set the build display name
                    currentBuild.displayName = "#${BUILD_ID}-${VERSION}"
                    IMAGE = "$PROJECT:$VERSION"
                }
            }
        }


        stage('Docker build')
        {
             when {
                  expression { return params.branch == "Develop" && params.state == "MERGED" }
              }
            steps
            {
                script
                {
                    // Build the docker image using a Dockerfile
                    dockerImage = docker.build env.PROJECT
                }
            }
        }

        stage('Docker Image Tag')
        {
            when {
                  expression { return params.branch == "Develop" && params.state == "MERGED" }
              }
            steps
            {
                script
                {
                    // Tag with the appropriate image name.
                    sh "docker image tag $env.PROJECT $env.ECRURL"

                }
            }
        }

        stage('Docker Push')
        {
            when {
                  expression { return params.branch == "Develop" && params.state == "MERGED" }
              }
            steps
            {
                script{
                    docker.withRegistry("$env.AWSURL","$env.ECRCRED"){

                        docker.image("$env.ECRURL").push()

                    }


                }

            }
        }

    }

    post
    {
        always
        {
            // make sure that the Docker image is removed
            sh "docker rmi $env.Project | true"
        }
    }
}