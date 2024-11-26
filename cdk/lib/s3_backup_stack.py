from aws_cdk import core, aws_s3 as s3, aws_iam as iam, aws_kms as kms

class S3BackupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Optional: KMS Key for Encryption
        encryption_key = kms.Key(
            self, 
            "S3BackupEncryptionKey",
            description="KMS key for encrypting S3 backups",
            enable_key_rotation=True
        )

        # S3 Backup Bucket
        self.backup_bucket = s3.Bucket(
            self,
            "MetabaseBackupBucket",
            versioned=True,
            removal_policy=core.RemovalPolicy.RETAIN,  # Retain backups even if stack is deleted
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    expiration=core.Duration.days(90),  # Automatically delete objects older than 90 days
                )
            ],
            encryption=s3.BucketEncryption.KMS,  # Enable encryption
            encryption_key=encryption_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # Prevent public access
        )

        # IAM Role for EC2 Access
        self.backup_bucket_access_role = iam.Role(
            self,
            "S3BackupAccessRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="Role for accessing the backup bucket from EC2",
        )

        # Grant EC2 Role Access to the Bucket
        self.backup_bucket.grant_read_write(self.backup_bucket_access_role)

        # Outputs for Easy Reference
        core.CfnOutput(self, "BackupBucketName", value=self.backup_bucket.bucket_name)
        core.CfnOutput(self, "BackupBucketArn", value=self.backup_bucket.bucket_arn)
