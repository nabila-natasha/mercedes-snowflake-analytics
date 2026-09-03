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

Modeling approach:

    1. Naive mean baseline
    2. Hand-tuned Random Forest
    3. RandomizedSearchCV hyperparameter tuning
       using 5-fold cross-validation
    4. Final evaluation on an unseen test set

The objective is to demonstrate an end-to-end
data + ML platform rather than competition-grade modeling.
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
    r2_score,
)
from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
)
from sklearn.preprocessing import OneHotEncoder


# 1. SNOWFLAKE CONNECTION

def get_connection():
    """
    Create a connection to Snowflake.

    Credentials are supplied through environment variables.

    GitHub Actions:
        Values come from GitHub Secrets / Variables.

    Local development:
        Values are supplied through the local environment.
    """

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse="TRANSFORM_WH",
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="SILVER",
    )


# 2. LOAD SILVER DATA

def load_data():
    """
    Load the cleaned manufacturing dataset from SILVER.

    SILVER is the ML training source.
    ML outputs are written to GOLD.
    """

    conn = get_connection()

    try:

        query = f"""
        SELECT *
        FROM {os.environ["SNOWFLAKE_DATABASE"]}.SILVER.MANUFACTURING_CLEAN
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
    Calculate standard regression metrics.

    MAE:
        Average absolute prediction error.

    RMSE:
        Penalizes larger errors more heavily.

    R2:
        Measures the proportion of target variation
        explained by the model.
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
        f"{label:>30} | "
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

    print("=" * 80)
    print("MANUFACTURING TEST-TIME ML PIPELINE")
    print("=" * 80)


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
            include=["object", "string"] # keeps text/object data type columns
        )
        .columns
        .tolist()
    )


    numerical_columns = (
        X
        .select_dtypes(
            exclude=["object", "string"]  # keep non text/object (numbers) columns
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

    print()
    print("=" * 80)
    print("NAIVE BASELINE")
    print("=" * 80)


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


    baseline_train_metrics = evaluate_model(
        y_train,
        baseline_train_predictions,
        "Naive Baseline - Train"
    )


    baseline_test_metrics = evaluate_model(
        y_test,
        baseline_test_predictions,
        "Naive Baseline - Test"
    )


    # 6. HAND-TUNED RANDOM FOREST
    # Added max_depth=15 and min_samples_leaf=3.
    # Goal: Improve generalization to unseen manufacturing configurations.

    print()
    print("=" * 80)
    print("HAND-TUNED RANDOM FOREST")
    print("=" * 80)

    hand_tuned_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,           # prevents trees from becoming excessively deep
        min_samples_leaf=3,     # prevents the model from creating extremely specific rules around tiny groups of records
        random_state=42,
        n_jobs=-1
    )
    
    hand_tuned_model.fit(
        X_train_processed,
        y_train
    )

    # Predictions on TRAINING data
    hand_tuned_train_predictions = (
        hand_tuned_model.predict(
            X_train_processed
        )
    )

    # Predictions on UNSEEN TEST data
    hand_tuned_test_predictions = (
        hand_tuned_model.predict(
            X_test_processed
        )
    )


    hand_tuned_train_metrics = evaluate_model(
        y_train,
        hand_tuned_train_predictions,
        "Hand-Tuned RF - Train"
    )


    hand_tuned_test_metrics = evaluate_model(
        y_test,
        hand_tuned_test_predictions,
        "Hand-Tuned RF - Test"
    )

    
    # 7. HYPERPARAMETER TUNING

    print()
    print("=" * 80)
    print("RANDOMIZED HYPERPARAMETER SEARCH")
    print("=" * 80)


    # Parameter distributions to explore.
    #
    # n_estimators:
    #     Number of trees in the forest.
    #
    # max_depth:
    #     Maximum depth of each decision tree.
    #
    # min_samples_leaf:
    #     Minimum observations required in a leaf.
    #
    # max_features:
    #     Number/proportion of features considered
    #     when splitting a tree.

    param_distributions = {

        "n_estimators": [
            100,
            200,
            300,
            400
        ],

        "max_depth": [
            5,
            8,
            10,
            12,
            15,
            None
        ],

        "min_samples_leaf": [
            1,
            2,
            3,
            5,
            8
        ],

        "max_features": [
            "sqrt",
            "log2",
            0.5
        ],
    }


    search = RandomizedSearchCV(
        estimator=RandomForestRegressor(
            random_state=42,
            n_jobs=-1
        ),
        param_distributions=param_distributions,
        n_iter=15,
        cv=5,
        scoring="neg_mean_absolute_error",
        random_state=42,
        n_jobs=-1,
        verbose=1,
    )

    search.fit(
        X_train_processed,
        y_train
    )


    # BEST PARAMETERS

    print()
    print("=" * 80)
    print("BEST HYPERPARAMETERS")
    print("=" * 80)


    print(
        search.best_params_
    )


    print()
    print(
        f"Best CV MAE: "
        f"{-search.best_score_:.3f}"
    )


    # Best estimator selected by cross-validation

    tuned_model = search.best_estimator_


    # 8. FINAL TUNED MODEL PREDICTIONS

    tuned_train_predictions = (
        tuned_model.predict(
            X_train_processed
        )
    )


    tuned_test_predictions = (
        tuned_model.predict(
            X_test_processed
        )
    )


    # 9. FINAL MODEL PERFORMANCE

    print()
    print("=" * 80)
    print("FINAL MODEL PERFORMANCE")
    print("=" * 80)


    tuned_train_metrics = evaluate_model(
        y_train,
        tuned_train_predictions,
        "Tuned RF - Train"
    )


    tuned_test_metrics = evaluate_model(
        y_test,
        tuned_test_predictions,
        "Tuned RF - Test"
    )


    # 10. OVERFITTING CHECK
    # Compare train and test R2 to monitor potential overfitting.
    # A large gap may indicate that the model is fitting the training
    # data substantially better than unseen data.

    hand_tuned_r2_gap = (
        hand_tuned_train_metrics["r2"]
        - hand_tuned_test_metrics["r2"]
    )


    tuned_r2_gap = (
        tuned_train_metrics["r2"]
        - tuned_test_metrics["r2"]
    )


    print()
    print("=" * 80)
    print("OVERFITTING CHECK")
    print("=" * 80)


    print(
        f"Hand-Tuned RF Train/Test R2 gap: "
        f"{hand_tuned_r2_gap:.3f}"
    )


    print(
        f"Tuned RF Train/Test R2 gap: "
        f"{tuned_r2_gap:.3f}"
    )


    if tuned_r2_gap > 0.20:

        print(
            "WARNING: Tuned model has a large "
            "train/test R2 gap. Potential overfitting."
        )

    else:

        print(
            "Tuned model train/test R2 gap is "
            "within the selected monitoring threshold."
        )


    # 11. FEATURE IMPORTANCE
    # One-hot encoding changes the feature names.
    # get_feature_names_out() gives us the actual names
    # used by the trained model.

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    importances = pd.DataFrame({
        "FEATURE": feature_names,
        "IMPORTANCE": tuned_model.feature_importances_,
    }).reset_index(drop=True)


    importances = (
        importances
        .sort_values(
            "IMPORTANCE",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )


    print()
    print("=" * 80)
    print("TOP 10 FEATURES - TUNED MODEL")
    print("=" * 80)


    print(
        importances.to_string(
            index=False
        )
    )


    # 12. CREATE PREDICTION DATASET

    predictions_df = pd.DataFrame({

        "TEST_ID":
            ids_test.values,

        "ACTUAL_TEST_TIME_SECONDS":
            y_test.values,

        "PREDICTED_TEST_TIME_SECONDS":
            tuned_test_predictions,

        "HAND_TUNED_PREDICTED_TEST_TIME_SECONDS":
            hand_tuned_test_predictions,

        "BASELINE_PREDICTED_TEST_TIME_SECONDS":
            baseline_test_predictions,

    }).reset_index(drop=True)


    # 13. CREATE MODEL METRICS DATASET

    metrics_df = pd.DataFrame([

        {
            "MODEL_NAME": "Naive Baseline",
            "DATASET": "TRAIN",
            "MAE": baseline_train_metrics["mae"],
            "RMSE": baseline_train_metrics["rmse"],
            "R2": baseline_train_metrics["r2"],
        },
        {
            "MODEL_NAME": "Naive Baseline",
            "DATASET": "TEST",
            "MAE": baseline_test_metrics["mae"],
            "RMSE": baseline_test_metrics["rmse"],
            "R2": baseline_test_metrics["r2"],
        },
        {
            "MODEL_NAME": "Random Forest - Hand-Tuned",
            "DATASET": "TRAIN",
            "MAE": hand_tuned_train_metrics["mae"],
            "RMSE": hand_tuned_train_metrics["rmse"],
            "R2": hand_tuned_train_metrics["r2"],
        },
        {
            "MODEL_NAME": "Random Forest - Hand-Tuned",
            "DATASET": "TEST",
            "MAE": hand_tuned_test_metrics["mae"],
            "RMSE": hand_tuned_test_metrics["rmse"],
            "R2": hand_tuned_test_metrics["r2"],
        },
        {
            "MODEL_NAME": "Random Forest - Tuned",
            "DATASET": "TRAIN",
            "MAE": tuned_train_metrics["mae"],
            "RMSE": tuned_train_metrics["rmse"],
            "R2": tuned_train_metrics["r2"],
        },
        {
            "MODEL_NAME": "Random Forest - Tuned",
            "DATASET": "TEST",
            "MAE": tuned_test_metrics["mae"],
            "RMSE": tuned_test_metrics["rmse"],
            "R2": tuned_test_metrics["r2"],
        },
    ]).reset_index(drop=True)


    print()
    print("=" * 80)
    print("MODEL METRICS")
    print("=" * 80)

    print(
        metrics_df.to_string(
            index=False
        )
    )


    # 14. WRITE ML RESULTS TO GOLD

    print()
    print("=" * 80)
    print("WRITING ML RESULTS TO GOLD")
    print("=" * 80)

    conn = get_connection()


    try:

        # Prediction results
        predictions_df = predictions_df.reset_index(drop=True)
        predictions_df.index = pd.RangeIndex(start=0, stop=len(predictions_df))
        
        write_pandas(
            conn,
            predictions_df,
            "MANUFACTURING_PREDICTIONS",
            schema="GOLD",
            auto_create_table=True,
            overwrite=True,
        )


        # Feature importance
        importances = importances.reset_index(drop=True)
        importances.index = pd.RangeIndex(start=0, stop=len(importances))
        
        write_pandas(
            conn,
            importances,
            "MANUFACTURING_FEATURE_IMPORTANCE",
            schema="GOLD",
            auto_create_table=True,
            overwrite=True,
        )


        # Model metrics
        metrics_df = metrics_df.reset_index(drop=True)
        metrics_df.index = pd.RangeIndex(start=0, stop=len(metrics_df))
        
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


    # 15. FINAL SUMMARY

    print()
    print("=" * 80)
    print("ML PIPELINE COMPLETED")
    print("=" * 80)


    print("Best hyperparameters:")
    print(search.best_params_)
    print()
    print(
        f"Best cross-validation MAE: "
        f"{-search.best_score_:.3f}"
    )

    print()
    print("Created:")
    print("  GOLD.MANUFACTURING_PREDICTIONS")
    print("  GOLD.MANUFACTURING_FEATURE_IMPORTANCE")
    print("  GOLD.MANUFACTURING_MODEL_METRICS")


# 16. PYTHON ENTRY POINT

if __name__ == "__main__":
    main()
