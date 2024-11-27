from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    core
)

class BackupTaskStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create ECS Cluster
        cluster = ecs.Cluster(self, "BackupCluster")

        # Define IAM Role for Backup Task
        task_execution_role = iam.Role(
            self,
            "BackupTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )

        # Create Fargate Task Definition for Backups
        task_definition = ecs.FargateTaskDefinition(
            self,
            "BackupTaskDef",
            cpu=256,
            memory_limit_mib=512,
            execution_role=task_execution_role
        )

        # Add Backup Container
        task_definition.add_container(
            "BackupContainer",
            image=ecs.ContainerImage.from_asset("./docker/backup"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="BackupLogs")
        )

        # Schedule ECS Task
        rule = events.Rule(
            self,
            "DailyBackupRule",
            schedule=events.Schedule.cron(hour="2", minute="0"),  # Daily at 2 AM
        )
        rule.add_target(
            targets.EcsTask(
                cluster=cluster,
                task_definition=task_definition,
                subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE)
            )
        )
