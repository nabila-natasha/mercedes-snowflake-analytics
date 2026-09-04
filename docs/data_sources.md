# Mercedes-Benz Vehicle Analytics — Data Sources

## 1. Overview

The platform uses three main data domains:

1. Used vehicle data
2. Manufacturing data
3. NHTSA vehicle safety data

These datasets have different grains, structures and business purposes.

They are therefore treated as separate analytical domains rather than
being artificially joined through unsupported keys.

---

# 2. Used Vehicle Dataset

## Source

100,000 UK Used Car Data Set — Mercedes-Benz subset.

## Local File

`data/raw/mercedes.csv`

## Purpose

Used for vehicle resale, pricing and vehicle characteristic analytics.

## Grain

One row represents one used-vehicle listing.

## Columns

| Column | Type | Business Meaning |
|---|---|---|
| model | string | Mercedes vehicle model |
| year | integer | Vehicle registration/model year |
| price | integer | Listed resale price |
| transmission | string | Transmission type |
| mileage | integer | Vehicle mileage |
| fuelType | string | Fuel type |
| tax | integer | Vehicle tax |
| mpg | float | Fuel economy |
| engineSize | float | Engine displacement |

## Initial Data Quality Findings

- 13,119 rows
- 9 columns
- No missing values
- 259 duplicate rows
- Year range: 1970–2020
- Price range: 650–159,999
- Mileage range: 1–259,000
- Tax range: 0–580
- MPG range: 1.1–217.3
- Engine size range: 0–6.2

## Data Quality Decision

RAW should preserve the source data.

Duplicate records are therefore investigated before downstream
transformation rather than automatically removing them from RAW.

---

# 3. Manufacturing Dataset

## Source

Mercedes-Benz Greener Manufacturing competition dataset.

## Local File

`data/raw/train.csv`

## Purpose

Used to demonstrate ingestion and processing of high-dimensional
manufacturing test-bench data and machine learning prediction.

## Grain

One row represents one manufacturing observation.

## Structure

- `ID`
- `y`
- `X0` through `X385`

## Initial Data Quality Findings

- 4,209 rows
- 378 columns
- No missing values
- No duplicate rows
- `ID` is an integer identifier
- `y` is the numeric target
- X-columns contain categorical and numerical manufacturing features

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

## Data Quality Checks

Performed:

- Row count validation
- Column validation
- NULL checks
- Sample record inspection
- Schema validation

## Data Quality Decision

The original anonymised feature names are preserved in RAW.

Feature meanings are not invented because the source dataset does not
provide business definitions for the anonymised X-columns.

---

# 4. NHTSA Vehicle Safety Data

## Source

NHTSA public vehicle safety / recall data.

## Purpose

Used to support vehicle safety analytics covering:

- Vehicle configurations
- Complaints
- Recalls
- Investigations
- Model years
- Safety-related attributes
- Crash-rating information where available

## Loading Pattern

Source API data is retrieved using the Python ingestion layer and loaded
into Snowflake.

The ingestion workflow separates source retrieval from downstream
transformation.

## Expected Attributes

Depending on the source endpoint, attributes may include:

- Manufacturer
- Make
- Model
- Model year
- Campaign number
- Recall component
- Recall summary
- Consequence
- Remedy

## Data Quality Decision

Source responses are validated before downstream analytical use.

---

# 5. Data Integration Strategy

The three domains do not share a reliable technical primary key.

Therefore:

```text
USED VEHICLE
      |
      +----> Used Vehicle Analytics


MANUFACTURING
      |
      +----> Manufacturing ML


NHTSA SAFETY
      |
      +----> Vehicle Safety Analytics

```
They share the same Snowflake platform but remain analytically independent.

Potential semantic relationships may be explored using attributes such as:
- Make
- Model
- Model Year

However, relationships are only implemented where the source data provides
sufficient evidence to support them. No artificial relationships are created 
solely to force unrelated datasets into a single analytical model.

---

# 6. Data Layer Strategy

Source data is loaded into the RAW layer before transformation.

```text
Source
  |
  v
RAW
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
**RAW** preserves source-aligned information.
**SILVER** applies cleaning and standardization.
**GOLD** provides business-ready analytical structures.

---

# 7. Data Quality Principles

The project follows these principles:
- Preserve source data in RAW
- Separate source ingestion from transformation
- Validate source structures before downstream use
- Avoid unsupported cross-domain joins
- Document known data-quality issues
- Apply business transformations downstream of RAW



