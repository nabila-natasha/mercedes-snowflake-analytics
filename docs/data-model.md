# Analytical Data Model

## 1. Overview

The Mercedes-Benz Vehicle Analytics Platform uses a **fact constellation
(also known as a galaxy schema)** for its analytical reporting model.

The model contains multiple fact tables representing different business
processes and grains, with selected dimensions shared across those facts
as **conformed dimensions**.

The primary analytical facts are:

* `FACT_USED_CAR`
* `FACT_VEHICLE_SAFETY`

The main shared dimensions are:

* `DIM_YEAR`
* `DIM_MODEL`

The safety domain also contains:

* `DIM_SAFETY`

The manufacturing dataset is handled separately as a machine-learning
feature matrix because its anonymised features and target do not require
the vehicle dimensions used by the Used Car and Vehicle Safety domains.

This approach avoids forcing unrelated datasets into a single fact table
or creating artificial relationships between domains.

---

# 2. Data Modelling Strategy

The analytical model can be represented conceptually as:

```text
                         FACT CONSTELLATION
                                 |
             +-------------------+-------------------+
             |                                       |
             v                                       v
      USED VEHICLE STAR                      VEHICLE SAFETY STAR
             |                                       |
             |                                       |
       FACT_USED_CAR                         FACT_VEHICLE_SAFETY
          /       \                              /        \
         /         \                            /          \
        v           v                          v            v
 DIM_MODEL       DIM_YEAR                 DIM_MODEL     DIM_YEAR
                                                |
                                                v
                                           DIM_SAFETY
```

`DIM_MODEL` and `DIM_YEAR` act as **conformed dimensions** because they
provide common vehicle attributes that can be used consistently across
the Used Vehicle and Vehicle Safety fact tables.

The result is a constellation of related dimensional models rather than
one large fact table.

This design is consistent with dimensional modelling practices in which
multiple business processes can have separate fact tables while sharing
conformed dimensions.

---

# 3. Why a Fact Constellation Is Used

A single central fact table would require combining different business
processes with different grains.

The two primary fact tables represent different analytical events:

| Fact Table            | Business Process              | Grain                                        |
| --------------------- | ----------------------------- | -------------------------------------------- |
| `FACT_USED_CAR`       | Used vehicle/resale analytics | One row per used vehicle listing             |
| `FACT_VEHICLE_SAFETY` | Vehicle safety analytics      | One row per safety-related analytical record |

These facts have different measures, attributes and business meanings.

Combining them into one physical fact table would introduce unnecessary
sparsity and could create ambiguous or misleading measures.

Instead, each business process retains its own fact table while common
vehicle attributes are represented through shared dimensions.

This is the key characteristic of a fact constellation: multiple
dimensional stars coexist and can share conformed dimensions.

---

# 4. Conformed Dimensions

## 4.1 DIM_YEAR

`DIM_YEAR` provides the common year context used by the relevant
analytical facts.

It allows the Used Vehicle and Vehicle Safety domains to be analysed
using a consistent year dimension.

Conceptually:

```text
                  DIM_YEAR
                     |
          +----------+----------+
          |                     |
          v                     v
   FACT_USED_CAR       FACT_VEHICLE_SAFETY
```

The use of a common year dimension allows measures from separate facts
to be analysed consistently by year where the business grain supports
that analysis.

---

## 4.2 DIM_MODEL

`DIM_MODEL` provides common vehicle model context.

Conceptually:

```text
                  DIM_MODEL
                     |
          +----------+----------+
          |                     |
          v                     v
   FACT_USED_CAR       FACT_VEHICLE_SAFETY
```

This allows the two subject areas to use a consistent model-level
classification rather than maintaining independent model definitions.

The dimension is therefore a **conformed dimension** across the two
analytical stars.

A conformed dimension is a shared dimension whose attributes have
consistent meaning and domains across fact tables.

---

# 5. Used Vehicle Star

The Used Vehicle analytical star is centred on:

```text
                 DIM_YEAR
                    |
                    |
DIM_MODEL ---- FACT_USED_CAR
                    |
                    |
              Used Vehicle
                 Measures
```

## Fact Table

### FACT_USED_CAR

The grain is:

> **One row represents one used vehicle listing.**

The fact supports analysis of measures and attributes such as:

* Vehicle price
* Mileage
* MPG
* Tax
* Engine size
* Fuel type
* Transmission
* Vehicle model
* Vehicle year

The fact is primarily used to support the used vehicle Power BI
dashboard.

---

# 6. Vehicle Safety Star

The Vehicle Safety analytical star is centred on:

```text
                 DIM_YEAR
                    |
                    |
DIM_MODEL ---- FACT_VEHICLE_SAFETY
                    |
                    |
               DIM_SAFETY
```

## Fact Table

### FACT_VEHICLE_SAFETY

This fact represents the analytical records used for vehicle safety
analysis.

The safety domain contains information relating to areas such as:

* Vehicle configurations
* Complaints
* Recalls
* Investigations
* Safety technologies
* Crash ratings

The exact grain of `FACT_VEHICLE_SAFETY` should be interpreted according
to the final Snowflake table definition and the Power BI semantic model.

The important modelling principle is that the safety fact remains
separate from `FACT_USED_CAR` because the two facts represent different
business processes.

---

# 7. DIM_SAFETY

`DIM_SAFETY` contains descriptive attributes specific to the vehicle
safety analytical domain.

Unlike `DIM_YEAR` and `DIM_MODEL`, this dimension is not required by the
Used Vehicle fact.

Conceptually:

```text
                  DIM_YEAR
                     |
                     |
DIM_MODEL ---- FACT_VEHICLE_SAFETY
                     |
                     |
                DIM_SAFETY
```

This is an example of a **local/non-conformed dimension**: it is relevant
to the safety subject area but does not need to be shared with the Used
Vehicle fact.

Not every dimension in a dimensional model needs to be related to every
fact table. Multiple subject areas can contain both conformed dimensions
and dimensions that are local to a particular business process.

---

# 8. Overall Fact Constellation

The implemented analytical structure can therefore be represented as:

```text
                              DIM_YEAR
                             /        \
                            /          \
                           v            v
                  FACT_USED_CAR    FACT_VEHICLE_SAFETY
                        ^                 ^
                       / \               / \
                      /   \             /   \
                     /     \           /     \
               DIM_MODEL   ...     DIM_MODEL  DIM_SAFETY
```

More conceptually:

```text
                         ┌──────────────┐
                         │   DIM_YEAR   │
                         └──────┬───────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
                     ▼                     ▼
             ┌───────────────┐    ┌────────────────────┐
             │FACT_USED_CAR  │    │FACT_VEHICLE_SAFETY │
             └───────┬───────┘    └─────────┬──────────┘
                     │                      │
                     │                      │
                     ▼                      ▼
              ┌────────────┐         ┌────────────┐
              │ DIM_MODEL  │         │ DIM_SAFETY │
              └────────────┘         └────────────┘
```

`DIM_MODEL` and `DIM_YEAR` provide the common analytical context across
the two fact tables.

The facts remain independent at their respective grains.

---

# 9. Manufacturing Domain

The manufacturing dataset is structurally different from the Used
Vehicle and Vehicle Safety analytical domains.

The source dataset contains:

```text
ID
y
X0
X1
X2
...
X385
```

The `X` columns are anonymised manufacturing features and their original
business meanings are not provided by the source dataset.

The manufacturing workflow therefore treats the dataset primarily as a
**machine-learning feature matrix**, rather than forcing it into the
vehicle fact constellation.

Conceptually:

```text
                 MANUFACTURING DATA
                         |
                         v
                 Feature Matrix
                         |
             +-----------+-----------+
             |                       |
             v                       v
        X0 ... X385                  y
        Features                  Target
             |                       |
             +-----------+-----------+
                         |
                         v
                Machine Learning Model
```

The manufacturing ML workflow is documented separately in:

`docs/ml-model.md`

This separation prevents artificial relationships from being created
between anonymised manufacturing features and vehicle dimensions for
which there is no reliable source-supported relationship.

---

# 10. Cross-Domain Relationships

The Used Vehicle and Vehicle Safety datasets contain potentially common
attributes such as:

* Model
* Model year
* Make

However, an attribute appearing in two datasets does not automatically
make it a valid relational key.

The project therefore uses only relationships supported by the
analytical model and source data.

The primary cross-fact integration is achieved through the conformed
dimensions:

```text
                DIM_YEAR
                   |
        +----------+----------+
        |                     |
        v                     v
 FACT_USED_CAR       FACT_VEHICLE_SAFETY


               DIM_MODEL
                   |
        +----------+----------+
        |                     |
        v                     v
 FACT_USED_CAR       FACT_VEHICLE_SAFETY
```

No artificial relationship is created between the manufacturing feature
matrix and the vehicle analytics facts.

---

# 11. Fact Grain

Defining the grain of each fact table is a fundamental modelling
principle.

The project uses separate grains for its different analytical
processes.

### FACT_USED_CAR

**Grain:**

> One row per used vehicle listing.

This grain supports listing-level pricing, mileage and vehicle
characteristic analysis.

### FACT_VEHICLE_SAFETY

**Grain:**

> One row per safety-related analytical record, according to the final
> production table definition.

The safety fact must be analysed according to its actual implemented
grain rather than being treated as a vehicle listing fact.

Maintaining a clearly defined grain prevents measures from being
incorrectly aggregated when facts represent different business
processes. Dimensional modelling guidance emphasises maintaining facts
at a consistent level of detail within each fact table.

---

# 12. Power BI Semantic Model

Power BI acts as the semantic and reporting layer over the analytical
model.

The semantic model provides:

* Relationships
* Measures
* Calculations
* Business-friendly filtering
* Cross-dimensional analysis
* Dashboard-level analytical logic

The Power BI model reflects the fact constellation implemented for the
reporting layer.

The important distinction is:

```text
Snowflake Analytical Model
            |
            v
     Fact + Dimensions
            |
            v
     Power BI Semantic Model
            |
            v
        Dashboards
```

The Power BI model is therefore not a separate replacement for the
Snowflake data model. It is the reporting/semantic representation of
the analytical structures consumed by the dashboards.

---

# 13. Power BI Semantic Model Evidence

The Power BI Model view provides visual evidence of the implemented
relationships between the fact and dimension tables.

The model contains:

* `FACT_USED_CAR`
* `FACT_VEHICLE_SAFETY`
* `DIM_YEAR`
* `DIM_MODEL`
* `DIM_SAFETY`

The screenshot below documents the implemented Power BI semantic model.

![Power BI Semantic Model](./screenshots/data-model.png)

> **Note:** The exact filename must match the file committed under
> `docs/screenshots/`. GitHub paths are case-sensitive.

---

# 14. Why the Model Is Not a Single Star

The overall model should not be described simply as a single star schema.

A single-star representation would imply one central fact surrounded by
its dimensions.

This project instead contains:

```text
              STAR 1
        FACT_USED_CAR
          /       \
         /         \
 DIM_YEAR         DIM_MODEL


              STAR 2
     FACT_VEHICLE_SAFETY
        /       |       \
       /        |        \
 DIM_YEAR   DIM_MODEL  DIM_SAFETY
```

The two stars share conformed dimensions.

Therefore, at the overall model level, the structure is better described
as a:

> **Fact constellation / galaxy schema**

This terminology is consistent with dimensional modelling literature
describing multiple star schemas connected through shared/conformed
dimensions.

---

# 15. Modelling Principles

The project follows these principles:

* Fact table grain is defined before analytical modelling.
* Different business processes are represented by separate fact tables.
* Shared dimensions are treated as conformed dimensions where their
  meaning and domain are consistent.
* Local dimensions remain specific to the business process where they
  are required.
* Facts are not artificially combined simply because they contain
  similar attributes.
* Unrelated datasets are not joined using artificial keys.
* Manufacturing features are treated as an ML feature matrix because
  their source semantics do not support the vehicle dimensional model.
* Power BI provides the semantic and reporting layer.
* Analytical relationships are implemented based on business meaning
  and source-supported keys.
* Measures from different fact tables should only be combined when their
  dimensional context and grain make the comparison analytically valid.

---

# 16. Summary

The Mercedes-Benz analytical model is a **fact constellation** consisting
of multiple subject-specific stars.

The primary structure is:

```text
                     FACT CONSTELLATION
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       USED VEHICLE STAR           SAFETY STAR
              │                           │
              ▼                           ▼
      FACT_USED_CAR              FACT_VEHICLE_SAFETY
          /      \                   /      |      \
         /        \                 /       |       \
        ▼          ▼               ▼        ▼        ▼
   DIM_YEAR    DIM_MODEL       DIM_YEAR DIM_MODEL DIM_SAFETY
        ▲          ▲               ▲        ▲
        └──────────┴───────────────┘────────┘
          CONFORMED DIMENSIONS

                    +
                    |
                    v

             MANUFACTURING ML
             Feature Matrix
                    |
                    v
             Random Forest
```

This structure preserves the distinct grains and business purposes of
the Used Vehicle and Vehicle Safety facts while allowing them to share
common vehicle dimensions.

The manufacturing dataset remains independent because it serves a
machine-learning use case rather than a shared vehicle analytics
process.
