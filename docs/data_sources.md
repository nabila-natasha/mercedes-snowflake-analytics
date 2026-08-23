# Mercedes-Benz Vehicle Analytics — Data Sources

## 1. Used Car Dataset

### Source

100,000 UK Used Car Data Set — Mercedes-Benz subset.

### Local file

`data/raw/mercedes.csv`

### Purpose

Used for vehicle resale and pricing analytics.

### Grain

One row represents one used-vehicle listing.

### Columns

| Column | Source Type | Business Meaning |
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

### Initial Data Quality Findings

- 13,119 rows
- 9 columns
- No missing values
- 259 duplicate rows
- Year range: 1970–2020
- Price range: 650–159,999
- Mileage range: 1–259,000
- Tax range: 0-580
- mpg range: 1.1-217.3
- Engine size range: 0–6.2

### Data Quality Decision

Duplicate records will be investigated before the Silver layer.

We will not automatically remove duplicates from RAW because RAW should preserve source data.

---

## 2. Mercedes-Benz Greener Manufacturing

### Source

Mercedes-Benz Greener Manufacturing competition dataset.

### Local file

`data/raw/train.csv`

### Purpose

Used to demonstrate ingestion and processing of high-dimensional manufacturing test-bench data.

### Grain

One row represents one manufacturing observation.

### Columns

- `ID`
- `y`
- `X0` through `X385`

### Initial Data Quality Findings

- 4,209 rows
- 378 columns
- No missing values
- No duplicate rows
- `ID` is an integer identifier
- `y` is a numeric target
- X-columns contain categorical and numeric manufacturing features

### Data Quality Decision

The original anonymized feature names will be preserved in RAW.

Feature interpretation will not be invented because the source does not provide business definitions for X0-X385.

---

## 3. NHTSA Recall API

### Source

NHTSA public vehicle recall API.

### Purpose

Used to demonstrate incremental API ingestion and recall analytics.

### Loading Pattern

API data will be ingested incrementally into Snowflake RAW.

### Expected Business Attributes

Depending on API response:

- manufacturer
- make
- model
- model year
- campaign number
- recall component
- recall summary
- consequence
- remedy

### Data Quality

API response schema will be validated before loading.

---

# Data Integration Strategy

The three sources do not share a reliable technical primary key.

Therefore, they will initially be modeled as separate business domains.

Potential semantic relationships may be established later using normalized vehicle attributes such as:

- make
- model
- model year

Only relationships supported by the source data will be implemented.

No artificial keys will be created solely to force relationships between unrelated datasets.