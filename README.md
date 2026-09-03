# Mercedes-Benz Vehicle Analytics Platform

![CI](https://github.com/nabila-natasha/mercedes-snowflake-analytics/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/nabila-natasha/mercedes-snowflake-analytics/actions/workflows/cd.yml/badge.svg)

An end-to-end automotive data engineering, analytics and machine learning
platform built using Snowflake, Python, SQL, Power BI and GitHub Actions.

The project demonstrates how raw automotive datasets can be transformed
into production-ready analytical data products and machine learning
insights through a cloud data platform with automated CI/CD validation
and deployment.

---

## 1. Project Overview

This project combines three analytical areas:

1. Mercedes-Benz Used Car analytics
2. Manufacturing test-time machine learning
3. Vehicle Safety analytics

The platform uses Snowflake as the cloud data warehouse and analytical
platform, Python for ingestion and machine learning, SQL for data
transformation and validation, Power BI for business intelligence, and
GitHub Actions for automated CI/CD.

The project was designed to demonstrate an end-to-end production-style
data workflow rather than a standalone dashboard or machine learning
notebook.

---

## 2. Business Problems

### Used Vehicle Analytics

Used vehicle data is incorporated into the analytical platform to support
vehicle and market-level analysis.


### Manufacturing Analytics

The manufacturing component focuses on predicting vehicle manufacturing
test time using machine learning.

The objective is to:

- Establish a naive baseline
- Train a Random Forest regression model
- Tune model hyperparameters
- Evaluate train/test performance
- Identify important manufacturing features
- Compare model performance against the baseline


### Vehicle Safety Analytics

The safety analytics component explores:

- Vehicle configurations
- Model years
- Safety technology adoption
- Vehicle complaints
- Recalls
- Investigations
- Crash ratings

The objective is to provide a consolidated view of vehicle safety
performance and identify patterns across model years and vehicle models.


---

## 3. Key Results

### Manufacturing Machine Learning Model

The final tuned Random Forest model achieved:

| Metric | Result |
|---|---:|
| Test MAE | 5.30 seconds |
| Test R² | 0.59 |
| Baseline Test MAE | 10.14 seconds |
| MAE Improvement | 47.7% |
| Train MAE | 5.11 seconds |

The tuned model reduced test mean absolute error (MAE) by approximately 47.7%
compared with the naive baseline.

The relatively small difference between training MAE (5.11 seconds) and
test MAE (5.30 seconds) indicates that the final model does not exhibit a
large train/test performance gap.


---

## 4. Technology Stack

| Area | Technology |
|---|---|
| Cloud Data Platform | Snowflake |
| Data Ingestion | Python |
| Transformation | Snowflake SQL |
| Data Modelling | Star Schema |
| Machine Learning | Python / scikit-learn |
| Machine Learning Model | Random Forest Regression |
| Hyperparameter Tuning | Randomized Search |
| BI / Visualization | Power BI |
| Version Control | Git / GitHub |
| CI/CD | GitHub Actions |
| Testing | Python / pytest |
| Architecture Documentation | draw.io |

---

## 5. Architecture

The project follows a layered data architecture:

```text
External Data Sources
        |
        v
Python Ingestion
        |
        v
Snowflake RAW
        |
        v
Snowflake SILVER
        |
        v
Snowflake GOLD
        |
        +--------------------+
        |                    |
        v                    v
     Power BI          Manufacturing ML Analytics
        |                    |
        v                    v
Used-Car &  Safety       Test-Time
Dashboards              Prediction

```

The complete architecture is documented in:
docs/architecture.md

Architecture diagram:
docs/screenshots/architecture.png


---

## 6. Data Architecture

The Snowflake environment uses a medallion-style architecture:

```text
RAW
 |
 | ingestion / standardisation
 v
SILVER
 |
 | business transformation
 v
GOLD
 |
 +----> Power BI
 |
 +----> Analytical / ML workflows

```

### RAW
Contains source data loaded into Snowflake with minimal transformation.

### SILVER
Contains cleaned, standardised and transformed data suitable for analytical processing.

### GOLD
Contains business-ready analytical structures consumed by downstream analytics and reporting.

### AUDIT
Contains validation and operational audit information used to support data quality and production monitoring.


---

## 7. Analytical Data Model

The analytical layer follows a star-schema approach where measurable
business events are represented by fact tables and descriptive
attributes are represented by dimension tables.

The model is consumed by Power BI to provide interactive analytical
reporting.

The Power BI data model is documented in:
docs/data-model.md


---

## 8. Machine Learning

The manufacturing machine learning pipeline predicts manufacturing test time.

### Modelling approach

The workflow consists of:

1. Data preparation
2. Train/test split
3. Naive baseline
4. Random Forest regression
5. Hand-tuned model evaluation
6. Hyperparameter tuning
7. Final model evaluation
8. Feature importance analysis
9. Residual analysis
10. Final model

The final model is a tuned Random Forest regression model.
The model achieved:

Test MAE: 5.30 seconds
Test R²: 0.59
MAE improvement versus baseline: 47.7%

More detail is available in:
docs/ml-model.md


---

## 9. Power BI Analytics

The project contains three main analytical dashboards.

### Used Car Analytics
 The dashboard provides:
 - Total Cars
 - Average Price
 - Average Miles Per Gallon (MPG)
 - Average Mileage
 - Average Price by Year
 - Cars by Model
 - Price vs Mileage
 - Average & Median Price by Fuel Type

 ### Manufacturing ML Performance
 The dashboard provides:
 - Test MAE
 - Test R²
 - MAE Improvement vs Baseline
 - Train/test R² Gap
 - Actual vs Predicted Test Time
 - Feature Importance
 - Train/test model comparison

### Vehicle Safety Analytics
The dashboard provides:
 - Vehicle configurations
 - Electronic Stability Control adoption
 - Complaints
 - Recalls
 - Investigations
 - Crash Ratings by Model Year
 - Recalls by Model Year
 - Complaints vs Recalls
 - Safety Technology Adoptions

Dashboard screenshots are available under:
docs/screenshots/

--- 

## 10. CI/CD

GitHub Actions automates validation and production deployment.

#### Continuous Integration
The CI workflow validates code changes before they are considered production-ready.

The workflow includes automated testing and Snowflake-related validation.

#### Continuous Deployment
The CD workflow automates the production deployment process, including:

1. Source data ingestion
2. Loading data into Snowflake
3. Production database object deployment
4. Transformation layer deployment
5. Production validation

Both CI and CD workflows completed successfully for the final project
version.

Detailed documentation:
docs/validation.md


--- 

## 11. Reproducibility

The project is designed so that the main data engineering workflow can
be reproduced through the Python scripts, Snowflake SQL deployment
scripts and GitHub Actions workflows.

Credentials and secrets are not stored in the repository.

Snowflake credentials required by GitHub Actions are supplied through
GitHub repository secrets / environment configuration.


--- 

## 12. Data Governance and Security

The project follows several basic production-oriented practices:
- Credentials are not committed to Git
- Snowflake access is managed through roles
- Development and analytical responsibilities are separated
- Production deployment is automated
- Validation is executed as part of the deployment workflow
- Raw and analytical data are separated into different schemas


--- 

## 13. Validation

The final repository was validated through:
- Automated CI tests
- Snowflake connectivity validation
- Production deployment
- Production data validation
- Power BI dashboard verification

CI and CD execution evidence is documented in:
docs/validation.md


--- 

## 14. Project Limitations

This project is a portfolio implementation and therefore does not
represent a production Mercedes-Benz enterprise environment.

Limitations include:
- Public / externally available datasets
- Limited historical and operational context
- No real-time manufacturing data stream
- ML performance depends on the available training dataset
- Power BI is used primarily for analytical reporting rather than
enterprise deployment


--- 

## 15. Future Improvements

Potential extensions include:
- Real-time vehicle or manufacturing data ingestion
- Streaming architecture using Azure Event Hubs or Kafka
- Model monitoring
- Automated ML retraining
- Data quality monitoring and alerting
- Snowflake cost and warehouse optimisation
- Additional vehicle safety indicators
- Model explainability using SHAP
- Cloud-based orchestration

---

## What this project demonstrates

- Cloud data warehousing with Snowflake
- Medallion architecture (RAW → SILVER → GOLD)
- Automated ingestion pipelines
- Snowflake Dynamic Tables
- Star-schema analytical modelling
- Machine learning for manufacturing test-time prediction
- Hyperparameter tuning and model validation
- Power BI analytics and reporting
- Automated CI/CD using GitHub Actions
- Production deployment and data-quality validation
