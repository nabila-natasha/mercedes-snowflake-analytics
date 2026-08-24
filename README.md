# mercedes-snowflake-analytics

Data Sources
------------
1. UK Used Car Dataset
2. Mercedes-Benz Greener Manufacturing Dataset
3. NHTSA API

Raw datasets are excluded from this repository.
See README for dataset source and ingestion instructions.

"Recall data is sourced from NHTSA (US market) and is not scoped to the same physical vehicles as the UK resale dataset. It's included to demonstrate live incremental API ingestion and to give an illustrative (not literal) safety signal by model line. A production system would instead integrate DVSA's manufacturer-facing Recalls API, which requires organizational onboarding."