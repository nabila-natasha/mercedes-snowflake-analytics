# System Architecture

## 1. Overview

The Mercedes-Benz Vehicle Analytics Platform is an end-to-end data
engineering, analytics and machine learning platform.

The architecture separates:

- Data sources
- Data ingestion
- Data storage
- Data transformation
- Analytical modelling
- Machine learning
- Business intelligence
- CI/CD automation

The platform uses Snowflake as the central cloud data platform.

---

## 2. High-Level Architecture

```text
                         DATA SOURCES
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
          NHTSA         Used Vehicle      Manufacturing
           Data              Data              Data
             |                |                |
             +----------------+----------------+
                              |
                              v
                     PYTHON INGESTION
                              |
                              v
                     SNOWFLAKE PLATFORM
                              |
                +-------------+-------------+
                |             |             |
                v             v             v
               RAW          SILVER         GOLD
                |             |             |
                |             |             +------> Power BI
                |             |
                |             +--------------------> Analytics
                |
                +---------------------------------> Audit / Validation

                              |
                              v
                       ML WORKFLOW
                              |
                              v
                 Manufacturing Prediction
```


---

## 2. Data Sources

The platform combines three main data domains.

#### Used Vehicle Data
Used for:
- Vehicle pricing analysis
- Mileage analysis
- Model analysis
- Fuel type analysis

#### Manufacturing Data
Used for:
- Manufacturing test-time prediction
- Machine learning
- Feature importance
- Residual analysis

#### NHTSA Vehicle Safety Data
Used for:
- Vehicle configurations
- Complaints
- Recalls
- Investigations
- Safety-related attributes
- Crash ratings


---

## 4. Ingestion Architecture

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
This separates data acquisition/loading from downstream transformation.


---

## 5. Snowflake Architecture

The production database is organised into four meain schemas:

```text
MERCEDES_PROD
│
├── RAW
├── SILVER
├── GOLD
└── AUDIT
```

#### RAW  
The RAW layer contains source-aligned data with minimal transformation.

Its purpose is to provide a persistent landing layer for ingested
source data.

#### SILVER
The SILVER layer contains cleaned and standardised data.

Typical responsibilities include:
- Standardisation
- Data type handling
- Cleaning
- Normalisation
- Preparation for analytical modelling

#### GOLD
The GOLD layer contains business-ready analytical structures.

These structures are designed for downstream reporting and analytics.

#### AUDIT
The AUDIT layer contains validation and operational information used
to support production data quality checks.


---

## 6. Snowflake Dynamic Tables

Snowflake Dynamic Tables are used for selected transformed analytical
structures.

The purpose is to allow Snowflake to maintain derived data based on
the defined target-lag configuration rather than requiring every
transformation to be manually orchestrated through repeated data
movement operations.

This is particularly useful for maintaining derived analytical data
within the Snowflake platform.


---

## 7. Security Architecture  

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

## 8. Analytical Layer

The analytical layer is consumed by Power BI.

The platform supports three analytical products:

```text
                    GOLD / ANALYTICAL DATA
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
        Used Vehicle     Manufacturing     Vehicle Safety
          Analytics           ML              Analytics
             |                |                |
             +----------------+----------------+
                              |
                              v
                           POWER BI
```


---

## 8. Machine Learning Architecture

The manufacturing machine learning workflow is implemented in Python.

```text
Manufacturing Data
        |
        v
Feature Preparation
        |
        v
Train / Test Split
        |
        +--------------------+
        |                    |
        v                    v
Naive Baseline          Random Forest
                             |
                             v
                      Model Tuning
                             |
                             v
                     Final Model
                             |
                +------------+------------+
                |                         |
                v                         v
        Feature Importance          Residual Analysis
                |                         |
                +------------+------------+
                             |
                             v
                         Power BI
```







