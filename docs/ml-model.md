# Manufacturing Machine Learning

## 1. Objective

The manufacturing machine learning component predicts vehicle
manufacturing test time.

The objective is to determine whether a machine learning model can
provide a meaningful improvement over a simple baseline.

---

# 2. Dataset

The manufacturing dataset contains:

- 4,209 observations
- 378 columns
- `ID`
- Target variable `y`
- Manufacturing features `X0`–`X385`

The source contains anonymised feature names.

No business meaning is assigned to individual X-columns without
supporting source documentation.

---

# 3. Modelling Workflow

```text
Manufacturing Dataset
        |
        v
Data Preparation
        |
        v
Train / Test Split
        |
        v
Naive Baseline
        |
        v
Random Forest
        |
        v
Hyperparameter Tuning
        |
        v
Final Tuned Model
        |
        +------> Feature Importance
        |
        +------> Residual Analysis
```

# 4. Baseline

A naive baseline was established before evaluating the machine learning
model.

| Dataset | MAE |
|---|---|
| Train | 10.08s |
| Test | 10.14s |

The baseline provides a reference point for measuring whether the
machine learning model provides meaningful improvement.

---

# 5. Model

The final model is a tuned Random Forest Regression model.

The workflow includes:
- Initial Random Forest model
- Hand tuning
- Hyperparameter search
- Final model selection

---

# 6. Final Performance

| Metric | Result |
|---|---:|
| Tuned Model Train MAE | 5.11 s |
| Tuned Model Test MAE | 5.30 s |
| Test R² | 0.59 |
| MAE Improvement vs Baseline | 47.7% |
| Train/Test R² Gap | 0.013 |

The final model reduced test MAE from 10.14 seconds to 5.30 seconds.

This represents a 47.7% reduction in Mean Absolute Error (MAE) compared
with Naive Baseline.

---

# 7. Train vs Test Performance

The final model produced:  
**Train MAE = 5.11 s**  
**Test MAE  = 5.30 s**

The relatively small difference suggests that the final model does not
have a large train/test performance gap.

The result should not be interpreted as proof that the model will
generalize to future production data without additional validation.

---

# 8. Feature Importance

Feature importance is used to identify features that contribute most to
the Random Forest's predictive performance.

The leading features in the final dashboard include:
- X314
- X261
- X127
- X315
- X263

Feature importance represents model-level predictive contribution and
should not be interpreted as causal influence.

---

# 9. Residual Analysis

Residuals are calculated as:  
**Residual = Actual Test Time - Predicted Test Time**

The dashboard uses three categories:

| Residual | Category |
|---|---:|
| > +10 s | Under-predicted |
| -10 to +10 s | Close to Actual |
| < -10 s | Over-predicted |

A prediction is classified as close to actual when the absolute residual
is no greater than 10 seconds.

The ±10-second threshold is a practical analytical tolerance selected
for dashboard interpretation.

---

# 10. Model Limitations

The model's performance depends on the available dataset.

The anonymised features make direct business interpretation difficult.

Feature importance identifies predictive contribution within the model
but does not establish causality.

Additional validation would be required before applying the model to
operational manufacturing decisions.

---

# 11. Future Improvements

Potential improvements include:
- Cross-validation
- SHAP-based model explainability
- Model monitoring
- Automated retraining
- Drift detection
- Additional manufacturing features
- Production inference monitoring
    
