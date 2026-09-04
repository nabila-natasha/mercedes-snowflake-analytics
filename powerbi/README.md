# Power BI Analytics

This directory contains the Power BI analytical reporting assets.

Power BI consumes analytical data from the Snowflake platform and
provides the business-facing reporting layer.

---

# 1. Used Car Analytics

The Used Car dashboard provides market-oriented analysis of
Mercedes-Benz used vehicles.

### Key analysis
- Total vehicles
- Average price
- Average MPG
- Average mileage
- Price by year
- Vehicle count by model
- Price versus mileage
- Average price by fuel type
- Median price by fuel type

### Analytical objective

Understand relationships between vehicle age, mileage, model,
fuel type and resale price.

---

# 2. Manufacturing ML Performance

The Manufacturing dashboard communicates the performance of the
manufacturing test-time prediction model.

### Key metrics
- Test MAE
- Test R²
- MAE improvement versus baseline
- Train/test performance

### Analytical visuals
- Actual vs Predicted Test Time
- Residual classification
- Feature importance
- Baseline vs model comparison

### Final model
Tuned Random Forest regression.

### Final test performance
- Test MAE: 5.30 seconds
- Test R²: 0.59
- MAE improvement: 47.7%

---

# 3. Vehicle Safety Analytics

The Vehicle Safety dashboard provides:
- Vehicle configurations
- Electronic Stability Control adoption
- Complaints
- Recalls
- Investigations
- Crash ratings by model year
- Recalls by model year
- Complaints vs recalls
- Safety technology adoption

---

# 4. Semantic Model

Power BI provides the semantic/reporting layer between the Snowflake
analytical data and dashboard users.

The model contains the relationships and measures required for the
individual analytical domains.

The model screenshot is documented in:

`docs/screenshots/data-model.png`

---

# 5. Dashboard Design

The dashboards follow an executive-to-detail structure:

```text
KPI
 |
 v
Trend
 |
 v
Comparison
 |
 v
Detailed Analysis
```
This allows users to move from high-level indicators to detailed patterns.

---

# 6. Dashboard Evidence

Dashboard screenshots are stored in:
`docs/screenshots/`

The screenshots are provided as portfolio evidence of the final analytical outputs.
