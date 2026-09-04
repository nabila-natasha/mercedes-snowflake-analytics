# Python Scripts

This directory contains Python components used for data ingestion and
machine learning.

---

## Responsibilities

Python is used primarily for:
- Source data loading
- Snowflake connectivity
- File handling
- Machine learning
- Model evaluation

Snowflake SQL is used for database object creation, transformation and
production validation.

---

# Scripts

## `02_load_nhtsa_snowflake.py`

Loads NHTSA vehicle safety data into Snowflake.

The script supports the ingestion layer of the vehicle safety domain.

---

## `03_train_manufacturing_model.py`

Runs the manufacturing machine learning workflow.

The workflow includes:
- Data preparation
- Baseline evaluation
- Random Forest regression
- Hyperparameter tuning
- Model evaluation
- Feature importance
- Residual analysis

---

## `04_load_used_car_snowflake.py`

Loads the used vehicle dataset into Snowflake.

The loading process uses Snowflake staging and table loading.

---

## `05_load_manufacturing_snowflake.py`

Loads the manufacturing dataset into Snowflake.

The workflow uses Snowflake staging and `COPY INTO` processing.

---

# Configuration

Credentials are not hard-coded in the scripts.

Environment variables and GitHub Secrets are used where credentials are
required.

---

# Design Principle

The scripts focus on ingestion and machine learning.

Snowflake SQL remains responsible for:
- Database setup
- Schema creation
- File formats
- Stages
- Tables
- Transformations
- Analytical objects
- Production validation
