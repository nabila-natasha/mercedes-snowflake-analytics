"""
Mercedes-Benz Vehicle Analytics
Manufacturing ML Pipeline

Purpose:
    Train a machine-learning model to predict manufacturing
    test time (y) using configuration variables from the
    Silver manufacturing dataset.

Architecture:

    RAW.MANUFACTURING_RAW
            |
            v
    SILVER.MANUFACTURING_CLEAN
            |
            v
    Python ML pipeline
            |
            +--> GOLD.MANUFACTURING_PREDICTIONS
            |
            +--> GOLD.MANUFACTURING_FEATURE_IMPORTANCE
            |
            +--> GOLD.MANUFACTURING_MODEL_METRICS

This script intentionally uses a simple Random Forest model.
The objective is to demonstrate an end-to-end data + ML platform,
not to build a competition-grade model.
"""

import os

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


# 1. SNOWFLAKE CONNECTION

def get_connection():
    """
    Create a connection to Snowflake.

    The credential are supplied through environment variables.
    In GitHub Actions these values come from GitHub Secrets/Variables.

    We read from the SILVER layer and write the ML outputs
    into the GOLD layers.
    """

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse="TRANSFORM_WH",
        database="MERCEDES_DEV",
        schema="SILVER",
    )


# 2. LOAD SILVER DATA

def load_data():
    """
    Load the cleaned manufacturing dataset from SILVER.

    Important architectural point:

    We are NOT creating another copy of the entire 
    manufacturing dataset in GOLD.

    SILVER is our ML training source.
    """
    conn = get_connection()

    try:

        query = """
        SELECT *
        FROM MERCEDES_DEV.SILVER.MANUFACTURING_CLEAN
        """

        cursor = conn.cursor()

        try:
            cursor.execute(query)

            # Get column names returned by Snowflake
            columns = [
                column[0]
                for column in cursor.description
            ]

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert Snowflake result into pandas DataFrame

            df = pd.DataFrame(
                rows,
                columns=columns
            )


        finally:
            cursor.close()

    finally:
        conn.close()

    return df


# 3. MODEL EVALUATION

def evaluate_model(y_true, y_pred, label):
    """
    Calculate three standard regression metrics.

    MAE:
        Average absolute prediction error.

    RMSE:
        Penalizes larger errors more heavily.

    R2:
        Measures how much variation in the target
        is explained by the model.

    The same function is used for both the baseline
    and Random Forest so the comparison is fair.
    """

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    rmse = mean_squared_error(
        y_true,
        y_pred
    ) ** 0.5

    r2 = r2_score(
        y_true,
        y_pred
    )

    print(
        f"{label:>20} | "
        f"MAE = {mae:7.3f} | "
        f"RMSE = {rmse:7.3f} | "
        f"R2 = {r2:6.3f}"
    )

    return {
        "label": label,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    }


# 4. MAIN MACHINE LEARNING PIPELINE

def main():

    print("=" * 70)
    print("MANUFACTURING TEST-TIME ML PIPELINE")
    print("=" * 70)


    # LOAD DATA

    df = load_data()

    print(
        f"Dataset shape: {df.shape}"
    )


    # BASIC VALIDATION

    if "y" not in df.columns:

        raise ValueError(
            "Target column y was not found."
        )


    if "ID" not in df.columns:

        raise ValueError(
            "ID column was not found."
        )


    # REMOVE ROWS WITH MISSING TARGET

    df = df.dropna(
        subset=["y"]
    )


    # SEPARATE ID, FEATURES AND TARGET

    # We retain it separately so that predictions can later
    # be linked back to the original record.

    row_ids = df["ID"]

    # y is the target variable:
    # manufacturing test time in seconds.

    y = df["y"]

    # Everything except ID and Y becomes a model feature.

    X = df.drop(
        columns=[
            "ID",
            "y"
        ]
    )

    print(
        f"Training rows: {len(X):,}"
    )

    print(
        f"Feature count: {X.shape[1]:,}"
    )


    # IDENTIFY CATEGORICAL / NUMERICAL FEATURES

    categorical_columns = (
        X
        .select_dtypes(
            include=["object", "string"]    # keeps text/object data type columns
        )
        .columns
        .tolist()
    )

    numerical_columns = (
        X
        .select_dtypes(
            exclude=["object", "string"]    # keep non text/object (numbers) columns
        )
        .columns
        .tolist()
    )

    print(
        f"Categorical features: "
        f"{len(categorical_columns)}"
    )

    print(
        f"Numerical features: "
        f"{len(numerical_columns)}"
    )


    # PREPROCESSING
    # Machine-learning algorithms cannot directly understand
    # strings such as:
    #   "A"
    #   "B"

    # OneHotEncoder converts categorical values into numerical
    # indicator columns.
    
    # handle_unknown="ignore" prevents the model from failing
    # when the test dataset contains a category that was not
    # present in the training dataset.

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_columns,
            ),
            (
                "numerical",
                "passthrough",
                numerical_columns,
            ),
        ]
    )


    # TRAIN / TEST SPLIT
    # 80% = training
    # 20% = testing
    # random_state=42 makes the experiment reproducible.

    (
        X_train,
        X_test,
        y_train,
        y_test,
        ids_train,
        ids_test,
    ) = train_test_split(X, y, row_ids, test_size=0.20, random_state=42)


     # FIT PREPROCESSOR ONLY ON TRAINING DATA

    X_train_processed = (
        preprocessor.fit_transform(
            X_train
        )
    )

    X_test_processed = (
        preprocessor.transform(
            X_test
        )
    )


    # 5. NAIVE BASELINE
    # The baseline simply predicts the average training Y
    # for every test record.

    # This gives us a reference point.
    
    # If Random Forest cannot beat this baseline, the ML
    # model is not providing useful predictive value.


    baseline = DummyRegressor(
        strategy="mean"
    )

    baseline.fit(
        X_train,
        y_train
    )

    baseline_train_predictions = (
        baseline.predict(X_train)
    )

    baseline_test_predictions = (
        baseline.predict(X_test)
    )


    # 6. RANDOM FOREST MODEL

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train_processed,
        y_train
    )


    # Predictions on TRAINING data

    train_predictions = (
        model.predict(
            X_train_processed
        )
    )


    # Predictions on UNSEEN TEST data

    test_predictions = (
        model.predict(
            X_test_processed
        )
    )
        

    # 7. MODEL PERFORMANCE

    print()
    print("=" * 70)
    print("MODEL PERFORMANCE")
    print("=" * 70)


    baseline_metrics = evaluate_model(
        y_train,
        baseline_train_predictions,
        "Baseline - Train"
    )


    baseline_test_metrics = evaluate_model(
        y_test,
        baseline_test_predictions,
        "Baseline - Test"
    )


    train_metrics = evaluate_model(
        y_train,
        train_predictions,
        "Random Forest - Train"
    )


    test_metrics = evaluate_model(
        y_test,
        test_predictions,
        "Random Forest - Test"
    )


    # 8. OVERFITTING CHECK
    # Example:
    # Train R2 = 0.95
    # Test  R2 = 0.55
    # Large gap -> model may be overfitting.

    r2_gap = (
        train_metrics["r2"]
        - test_metrics["r2"]
    )


    print()
    print(
        f"Train/Test R2 gap: "
        f"{r2_gap:.3f}"
    )


    if r2_gap > 0.20:

        print(
            "WARNING: Large train/test R2 gap. "
            "Potential overfitting."
        )

    else:

        print(
            "Train/test R2 gap is within "
            "the selected monitoring threshold."
        )


    # 9. FEATURE IMPORTANCE
    # One-hot encoding changes the feature names.

    # get_feature_names_out() gives us the actual names
    # used by the trained model.

    feature_names =(
        preprocessor
        .get_feature_names_out()
    )


    importances = pd.DataFrame({
        "FEATURE": feature_names,
        "IMPORTANCE": model.feature_importances_,
    }).reset_index(drop=True)


    importances = (
        importances
        .sort_values(
            "IMPORTANCE",
            ascending=False
        )
        .head(10)
    )


    print()
    print("=" * 70)
    print("TOP 10 FEATURES")
    print("=" * 70)

    print(importances.to_string(index=False))


    # 10. CREATE PREDICTION DATASET

    predictions_df = pd.DataFrame({

        "TEST_ID": ids_test.values,
        "ACTUAL_TEST_TIME_SECONDS": y_test.values,
        "PREDICTED_TEST_TIME_SECONDS": test_predictions,
        "BASELINE_PREDICTED_TEST_TIME_SECONDS": baseline_test_predictions,
    }).reset_index(drop=True)


    # 11. CREATE MODEL METRICS DATASET

    metrics_df = pd.DataFrame([
        {
            "MODEL_NAME": "Naive Baseline",
            "DATASET": "TEST",
            "MAE": baseline_test_metrics["mae"],
            "RMSE": baseline_test_metrics["rmse"],
            "R2": baseline_test_metrics["r2"]
        },

        {
            "MODEL_NAME": "Random Forest",
            "DATASET": "TRAIN",
            "MAE": train_metrics["mae"],
            "RMSE": train_metrics["rmse"],
            "R2": train_metrics["r2"]
        },

        {
            "MODEL_NAME":  "Random Forest",
            "DATASET": "TEST",
            "MAE": test_metrics["mae"],
            "RMSE": test_metrics["rmse"],
            "R2": test_metrics["r2"]
        }
    ]).reset_index(drop=True)


    # 12. WRITE ML RESULTS TO GOLD

    print()
    print("=" * 70)
    print("WRITING ML RESULTS TO GOLD")
    print("=" * 70)


    conn = get_connection()


    try:

        # Prediction results
        write_pandas(
            conn,
            predictions_df,
            "MANUFACTURING_PREDICTIONS",
            schema="GOLD",
            auto_create_table=True,
            overwrite=True,
        )


        # Feature importance
        write_pandas(
            conn,
            importances,
            "MANUFACTURING_FEATURE_IMPORTANCE",
            schema="GOLD",
            auto_create_table=True,
            overwrite=True,
        )
    

        # Model metrics
        write_pandas(
            conn,
            metrics_df,
            "MANUFACTURING_MODEL_METRICS",
            schema="GOLD",
            auto_create_table=True,
            overwrite=True,
        )
    
    
    finally:
    
        conn.close()


    print()
    print("=" * 70)
    print("ML PIPELINE COMPLETED")
    print("=" * 70)

    print(
        "Created:"
    )

    print(
        "  GOLD.MANUFACTURING_PREDICTIONS"
    )

    print(
        "  GOLD.MANUFACTURING_FEATURE_IMPORTANCE"
    )

    print(
        "  GOLD.MANUFACTURING_MODEL_METRICS"
    )



# 13. PYTHON ENTRY POINT

if __name__ == "__main__":
    main()