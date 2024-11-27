# **Metabase Deployment Project**

## **Overview**
This project automates the deployment and management of Metabase, a powerful open-source analytics platform, using AWS infrastructure, Docker Compose, and CI/CD pipelines. It includes staging and production environments, robust backup strategies, and database schema management.

---

## **Table of Contents**
1. [Architecture Overview](#architecture-overview)
2. [Features](#features)
3. [Setup Guide](#setup-guide)
4. [Usage Guide](#usage-guide)
5. [Scripts Overview](#scripts-overview)
6. [Folder Structure](#folder-structure)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## **Architecture Overview**
### **High-Level Architecture**
- **Infrastructure**:
  - AWS CDK for provisioning S3 buckets, IAM roles, and CI/CD pipelines.
  - Docker Compose for containerized Metabase and PostgreSQL.
- **Environments**:
  - **Staging**: For testing and experimentation.
  - **Production**: For live deployments with higher security and retention policies.
- **CI/CD**:
  - GitHub Actions triggers deployments to staging and production.
- **Backups**:
  - PostgreSQL database and Metabase volumes are backed up to AWS S3.

---

## **Features**
1. **Environment-Specific Configurations**:
   - Separate configurations for staging and production.
2. **Backup System**:
   - Automatic database and volume backups with S3 integration.
3. **Security**:
   - IAM roles with least privilege.
   - Secrets managed using environment variables.
4. **Scalability**:
   - Easily deployable and scalable using Docker Compose and AWS.
5. **Automation**:
   - Scripts for instance setup, starting services, backups, and schema migration.

---

## **Setup Guide**

### **1. Prerequisites**
- AWS account with necessary permissions.
- Domain for accessing Metabase (optional but recommended).
- Tools installed:
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/)
  - [AWS CLI](https://aws.amazon.com/cli/)
  - [Node.js](https://nodejs.org/) (for AWS CDK)

---

### **2. Repository Setup**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/metabase-project.git
   cd metabase-project
   ```

2. Install Python dependencies for AWS CDK:
   ```bash
   python -m pip install -r cdk/requirements.txt
   ```

---

### **3. Environment Configuration**
1. Configure `.env` files:
   - `config/staging/.env.stg`:
     ```plaintext
     MB_DB_DBNAME=metabase_staging
     MB_DB_PORT=5432
     MB_DB_USER=metabase_stg
     MB_DB_PASS=secure_stg_password

     POSTGRES_USER=metabase_stg
     POSTGRES_DB=metabase_staging
     POSTGRES_PASSWORD=secure_stg_password
     ```
   - `config/production/.env.prod`:
     ```plaintext
     MB_DB_DBNAME=metabase_production
     MB_DB_PORT=5432
     MB_DB_USER=metabase_prod
     MB_DB_PASS=secure_prod_password

     POSTGRES_USER=metabase_prod
     POSTGRES_DB=metabase_production
     POSTGRES_PASSWORD=secure_prod_password
     ```

---

### **4. Infrastructure Deployment**
1. Bootstrap the AWS CDK environment:
   ```bash
   npx cdk bootstrap
   ```

2. Deploy stacks:
   ```bash
   # Deploy Backup Resources
   npx cdk deploy S3BackupStack --require-approval never

   # Deploy Staging Resources
   npx cdk deploy StagingStack --require-approval never

   # Deploy Production Resources
   npx cdk deploy ProductionStack --require-approval never

   # Deploy CI/CD Pipeline
   npx cdk deploy PipelineStack --require-approval never
   ```

---

## **Usage Guide**

### **1. Starting Services**
Use the `start_metabase.sh` script:
```bash
# Start staging environment
./scripts/start_metabase.sh staging

# Start production environment
./scripts/start_metabase.sh production
```

### **2. Backups**
Automate backups to S3:
```bash
./scripts/backup_s3.sh
```

### **3. Migrating Schema**
Apply schema changes:
```bash
./scripts/migrate_database.sh
```

---

## **Scripts Overview**

### **1. `setup_instance.sh`**
- Sets up the instance by installing Docker, AWS CLI, and other dependencies.

### **2. `start_metabase.sh`**
- Starts Metabase services for the specified environment using Docker Compose.

### **3. `backup_s3.sh`**
- Backs up PostgreSQL databases and Metabase volumes to AWS S3.

### **4. `migrate_database.sh`**
- Applies schema changes to the PostgreSQL database.

---

## **Folder Structure**
```plaintext
project-root/
├── .github/
│   └── workflows/                     # CI/CD workflows
├── cdk/                               # CDK infrastructure as code
│   ├── lib/                           # Stack definitions
│   ├── app.py                         # CDK entry point
│   └── requirements.txt               # Python dependencies
├── config/                            # Environment-specific configurations
│   ├── staging/                       # Staging environment
│   ├── production/                    # Production environment
├── data/                              # Data and backups
│   ├── volumes/                       # Persistent volumes
│   ├── backups/                       # Backup storage
│   └── schema/                        # Database schema definitions
├── scripts/                           # Automation scripts
├── README.md                          # Documentation
└── .env                               # Local environment variables (gitignored)
```

---

## **Best Practices**
1. **Secrets Management**:
   - Never commit `.env` files. Use AWS Secrets Manager for sensitive data in production.

2. **Backup Strategy**:
   - Schedule `backup_s3.sh` using a cron job or AWS EventBridge.

3. **Testing**:
   - Always test schema changes on staging before applying them to production.

4. **Security**:
   - Ensure IAM roles and policies follow the principle of least privilege.

5. **Monitoring**:
   - Integrate with CloudWatch or ELK stack for logs and alerts.

---

## **Troubleshooting**

### **1. Docker Services Not Starting**
- Ensure Docker is running:
  ```bash
  sudo systemctl start docker
  ```

### **2. Failed Deployment**
- Verify AWS credentials:
  ```bash
  aws configure
  ```
- Check CI/CD logs in GitHub Actions.

### **3. Backup Failures**
- Ensure the S3 bucket exists and permissions are configured correctly:
  ```bash
  aws s3 ls s3://your-s3-bucket-name
  ```

---