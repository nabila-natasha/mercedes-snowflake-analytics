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
