from aws_cdk import aws_ec2 as ec2, aws_s3 as s3, aws_iam as iam, core

class StagingStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, shared_stack: core.Stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Use shared VPC and security group
        vpc = shared_stack.vpc
        shared_sg = shared_stack.shared_sg

        # S3 bucket for staging environment
        self.staging_bucket = s3.Bucket(
            self, "StagingBucket",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Add IAM permissions to existing EC2 instance
        iam_role = iam.Role.from_role_arn(
            self,
            "ExistingEC2Role",
            role_arn="arn:aws:iam::<account-id>:role/<existing-ec2-role>"
        )
        iam_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:*"],
                resources=[self.staging_bucket.bucket_arn + "/*"]
            )
        )
