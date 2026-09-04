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
