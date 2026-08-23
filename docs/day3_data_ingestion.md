# Day 3 — Data Ingestion

## Objective

Load Mercedes-Benz vehicle datasets into Snowflake RAW layer.

## Source datasets

### Used Car Dataset

Source:
100,000 UK Used Car Data Set

Selected file:
mercedes.csv

Purpose:
Used vehicle attributes and pricing analysis.

### Mercedes-Benz Greener Manufacturing

Source:
Mercedes-Benz Greener Manufacturing competition dataset.

Selected file:
train.csv

Purpose:
Vehicle manufacturing / production optimization analysis.

## Snowflake RAW Layer

MERCEDES_DEV.RAW

Tables:

- USED_CAR_RAW
- MANUFACTURING_RAW

## Ingestion approach

Used:

- Snowflake internal stages
- CSV file formats
- COPY INTO
- INFER_SCHEMA
- USING TEMPLATE

Problem:
COPY INTO failed because PARSE_HEADER was used in the loading file format.

Root cause:
PARSE_HEADER is intended for schema inference / header matching,
not ordinary COPY INTO loading.

Resolution:
Separated the file formats:
- INFER_FORMAT → PARSE_HEADER = TRUE
- LOAD_FORMAT  → SKIP_HEADER = 1*/

## Data quality checks

Performed:

- Row count validation
- Column validation
- NULL checks
- Sample record inspection
- Schema validation

## Results

USED_CAR_RAW:

13,119 rows

MANUFACTURING_RAW:

4,209 rows