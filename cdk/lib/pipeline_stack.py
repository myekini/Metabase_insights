from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codebuild as codebuild,
    aws_ecr as ecr,
    aws_ecs as ecs,
    core
)


class PipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ECR Repositories (Consolidated)
        metabase_repo = ecr.Repository.from_repository_name(self, "MetabaseRepo", "metabase")
        postgres_repo = ecr.Repository.from_repository_name(self, "PostgresRepo", "postgres")

        # Source Stage: GitHub Repository
        source_output = codepipeline.Artifact()
        source_action = actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="your_github_username",
            repo="your_repo_name",
            branch="main",  # Adjust for staging/production
            oauth_token=core.SecretValue.secrets_manager("github-token"),
            output=source_output
        )

        # Build Stage: Docker Compose Build with CodeBuild
        build_project = codebuild.PipelineProject(
            self,
            "DockerComposeBuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True  # Required for Docker and Docker Compose
            ),
            build_spec=codebuild.BuildSpec.from_object_to_yaml({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "echo Installing Docker Compose...",
                            "curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose",
                            "chmod +x /usr/local/bin/docker-compose"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "echo Logging in to Amazon ECR...",
                            "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com"
                        ]
                    },
                    "build": {
                        "commands": [
                            "echo Building Docker images using docker-compose...",
                            "docker-compose -f docker-compose.yml build",
                            "docker tag metabase-production <account-id>.dkr.ecr.us-east-1.amazonaws.com/metabase:staging-$CODEBUILD_RESOLVED_SOURCE_VERSION",
                            "docker tag postgres-production <account-id>.dkr.ecr.us-east-1.amazonaws.com/postgres:staging-$CODEBUILD_RESOLVED_SOURCE_VERSION"
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "echo Pushing Docker images to Amazon ECR...",
                            "docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/metabase:staging-$CODEBUILD_RESOLVED_SOURCE_VERSION",
                            "docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/postgres:staging-$CODEBUILD_RESOLVED_SOURCE_VERSION",
                            "echo Build and push completed."
                        ]
                    }
                },
                "artifacts": {
                    "files": ["docker-compose.yml"]
                }
            })
        )

        build_output = codepipeline.Artifact()
        build_action = actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )

        # Deploy Stage: ECS Deploy Actions
        staging_service = ecs.FargateService.from_service_arn(
            self,
            "StagingService",
            "arn:aws:ecs:us-east-1:<account-id>:service/metabase-staging-service"
        )
        production_service = ecs.FargateService.from_service_arn(
            self,
            "ProductionService",
            "arn:aws:ecs:us-east-1:<account-id>:service/metabase-production-service"
        )

        deploy_staging_action = actions.EcsDeployAction(
            action_name="DeployToStaging",
            service=staging_service,
            input=build_output
        )

        deploy_production_action = actions.EcsDeployAction(
            action_name="DeployToProduction",
            service=production_service,
            input=build_output
        )

        # CodePipeline
        pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(stage_name="Build", actions=[build_action]),
                codepipeline.StageProps(stage_name="Deploy", actions=[deploy_staging_action, deploy_production_action])
            ]
        )
