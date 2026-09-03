import os
import sys

import snowflake.connector


# 1. SNOWFLAKE CONNECTION

def get_connection():

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="GOLD"
    )


# 2. HELPER FUNCTION

def print_check(label, value, passed=True):

    status = "PASS" if passed else "FAIL"

    print(
        f"{status:<6} | "
        f"{label:<45} | "
        f"{value}"
    )


# 3. MAIN VALIDATION

def main():

    database = os.environ["SNOWFLAKE_DATABASE"]

    print("=" * 90)
    print("MANUFACTURING ML DATA QUALITY & PERFORMANCE TEST")
    print("=" * 90)

    conn = get_connection()
    cursor = conn.cursor()

    overall_success = True

    try:

        # TEST 1 — PREDICTION TABLE


        cursor.execute(f"""
            SELECT
                COUNT(*) AS PREDICTION_ROWS,
                COUNT_IF(
                    PREDICTED_TEST_TIME_SECONDS IS NULL
                ) AS NULL_PREDICTIONS,
                COUNT_IF(
                    ACTUAL_TEST_TIME_SECONDS IS NULL
                ) AS NULL_ACTUALS
            FROM {database}.GOLD.MANUFACTURING_PREDICTIONS;
        """)

        prediction_rows, null_predictions, null_actuals = (
            cursor.fetchone()
        )

        print("\n" + "-" * 90)
        print("PREDICTION TABLE")
        print("-" * 90)

        print_check(
            "Prediction rows",
            prediction_rows,
            prediction_rows > 0
        )

        print_check(
            "NULL predictions",
            null_predictions,
            null_predictions == 0
        )

        print_check(
            "NULL actual test time",
            null_actuals,
            null_actuals == 0
        )

        if prediction_rows == 0:
            overall_success = False

        if null_predictions > 0:
            overall_success = False

        if null_actuals > 0:
            overall_success = False


        
        # TEST 2 — COMPARE AGAINST SILVER DATASET

        cursor.execute(f"""
            SELECT COUNT(*)
            FROM {database}.SILVER.MANUFACTURING_CLEAN;
        """)

        silver_rows = cursor.fetchone()[0]

        print_check(
            "Silver manufacturing rows",
            silver_rows,
            silver_rows > 0
        )

        if silver_rows == 0:
            overall_success = False


        # TEST 3 — FEATURE IMPORTANCE

        cursor.execute(f"""
            SELECT
                COUNT(*) AS FEATURE_ROWS,
                COUNT_IF(IMPORTANCE IS NULL)
                    AS NULL_IMPORTANCE
            FROM {database}.GOLD.MANUFACTURING_FEATURE_IMPORTANCE;
        """)

        feature_rows, null_importance = cursor.fetchone()

        print("\n" + "-" * 90)
        print("FEATURE IMPORTANCE")
        print("-" * 90)

        print_check(
            "Feature importance rows",
            feature_rows,
            feature_rows == 10
        )

        print_check(
            "NULL feature importance values",
            null_importance,
            null_importance == 0
        )

        if feature_rows != 10:
            overall_success = False

        if null_importance > 0:
            overall_success = False


       
        # TEST 4 — MODEL METRICS

        cursor.execute(f"""
            SELECT
                COUNT(*) AS METRIC_ROWS,
                COUNT_IF(
                    R2 IS NULL
                    OR R2 < -1
                    OR R2 > 1
                ) AS INVALID_R2,
                COUNT_IF(
                    MAE IS NULL
                    OR RMSE IS NULL
                    OR MAE < 0
                    OR RMSE < 0
                ) AS INVALID_ERROR_METRICS
            FROM {database}.GOLD.MANUFACTURING_MODEL_METRICS;
        """)

        metric_rows, invalid_r2, invalid_error_metrics = (
            cursor.fetchone()
        )

        print("\n" + "-" * 90)
        print("MODEL METRICS")
        print("-" * 90)

        print_check(
            "Model metric rows",
            metric_rows,
            metric_rows == 6
        )

        print_check(
            "Invalid R2 values",
            invalid_r2,
            invalid_r2 == 0
        )

        print_check(
            "Invalid MAE/RMSE values",
            invalid_error_metrics,
            invalid_error_metrics == 0
        )

        if metric_rows != 6:
            overall_success = False

        if invalid_r2 > 0:
            overall_success = False

        if invalid_error_metrics > 0:
            overall_success = False


        
        # TEST 5 — DISPLAY MODEL PERFORMANCE

        print("\n" + "-" * 90)
        print("MODEL PERFORMANCE")
        print("-" * 90)

        cursor.execute(f"""
            SELECT
                MODEL_NAME,
                MAE,
                RMSE,
                R2
            FROM {database}.GOLD.MANUFACTURING_MODEL_METRICS
            ORDER BY MODEL_NAME;
        """)

        metrics = cursor.fetchall()

        print(
            f"{'MODEL':<25}"
            f"{'MAE':>12}"
            f"{'RMSE':>12}"
            f"{'R2':>12}"
        )

        print("-" * 65)

        for model_name, mae, rmse, r2 in metrics:

            print(
                f"{model_name:<25}"
                f"{mae:>12.3f}"
                f"{rmse:>12.3f}"
                f"{r2:>12.3f}"
            )


        
        # TEST 6 — CHECK TUNED RANDOM FOREST PERFORMANCE

        cursor.execute(f"""
            SELECT
                MAX(
                    CASE
                        WHEN MODEL_NAME = 'Random Forest - Tuned'
                        AND DATASET = 'TEST'
                        THEN R2
                    END
                ) AS TUNED_RF_R2,

                MAX(
                    CASE
                        WHEN MODEL_NAME = 'Naive Baseline'
                        AND DATASET = 'TEST'
                        THEN R2
                    END
                ) AS BASELINE_R2,

                MAX(
                    CASE
                        WHEN MODEL_NAME = 'Random Forest - Tuned'
                        AND DATASET = 'TRAIN'
                        THEN R2
                    END
                ) -
                MAX(
                    CASE
                        WHEN MODEL_NAME = 'Random Forest - Tuned'
                        AND DATASET = 'TEST'
                        THEN R2
                    END
                ) AS R2_GAP

            FROM {database}.GOLD.MANUFACTURING_MODEL_METRICS;
        """)

        tuned_rf_r2, baseline_r2, r2_gap = cursor.fetchone()


        # Convert Snowflake numeric values to Python floats

        if tuned_rf_r2 is not None:
            tuned_rf_r2 = float(tuned_rf_r2)

        if baseline_r2 is not None:
            baseline_r2 = float(baseline_r2)

        if r2_gap is not None:
            r2_gap = float(r2_gap)


        print("\n" + "-" * 90)
        print("MODEL COMPARISON")
        print("-" * 90)


        # 1. Check Tuned Random Forest Test R2 Exists

        if tuned_rf_r2 is not None:

            print_check(
                "Tuned Random Forest Test R2",
                f"{tuned_rf_r2:.3f}",
                True
            )

        else:

            print_check(
                "Tuned Random Forest Test R2",
                "NOT FOUND",
                False
            )

            overall_success = False


        # 2. Check Baseline Test R2 Exists

        if baseline_r2 is not None:

            print_check(
                "Baseline Test R2",
                f"{baseline_r2:.3f}",
                True
            )

        else:

            print_check(
                "Baseline Test R2",
                "NOT FOUND",
                False
            )

            overall_success = False


        # 3. Compare Tuned Random Forest Against Baseline
        # This is informational rather than a deployment gate.
        
        if (
            tuned_rf_r2 is not None
            and baseline_r2 is not None
        ):
        
            model_beats_baseline = (
                tuned_rf_r2 > baseline_r2
            )
        
            print_check(
                "Tuned Random Forest beats baseline",
                f"{tuned_rf_r2:.3f} > {baseline_r2:.3f}",
                model_beats_baseline
            )

        # Informational only.
        # Do not fail the production deployment if tuning
        # does not beat the baseline.


        # 4. Check Tuned Model Train/Test R2 Gap

        MAX_R2_GAP = 0.20

        if r2_gap is not None:

            print_check(
                "Tuned Model Train/Test R2 Gap",
                f"{r2_gap:.3f} "
                f"(threshold <= {MAX_R2_GAP:.2f})",
                r2_gap <= MAX_R2_GAP
            )

            if r2_gap > MAX_R2_GAP:

                print(
                    "  WARNING: Tuned model Train/Test R2 gap "
                    "exceeds the selected threshold."
                )

                print(
                    "  This indicates potential overfitting "
                    "and requires model review."
                )

                overall_success = False

        else:

            print_check(
                "Tuned Model Train/Test R2 Gap",
                "NOT FOUND",
                False
            )

            overall_success = False


        # TEST 7 — CHECK PREDICTION RANGE

        cursor.execute(f"""
            SELECT
                MIN(PREDICTED_TEST_TIME_SECONDS),
                MAX(PREDICTED_TEST_TIME_SECONDS),
                AVG(PREDICTED_TEST_TIME_SECONDS)
            FROM {database}.GOLD.MANUFACTURING_PREDICTIONS;
        """)

        min_prediction, max_prediction, avg_prediction = (
            cursor.fetchone()
        )

        print("\n" + "-" * 90)
        print("PREDICTION DISTRIBUTION")
        print("-" * 90)

        if min_prediction is not None:

            print_check(
                "Minimum prediction",
                f"{min_prediction:.2f}",
                min_prediction >= 0
            )
        
            if min_prediction < 0:
                overall_success = False
        
        else:
        
            print_check(
                "Minimum prediction",
                "NOT FOUND",
                False
            )
        
            overall_success = False
        
        
        if max_prediction is not None:
        
            print_check(
                "Maximum prediction",
                f"{max_prediction:.2f}",
                max_prediction > 0
            )
        
            if max_prediction <= 0:
                overall_success = False
        
        else:
        
            print_check(
                "Maximum prediction",
                "NOT FOUND",
                False
            )
        
            overall_success = False
        
        
        if avg_prediction is not None:
        
            print_check(
                "Average prediction",
                f"{avg_prediction:.2f}",
                avg_prediction > 0
            )
        
            if avg_prediction <= 0:
                overall_success = False
        
        else:
        
            print_check(
                "Average prediction",
                "NOT FOUND",
                False
            )
        
            overall_success = False
        
            
        # TEST 8 — DISPLAY TOP FEATURES
        
        print("\n" + "-" * 90)
        print("TOP 10 FEATURES")
        print("-" * 90)

        cursor.execute(f"""
            SELECT
                FEATURE,
                IMPORTANCE
            FROM {database}.GOLD.MANUFACTURING_FEATURE_IMPORTANCE
            ORDER BY IMPORTANCE DESC
            LIMIT 10;
        """)

        features = cursor.fetchall()

        print(
            f"{'RANK':<8}"
            f"{'FEATURE':<30}"
            f"{'IMPORTANCE':>15}"
        )

        print("-" * 55)

        for rank, (feature, importance) in enumerate(
            features,
            start=1
        ):

            print(
                f"{rank:<8}"
                f"{feature:<30}"
                f"{importance:>15.6f}"
            )


    
        # FINAL RESULT
        
        print("\n" + "=" * 90)

        if overall_success:

            print("MANUFACTURING ML VALIDATION: SUCCESS")

        else:

            print("MANUFACTURING ML VALIDATION: FAILED")

            sys.exit(1)

        print("=" * 90)


    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
