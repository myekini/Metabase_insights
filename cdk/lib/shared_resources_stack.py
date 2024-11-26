from aws_cdk import aws_ec2 as ec2, aws_s3 as s3, core

class SharedResourcesStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # VPC for shared resources
        self.vpc = ec2.Vpc(
            self, "SharedVpc",
            max_azs=2,  # Default is all AZs in the region
            cidr="10.0.0.0/16",
            nat_gateways=1
        )

        # S3 bucket for shared storage
        self.shared_bucket = s3.Bucket(
            self, "SharedBucket",
            versioned=True,
            removal_policy=core.RemovalPolicy.RETAIN
        )

        # Security group for EC2 instances
        self.shared_sg = ec2.SecurityGroup(
            self, "SharedSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
            description="Shared security group for staging and production"
        )
        self.shared_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access")
