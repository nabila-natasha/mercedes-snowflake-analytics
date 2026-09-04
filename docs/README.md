# Project Documentation

This directory contains the technical documentation supporting the
Mercedes-Benz Vehicle Analytics Platform.

---

## Documentation Map

| Document | Purpose |
|---|---|
| [Architecture](architecture.md) | End-to-end platform and system architecture |
| [Data Sources](data_sources.md) | Source datasets and business purpose |
| [Data Model](data-model.md) | Analytical and Power BI data model |
| [Machine Learning](ml-model.md) | Manufacturing ML methodology and results |
| [Validation](validation.md) | CI/CD and production validation |

---

## Architecture

`architecture.md`

Documents:
- Source systems
- Python ingestion
- Snowflake architecture
- RAW / SILVER / GOLD / AUDIT layers
- Dynamic Tables
- Power BI
- Machine learning
- GitHub Actions
- CI/CD deployment flow

---

## Data Sources

`data_sources.md`

Documents the source datasets, their business purpose, grain, schema,
data-quality findings and ingestion considerations.

---

## Data Model

`data-model.md`

Documents the analytical star-schema approach and Power BI semantic
model.

The actual Power BI model screenshot is provided as supporting
documentation.

---

## Machine Learning

`ml-model.md`

Documents:

- Manufacturing prediction objective
- Baseline
- Random Forest
- Hyperparameter tuning
- Evaluation metrics
- Feature importance
- Residual analysis
- Model limitations

---

## Validation

`validation.md`

Documents:

- Continuous Integration
- Continuous Deployment
- Snowflake production validation
- Final validation status
- Validation evidence

---

## Screenshots

The `screenshots/` directory contains selected project evidence,
including:

- Power BI dashboards
- Power BI data model
- Snowflake environment
- Snowflake Dynamic Tables
- Snowflake roles
- CI workflow
- CD workflow
- Architecture diagram
