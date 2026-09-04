# System Architecture

## 1. Overview

The Mercedes-Benz Vehicle Analytics Platform is an end-to-end data
engineering, analytics and machine learning platform.

The architecture is organised around three independent analytical
domains:

- Used Vehicle Analytics
- Manufacturing Machine Learning
- Vehicle Safety Analytics

All three domains use Snowflake as the central cloud data platform.

GitHub Actions provides the CI/CD automation and deployment control
layer.

---

# 2. Architectural Principles

The platform follows these principles:

1. Separate data ingestion from transformation
2. Preserve source-aligned data in RAW
3. Transform data through layered Snowflake schemas
4. Keep independent business domains analytically separate
5. Use dimensional modelling where appropriate
6. Automate testing and deployment
7. Validate the production environment after deployment
8. Keep credentials outside source control

---

# 3. End-to-End Architecture

```text
                         DATA SOURCES
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
       Used Vehicle      Manufacturing      NHTSA
          Data               Data         Safety Data
             |                |                |
             +----------------+----------------+
                              |
                              v
                     PYTHON INGESTION
                              |
                              v
                    SNOWFLAKE PLATFORM
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
             RAW            SILVER           GOLD
              |               |               |
              |               |               |
              +---------------+---------------+
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
       USED VEHICLE      MANUFACTURING     VEHICLE SAFETY
        ANALYTICS             ML              ANALYTICS
            |                 |                 |
            +-----------------+-----------------+
                              |
                              v
                           POWER BI
```

---

# 4. Data Source Layer

The platform uses three independent source domains.

#### Used Car Data
Supports vehicle pricing and market analysis.

#### Manufacturing Data
Supports manufacturing test-time machine learning.

#### NHTSA Vehicle Safety Data
Supports vehicle safety analysis.

The datasets are not assumed to share a universal primary key.

---

# 5. Ingestion Layer

Python is used to move source data into Snowflake.

The general file-based ingestion pattern is:

```text
Source Dataset
      |
      v
Python Loader
      |
      v
Snowflake Internal Stage
      |
      v
COPY INTO
      |
      v
RAW Table
```
The ingestion layer is intentionally separated from downstream transformation.

---

# 6. Snowflake Data Platform

The production database is organised into four main schemas:

```text
MERCEDES_PROD
│
├── RAW
├── SILVER
├── GOLD
└── AUDIT
```

#### RAW  
Source-aligned landing layer.

Responsibilities:
- Store ingested source data
- Preserve source attributes
- Provide a stable downstream input

#### SILVER
Cleaned and standardised data layer.

Responsibilities:
- Data type standardisation
- Cleaning
- Normalisation
- Business preparation
- Transformation

#### GOLD
Business-ready analytical layer.

Responsibilities:
- Analytical structures
- Business metrics
- Reporting-ready data

#### AUDIT
The AUDIT layer contains validation and operational information used
to support production data quality checks.


---

# 7. Snowflake Dynamic Tables

Snowflake Dynamic Tables are used for selected derived analytical
structures.

The purpose is to allow Snowflake to maintain derived data according to
the defined target-lag configuration rather than requiring every
transformation to be manually orchestrated.

Dynamic Tables therefore form part of the transformation / analytical
processing architecture rather than being a separate data layer.

---

# 8. Analytical Domains

The platform contains three separate analytical domains.

```text
                         GOLD
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
      USED CAR       MANUFACTURING    VEHICLE SAFETY
      ANALYTICS           ML             ANALYTICS
```

#### Used Vehicle Analytics
Focuses on:
- Price
- Mileage
- MPG
- Model
- Year
- Fuel type

#### Manufacturing ML
Focuses on:
- Test-time prediction
- Model performance
- Feature importance
- Residual analysis

#### Vehicle Safety
- Focuses on:
- Complaints
- Recalls
- Investigations
- Crash ratings
- Safety technology
- Model-year trends

# 8. Security Architecture  

Snowflake access is managed through role-based access control.

The project separates engineering and analytical responsibilities.

```text
                         SYSADMIN
                            |
              +-------------+-------------+
              |                           |
              v                           v
          MERC_DE                   MERC_ANALYST
              |                           |
              v                           v
       Engineering /                Analytical /
        Deployment                   BI Access
```
The data engineering role supports deployment and engineering activities.

The analyst role supports analytical consumption.

---

# 9. Power BI Layer

Power BI consumes analytical data from Snowflake.

The reporting layer contains three dashboard products:

```text
Snowflake Analytical Data
          |
    +-----+-----+-----+
    |           |     |
    v           v     v
 Used Car   Manufacturing Safety
 Analytics       ML      Analytics
```
The dashboards provide the business-facing presentation layer.

---

# 10. Machine Learning Layer

The manufacturing ML workflow is implemented in Python.

```text
Manufacturing Data
        |
        v
Feature Preparation
        |
        v
Train / Test Split
        |
        +-------------------+
        |                   |
        v                   v
Naive Baseline       Random Forest
                            |
                            v
                     Hyperparameter
                        Tuning
                            |
                            v
                      Final Model
                            |
               +------------+------------+
               |                         |
               v                         v
       Feature Importance         Residual Analysis
               |                         |
               +------------+------------+
                            |
                            v
                         Power BI
```

# 11. Security Architecture

Snowflake access is managed using role-based access control.

```text
                         SYSADMIN
                            |
              +-------------+-------------+
              |                           |
              v                           v
          MERC_DE                   MERC_ANALYST
              |                           |
              v                           v
       Engineering /              Analytical / BI
        Deployment                    Access
```
The engineering role supports engineering and deployment activities.

The analyst role supports analytical consumption.

---

# 12. CI/CD Architecture

GithHub Actions operates as the automation and deployment control plane.

```text
Developer
    |
    v
GitHub Repository
    |
    v
GitHub Actions
    |
    +-------------------+
    |                   |
    v                   v
   CI                   CD
    |                   |
    v                   v
Automated Tests    Production Deployment
                        |
                        v
                    Snowflake
                        |
                        v
                 Production Validation
```

#### CI
CI validates project changes through automated checks.

#### CD
CD deploys the production environment and runs post-deployment validation.

---

# 13. Deployment Flow

The production deployment follows:

```text
GitHub
  |
  v
CD Workflow
  |
  +--> NHTSA Ingestion
  |
  +--> Used Vehicle Loading
  |
  +--> Manufacturing Loading
  |
  +--> Snowflake Deployment
  |
  +--> Production Validation
  |
  v
Deployment Result
```

---

# 14. Architecture Summary

The platform separates:

```text
SOURCE
   ↓
INGESTION
   ↓
STORAGE
   ↓
TRANSFORMATION
   ↓
ANALYTICS
   ↓
REPORTING / ML
```

while GitHub Actions provides:

```text
VERSION CONTROL
       ↓
      CI
       ↓
      CD
       ↓
PRODUCTION VALIDATION
```
