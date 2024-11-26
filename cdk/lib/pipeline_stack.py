from aws_cdk import core, aws_codepipeline as codepipeline, aws_codepipeline_actions as actions, aws_codebuild as codebuild

class PipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Source stage
        source_output = codepipeline.Artifact()
        source_action = actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="your_github_user",
            repo="your_repo_name",
            oauth_token=core.SecretValue.secrets_manager("github-token"),
            output=source_output,
            branch="main"
        )

        # Build stage
        build_project = codebuild.PipelineProject(self, "BuildProject")
        build_output = codepipeline.Artifact()
        build_action = actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )

        # Deploy to Staging
        deploy_staging_action = actions.CloudFormationCreateUpdateStackAction(
            action_name="DeployStaging",
            stack_name="StagingStack",
            template_path=build_output.at_path("template.yaml"),
            admin_permissions=True
        )

        # Deploy to Production
        deploy_production_action = actions.CloudFormationCreateUpdateStackAction(
            action_name="DeployProduction",
            stack_name="ProductionStack",
            template_path=build_output.at_path("template.yaml"),
            admin_permissions=True
        )

        # Pipeline
        codepipeline.Pipeline(self, "Pipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(stage_name="Build", actions=[build_action]),
                codepipeline.StageProps(stage_name="DeployStaging", actions=[deploy_staging_action]),
                codepipeline.StageProps(stage_name="DeployProduction", actions=[deploy_production_action]),
            ]
        )
