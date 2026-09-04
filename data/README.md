# Data

This directory contains data-related documentation and, where
appropriate, local source datasets used during development.

Raw production datasets are not necessarily committed to GitHub when
they are large, externally sourced, reproducible or unnecessary for
running the repository code.

---

# Data Domains

## Used Vehicle

Used vehicle listing data used for pricing and vehicle characteristic
analysis.

## Manufacturing

High-dimensional manufacturing data used for test-time prediction.

## NHTSA

Vehicle safety data used for complaints, recalls, investigations and
related safety analysis.

Recall data is sourced from NHTSA (US market) and is not scoped to the 
same physical vehicles as the UK resale dataset. It's included to demonstrate
live incremental API ingestion and to give an illustrative (not literal) safety 
signal by model line. A production system would instead integrate DVSA's 
manufacturer-facing Recalls API, which requires organizational onboarding.

---

# Data Handling

The general data flow is:

```text
Source Data
    |
    v
Python Ingestion
    |
    v
Snowflake RAW
    |
    v
  SILVER
    |
    v
   GOLD
    |
    v
 Analytics
```

---

# Data Privacy and Security

Credentials, API keys and other secrets must never be stored in this
directory or committed to Git.

---

# Reproducibility

Where datasets are publicly available, the ingestion scripts provide
the mechanism for loading the source data into Snowflake.

Source-specific details are documented in:  
`docs/data_sources.md`


