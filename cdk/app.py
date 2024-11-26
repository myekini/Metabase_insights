#!/usr/bin/env python3

from aws_cdk import core
from lib.staging_stack import StagingStack
from lib.production_stack import ProductionStack
from lib.pipeline_stack import PipelineStack
from lib.s3_backup_stack import S3BackupStack

app = core.App()

# Shared Resources (Optional)
s3_backup_stack = S3BackupStack(app, "S3BackupStack")

# Staging Stack
staging_stack = StagingStack(
    app,
    "StagingStack",
    backup_bucket=s3_backup_stack.backup_bucket
)

# Production Stack
production_stack = ProductionStack(
    app,
    "ProductionStack",
    backup_bucket=s3_backup_stack.backup_bucket
)

# CI/CD Pipeline Stack
PipelineStack(app, "PipelineStack")

# Synthesize the app
app.synth()
