from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_logs as logs,
    core
)

class StagingStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)


        # Create ECS Cluster
        cluster = ecs.Cluster(self, "Staging_Cluster")

        # Define IAM Role for ECS Task Execution
        task_execution_role = iam.Role(
            self,
            "StagingTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        # Create Fargate Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "Staging_Task",
            cpu=256,  # 0.25 vCPU
            memory_limit_mib=512,  # 0.5 GB memory
            execution_role=task_execution_role
        )

        # Add Metabase Container
        container = task_definition.add_container(
            "StagingMetabaseContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                ecs.Repository.from_repository_name(self, "Staging_Repo", "metabase-staging-repo"),
                tag="latest"
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix="Staging_Metabase"),
            environment={
                "MB_DB_TYPE": "postgres",
                "MB_DB_DBNAME": "metabase_staging",
                "MB_DB_PORT": "5432",
                "MB_DB_USER": "staging_user",
                "MB_DB_PASS": "secure_password",
                "MB_DB_HOST": "staging-db.endpoint.amazonaws.com"
            }
        )
        container.add_port_mappings(ecs.PortMapping(container_port=3000))

        # Create ECS Service with Load Balancer
        ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "StagingService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=True
        )
