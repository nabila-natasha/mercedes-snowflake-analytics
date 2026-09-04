# Mercedes-Benz Vehicle Analytics Platform

![CI](https://github.com/nabila-natasha/mercedes-snowflake-analytics/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/nabila-natasha/mercedes-snowflake-analytics/actions/workflows/cd.yml/badge.svg)

An end-to-end automotive data engineering, analytics and machine learning
platform built using Snowflake, Python, SQL, Power BI and GitHub Actions.

The project demonstrates how multiple automotive datasets can be ingested,
transformed and modelled into analytical data products, machine learning
insights and interactive Power BI dashboards through a production-style
cloud data platform with automated CI/CD validation and deployment.

---

## 1. Project Overview

This project brings together three analytical use cases on a common
data platform:

1. Mercedes-Benz used vehicle analytics
2. Manufacturing test-time machine learning
3. Vehicle safety analytics

The platform uses:

- Snowflake as the cloud data platform
- Python for data ingestion and machine learning
- SQL for transformation, analytical modelling and validation
- Power BI for business intelligence and reporting
- GitHub for version control
- GitHub Actions for continuous integration and deployment
- pytest for automated testing

The project was designed to demonstrate an end-to-end data engineering
workflow rather than a standalone dashboard, SQL exercise or machine
learning notebook.

---

## 2. Business Problems

### Used Vehicle Analytics

The used vehicle analysis provides a market-oriented view of Mercedes-Benz
vehicles using attributes such as model, year, price, mileage, fuel type
and MPG.

The dashboard supports analysis of:

- Total vehicles
- Average vehicle price
- Average MPG
- Average mileage
- Price by vehicle year
- Vehicle count by model
- Price versus mileage
- Average and median price by fuel type

The objective is to understand pricing patterns, vehicle characteristics
and potential relationships between mileage, age and price.

---

### Manufacturing Analytics

The manufacturing component focuses on predicting vehicle manufacturing
test time using machine learning.

The objective is to:

- Establish a naive baseline
- Train a Random Forest regression model
- Perform model tuning
- Evaluate train/test performance
- Identify important predictive features
- Analyse prediction residuals
- Compare model performance against the baseline

The final model is intended to demonstrate how machine learning can be
used to support manufacturing performance analysis.

---

### Vehicle Safety Analytics

The safety analytics component consolidates vehicle safety information
including:

- Vehicle configurations
- Model years
- Safety technology adoption
- Vehicle complaints
- Recalls
- Investigations
- Crash ratings

The objective is to provide a consolidated view of vehicle safety
patterns across models and model years.

---

## 3. Key Results

### Manufacturing Machine Learning Model

The final tuned Random Forest regression model achieved:

| Metric | Result |
|---|---:|
| Baseline Train MAE | 10.08 s |
| Baseline Test MAE | 10.14 s |
| Tuned Model Train MAE | 5.11 s |
| Tuned Model Test MAE | 5.30 s |
| Test R² | 0.59 |
| MAE Improvement vs Baseline | 47.7% |
| Train/Test R² Gap | 0.013 |

The final model reduced test MAE from 10.14 seconds for the naive
baseline to 5.30 seconds, representing a 47.7% reduction in mean
absolute error.

The relatively small difference between train MAE (5.11 seconds) and
test MAE (5.30 seconds) indicates that the final model does not show a
large train/test performance gap.

---

## 4. Technology Stack

| Area | Technology |
|---|---|
| Cloud Data Platform | Snowflake |
| Data Ingestion | Python |
| Data Transformation | Snowflake SQL |
| Data Modelling | Star Schema |
| Machine Learning | Python / scikit-learn |
| ML Algorithm | Random Forest Regression |
| Hyperparameter Tuning | Randomized Search |
| Business Intelligence | Power BI |
| Version Control | Git / GitHub |
| CI/CD | GitHub Actions |
| Automated Testing | pytest |
| Architecture Design | draw.io |

---

## 5. Architecture

The platform follows a layered data architecture in which source data
flows through Python ingestion into Snowflake and is transformed into
business-ready analytical structures.

```text
                         DATA SOURCES
                              |
                              v
                     PYTHON INGESTION
                              |
                              v
                    +-------------------+
                    |     SNOWFLAKE     |
                    |                   |
                    |       RAW         |
                    |        |          |
                    |      SILVER       |
                    |        |          |
                    |       GOLD        |
                    |                   |
                    |      AUDIT        |
                    +---------+---------+
                              |
                 +------------+------------+
                 |                         |
                 v                         v
             POWER BI              MACHINE LEARNING
                 |                         |
                 v                         v
        Analytical Dashboards      Test-Time Prediction
```

The complete architecture is documented in:
`docs/architecture.md`

Architecture diagram:
`docs/screenshots/architecture.PNG`

---

## 6. Snowflake Data Architecture

The Snowflake environment follows a medallion-style architecture.

```text
                    MERCEDES_PROD
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
         RAW           SILVER          GOLD
          |              |              |
          |              |              +--> Analytics
          |              |              +--> Power BI
          |              |
          |              +--> Cleaned /
          |                   Standardised Data
          |
          +--> Source-Aligned Data

                         |
                         v
                       AUDIT

```

### RAW
Contains source data loaded into Snowflake with minimal transformation.

### SILVER
Contains cleaned, standardised and transformed data prepared for downstream analytical processing.

### GOLD
Contains business-ready analytical structures used by Power BI and downstream analytical workflows.

### AUDIT
Contains validation and operational information supporting data quality and production validation.

Snowflake Dynamic Tables are used where appropriate to maintain
transformed analytical data automatically based on the defined
refresh/target-lag configuration.

---

## 7. Analytical Data Model

The analytical layer uses a star-schema approach.

Fact structures contain measurable business events and metrics, while
dimension structures provide descriptive context for filtering,
grouping and analysis.

The Power BI semantic model provides the reporting layer used by the
analytical dashboards.

See:  
`docs/data-model.md`

---

## 8. Machine Learning

The manufacturing machine learning workflow follows:

```text
Manufacturing Dataset
        |
        v
Data Preparation
        |
        v
Train / Test Split
        |
        v
Naive Baseline
        |
        v
Random Forest
        |
        v
Model Tuning
        |
        v
Final Tuned Model
        |
        +--------> Feature Importance
        |
        +--------> Residual Analysis
        |
        v
Power BI

```

The final model is a tuned Random Forest regression model.

#### Final performance
- Test MAE: 5.30 seconds
- Test R²: 0.59
- MAE improvement versus baseline: 47.7%
- Train/Test R² gap: 0.013

More detail is available in:  
`docs/ml-model.md`

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
- Train/Test R² Gap
- Actual vs Predicted Test Time
- Residual classification
- Feature Importance
- Train/Test model comparison

Residuals are defined as:  
**Residual = Actual Test Time - Predicted Test Time**

Therefore:
- Residual > +10 s → Under-predicted
- -10 s ≤ Residual ≤ +10 s → Close to Actual
- Residual < -10 s → Over-predicted
The ±10-second threshold is an analytical tolerance selected for
dashboard interpretation.

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
`docs/screenshots/`

--- 

## 10. CI/CD

GitHub Actions automates testing, validation and production deployment.

#### Continuous Integration
The CI workflow validates project changes through automated checks.

The workflow includes:
1. Repository checkout
2. Python environment setup
3. Dependency installation
4. Automated testing
5. Project validation
6. Snowflake-related validation where configured

#### Continuous Deployment
The CD workflow automates the production deployment process.

The workflow includes:
1. Source data ingestion
2. Used vehicle data loading
3. Manufacturing data loading
4. NHTSA data loading
5. Snowflake production deployment
6. Transformation and analytical object deployment
7. Production validation

The final project version successfully completed both CI and CD.

See:  
`docs/validation.md`

--- 

## 11. Reproducibility

The project is designed around reproducible data engineering and
analytical workflows.

The main components can be reproduced using:
- Python ingestion scripts
- Snowflake SQL setup and deployment scripts
- Automated validation tests
- GitHub Actions CI/CD workflows

Credentials and secrets are not stored in the repository.

Snowflake credentials required by automated workflows are supplied
through GitHub repository secrets and environment configuration.

--- 

## 12. Data Governance and Security

The project follows several basic production-oriented practices:
- Credentials are not committed to Git
- Snowflake access is managed through roles
- Engineering and analytical access are separated
- RAW, SILVER, GOLD and AUDIT responsibilities are separated
- Production deployment is automated
- Production validation is executed after deployment
- Data ingestion is separated from transformation logic

--- 

## 13. Validation

The final repository was validated through:
- Automated CI tests
- Snowflake connectivity validation
- Production deployment
- Production data validation
- Power BI dashboard verification

Both GitHub Actions workflows completed successfully for the final
implementation.

Validation evidence and methodology are documented in:  
`docs/validation.md`

--- 

## 14. Project Limitations

This is a portfolio implementation and does not represent the internal
Mercedes-Benz enterprise data environment.

Limitations include:
- Use of publicly available or externally sourced datasets
- Limited historical and operational context
- No real-time manufacturing data stream
- Machine learning performance depends on the available dataset
- No enterprise-scale model monitoring
- Power BI is used for analytical reporting rather than enterprise
cloud deployment

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

## 16. Project Status

#### Status: Completed

The final implementation includes:
- Snowflake data platform
- RAW / SILVER / GOLD / AUDIT architecture
- Python ingestion
- SQL transformations
- Manufacturing ML pipeline
- Hyperparameter tuning
- Power BI dashboards
- Automated CI
- Automated CD
- Production validation
- Technical documentation
