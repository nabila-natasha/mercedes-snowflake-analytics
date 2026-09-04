# Python Scripts

This directory contains the Python components used by the Mercedes-Benz
Vehicle Analytics Platform.

The scripts support:
- Source data extraction
- Data loading into Snowflake
- File and staging operations
- Manufacturing machine learning
- Model evaluation
- Snowflake SQL deployment through CI/CD

Snowflake SQL remains responsible for database object creation,
transformations and production validation.

---

## Script Overview

| Script | Purpose | Main Responsibility |
|---|---|---|
| `01_ingest_nhtsa.py` | Extract NHTSA safety data | API ingestion |
| `02_load_nhtsa_snowflake.py` | Load NHTSA raw data | Snowflake loading |
| `03_train_manufacturing_model.py` | Train and evaluate ML model | Machine learning |
| `04_load_used_car_snowflake.py` | Load used-car data | Snowflake loading |
| `05_load_manufacturing_snowflake.py` | Load manufacturing data | Snowflake loading |
| `deploy_sql.py` | Execute SQL files against Snowflake | CI/CD deployment |

---

# Scripts

## `01_ingest_nhtsa.py`

### Purpose

Extract Mercedes-Benz vehicle safety data from the NHTSA Safety Ratings
API and prepare the raw API responses for downstream loading.

### Process

The script:

1. Reads Mercedes model/year combinations from the used-car dataset
2. Normalises model names to match the NHTSA vehicle catalogue
3. Queries the NHTSA API for matching vehicle variants
4. Retrieves detailed safety ratings using the NHTSA vehicle IDs
5. Groups results by model year
6. Saves the raw API responses as JSON files

---

## `02_load_nhtsa_snowflake.py`

### Purpose

Load the raw NHTSA JSON files produced by `01_ingest_nhtsa.py` into
Snowflake.

### Process

The script:
1. Identifies the generated NHTSA JSON files
2. Connects to Snowflake using configured credentials
3. Uploads or stages the raw files
4. Loads the data into the appropriate Snowflake RAW structure

### Role in the Pipeline

This script performs the source-to-Snowflake loading step for the
NHTSA safety domain.

The data remains in the RAW layer for downstream SQL transformation.

---

## `03_train_manufacturing_model.py`

### Purpose

Train, tune and evaluate the machine learning model used to predict
manufacturing test time.

### Workflow

The script performs:
1. Data loading
2. Data preparation
3. Feature identification
4. Train/test split
5. Naive baseline evaluation
6. Random Forest regression
7. Hyperparameter tuning
8. Final model evaluation
9. Feature importance analysis
    
### Model

The final model uses a tuned Random Forest regression approach.

The model is evaluated using metrics including:
- MAE
- RMSE
- R²

The workflow also compares the final model against the naive baseline
to quantify performance improvement.

---

## `04_load_used_car_snowflake.py`

### Purpose

Load the Mercedes-Benz used vehicle dataset into Snowflake.

### Process

The script:
1. Connects to Snowflake
2. Uploads the source CSV to a Snowflake internal stage
3. Loads the staged data into the appropriate RAW table using `COPY INTO`
   
### Input
`data/raw/mercedes.csv`

### Role in the Pipeline

This script performs the used-vehicle source loading stage.

The raw data is subsequently transformed through Snowflake SQL.

---

## `05_load_manufacturing_snowflake.py`

### Purpose

Load the manufacturing dataset into Snowflake.

### Process

The script:
1. Connects to Snowflake
2. Uploads the manufacturing CSV to a Snowflake internal stage
3. Loads the staged data into the appropriate RAW table using `COPY INTO`

### Input
`data/raw/train.csv`

### Role in the Pipeline

This script performs the manufacturing source loading stage.

The raw manufacturing data is subsequently processed through the
machine learning workflow and Snowflake analytical pipeline.

---

## `deploy_sql.py`

### Purpose

Execute version-controlled Snowflake SQL files as part of the CI/CD
deployment process.

### Process

The script:
1. Receives a SQL file path as a command-line argument
2. Validates that the SQL file exists
3. Reads the SQL file
4. Splits the file into individual SQL statements
5. Removes empty statements
6. Connects to Snowflake
7. Executes each SQL statement sequentially
8. Reports execution progress
9. Reports the failing SQL statement if an error occurs
10. Closes the Snowflake connection

---

# Role in CI/CD

`deploy_sql.py` acts as the execution bridge between GitHub Actions and
the version-controlled Snowflake SQL deployment scripts.

```text
GitHub Actions
      |
      v
deploy_sql.py
      |
      v
SQL Deployment File
      |
      v
  Snowflake
```

The SQL file is supplied dynamically, allowing the same Python utility
to execute different deployment scripts without hard-coding the SQL
inside the Python code.

---

# Configuration and Authentication

Credentials are not hard-coded in the Python scripts.

Snowflake authentication details are supplied through environment
variables and GitHub Actions Secrets where required.

Typical Snowflake connection parameters include:
- Account
- User
- Password
- Role
- Warehouse
- Database
- Schema

Sensitive credentials must not be committed to the repository.

---

# Separation of Responsibilities

The project separates Python-based processing from Snowflake SQL
responsibilities.

Python

Python is responsible for:
- API extraction
- Source file handling
- Snowflake file loading
- Machine learning
- Model evaluation
- CI/CD SQL execution
- Snowflake SQL

Snowflake SQL is responsible for:
- Database setup
- Schema creation
- File formats
- Stages
- Tables
- Data transformations
- Analytical objects
- Dynamic tables
- Production validation

This separation keeps ingestion, machine learning, database
transformation and deployment logic modular and easier to maintain.

---

# Pipeline Relationship

The main relationship between the scripts can be summarised as:

```text
                 SOURCE DATA
                     |
        +------------+-------------+
        |            |             |
        v            v             v
    NHTSA API    Used Cars    Manufacturing
        |            |             |
        v            v             v
01_ingest_nhtsa     |             |
        |            |             |
        v            v             v
   Raw JSON       04_load       05_load
        |            |             |
        v            +------+------+ 
02_load_nhtsa          |
        |              |
        +------+-------+
               |
               v
          SNOWFLAKE RAW
               |
               v
        SNOWFLAKE SQL
               |
               v
        SILVER / GOLD
               |
        +------+------+
        |             |
        v             v
     Power BI        Analytics


Manufacturing Data
        |
        v
03_train_manufacturing_model.py
        |
        +--> Baseline
        +--> Random Forest
        +--> Hyperparameter Tuning
        +--> Evaluation
        |
        v
     Power BI


GitHub Actions
        |
        v
deploy_sql.py
        |
        v
Version-Controlled SQL
        |
        v
Snowflake Production

```
---

# Design Principles

The Python scripts follow several design principles:
- Source extraction is separated from Snowflake loading
- Data loading is separated from SQL transformation
- Machine learning is maintained as a separate analytical workflow
- SQL deployment is handled through a reusable deployment utility
- Credentials are supplied through environment configuration rather
than hard-coded
- Snowflake remains the central platform for persistent analytical data
- GitHub Actions provides automated CI/CD execution
