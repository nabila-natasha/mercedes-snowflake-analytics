# Snowflake SQL

This directory contains SQL used to configure, deploy, transform and
validate the Snowflake environment.

---

# Directory Structure

```text
sql/
│
├── setup/
│   └── 01_environment.sql
│   └── 02_ci_cd_role.sql
│   └── 03_github_ci_user.sql
│
├── deployment/
│   └── 01_deploy_dev.sql
│   └── 02_deploy_prod.sql
│
├── raw/
│   └── 01_create_raw_tables.sql
│   └── 02_nhtsa_raw_ingestion.sql
|
├── silver/
│   └── 01_build_silver_tables.sql
|
├── gold/
│   └── 01_create_dim_tables.sql
│   └── 02_create_fact_tables.sql
│   
└── tests/
    └── 01_environment_validation.sql
```

---

# 1. Setup

Creates and configures the initial Snowflake environment.

Responsibilities include:
- Database creation
- Schema creation
- Role creation
- Role hierarchy
- Permissions

Main schemas:
- RAW
- SILVER
- GOLD
- AUDIT

---

# 2. Production Deployment

Builds the production Snowflake environment.

The deployment includes:
- File formats
- Stages
- RAW tables
- SILVER transformations
- Analytical objects
- Dynamic Tables where applicable
- Production validation

The script is designed to be executed by the deployment workflow.

---

# 3. Transformations

The transformation SQL converts source-aligned RAW data into cleaned,
standardised and analytical structures.

The transformation process follows:

```text
RAW
 |
 v
SILVER
 |
 v
GOLD
```

---

# 4. Validation

Validation SQL checks that the production environment has been deployed
correctly and that expected objects and data are available.

Validation is integrated into the production deployment process.

---

# 5. Security

Credentials are not stored in SQL files.

Snowflake access is controlled using roles.

The project separates engineering and analytical responsibilities through
dedicated Snowflake roles.
