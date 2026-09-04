# Analytical Data Model

## 1. Overview

The project uses subject-specific analytical models rather than forcing
all source datasets into a single enterprise-wide schema.

This approach is necessary because the Used Vehicle, Manufacturing and
NHTSA datasets have different grains, structures and business purposes.

The analytical model is designed according to the needs of each domain.

---

# 2. Data Modelling Strategy

The platform follows this principle:

```text
                    MERCEDES_PROD
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      Used Car      Manufacturing     Safety
       Domain            ML           Domain
          |              |              |
          v              v              v
    Analytical       ML Feature      Dimensional /
      Model            Matrix        Analytical Model

```

The datasets share the same cloud platform but are not artificially joined.

---

# 3. Star Schema Approach

Where structured analytical reporting requires reusable descriptive
attributes and measurable events, a star-schema approach is used.

The general pattern is:

```text
                  DIMENSION
                      |
                      |
DIMENSION ---- FACT TABLE ---- DIMENSION
                      |
                      |
                  DIMENSION
```
Fact tables contain measurable events or metrics.

Dimension tables provide descriptive context for filtering and grouping.

---

# 4. Power BI Semantic Model

Power BI acts as the semantic and reporting layer.

The semantic model provides:
- Relationships
- Measures
- Calculations
- Business-friendly filtering
- Dashboard-level analytical logic

The actual Power BI model should be treated as the source of truth for
the reporting relationships shown in the dashboard.

---

# 5. Subject Area: Used Car Analytics

The Used Vehicle domain is primarily focused on listing-level vehicle
attributes.

The grain is:
**One row = one used vehicle listing**

Important attributes include:
- Model
- Year
- Price
- Mileage
- Fuel type
- Transmission
- MPG
- Engine size

The model supports:
- Pricing analysis
- Mileage analysis
- Model analysis
- Fuel-type analysis
- Vehicle-year analysis

---

# 6. Subject Area: Manufacturing

The manufacturing dataset is fundamentally different from a conventional
business fact/dimension model.

The source contains:
- ID
- y
- X0–X385

The anonymised feature columns are retained because their original
business meanings are not provided by the source.

The dataset is therefore primarily treated as a machine-learning feature
matrix.

```text
ID
 |
 +--- X0
 +--- X1
 +--- X2
 +--- ...
 +--- X385
 |
 +--- y
```

The ML pipeline uses the X-columns as predictive features and y as the target.

---

# 7. Subject Area: Vehicle Safety

The safety domain contains multiple analytical concepts including:
- Vehicle configuration
- Model
- Model year
- Complaints
- Recalls
- Investigations
- Safety technologies
- Crash ratings

---

# 8. Cross-Domain Relationships

The three source datasets do not share a reliable universal technical
key.

Potential attributes such as:
- Make
- Model
- Model year
may appear across domains.

However, these attributes are not automatically treated as valid
relational keys.

No artificial relationships are created solely to combine unrelated
datasets.

This prevents misleading analytical joins and preserves the integrity
of each subject area.

---

# 9. Power BI Semantic Model Evidence

The Power BI semantic model implements the analytical relationships
used by the dashboards.

The following screenshot shows the implemented table relationships
in Power BI Model view.

![Power BI Semantic Model](./docs/screenshots/data-model.png)

The model view provides visual evidence that the analytical tables
and relationships described in this document have been implemented
in the Power BI reporting layer.

---

# 10. Modelling Principles
The project follows these principles:
- Facts contain measurable business events
- Dimensions contain descriptive context
- Dataset grain is defined before modelling
- Relationships require business justification
- Source data is not artificially joined
- ML feature matrices are treated differently from dimensional
analytical models
- Power BI provides the final semantic/reporting layer

