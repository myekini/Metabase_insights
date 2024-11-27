from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_logs as logs,
    core
)
class ProductionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "ProductionVpc", max_azs=2)

        # Create ECS Cluster
        cluster = ecs.Cluster(self, "ProductionCluster", vpc=vpc)

        # Define IAM Role for ECS Task Execution
        task_execution_role = iam.Role(
            self,
            "ProductionTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        # Create Fargate Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "ProductionTaskDef",
            cpu=512,  # 0.5 vCPU
            memory_limit_mib=1024,  # 1 GB memory
            execution_role=task_execution_role
        )

        # Add Metabase Container
        container = task_definition.add_container(
            "ProductionMetabaseContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                ecs.Repository.from_repository_name(self, "ProductionEcrRepo", "metabase-production-repo"),
                tag="latest"
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix="ProductionMetabase"),
            environment={
                "MB_DB_TYPE": "postgres",
                "MB_DB_DBNAME": "metabase_production",
                "MB_DB_PORT": "5432",
                "MB_DB_USER": "production_user",
                "MB_DB_PASS": "secure_password",
                "MB_DB_HOST": "production-db.endpoint.amazonaws.com"
            }
        )
        container.add_port_mappings(ecs.PortMapping(container_port=3000))

        # Create ECS Service with Load Balancer
        ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ProductionService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=False  # Private LB for production
        )
