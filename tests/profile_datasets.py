from pathlib import Path
import argparse
import pandas as pd

# 1. DIRECTORIES

DATA_DIR = Path("data/raw")
FIXTURE_DIR = Path("tests/fixtures")


# 2. DEFINE A FUNCTION TO PROFILE ONE DATASET

def profile_dataset(file_path):

    file_path = Path(file_path)

    print("\n" + "=" * 70)
    print(f"PROFILE: {file_path}")
    print("=" * 70)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    # LOAD CSV INTO pandas DATAFRAME

    df = pd.read_csv(file_path)


    # BASIC SIZE (NUMBER OF ROWS, NUMBER OF COLUMNS)

    print("\n1. DATASET SIZE")
    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]:,}")


    # COLUMN NAMES

    print("\n2. COLUMN NAMES")

    for column in df.columns:
        print(f" - {column}")


    # DATA TYPES

    print("\n3. DATA TYPES")
    print(df.dtypes)


    # MISSING VALUES

    print("\n4. MISSING VALUES")

    missing = df.isna().sum()

    missing_summary = pd.DataFrame({
        "missing_count": missing,
        "missing_percentage": (missing / len(df) * 100).round(2)
    })

    print(f"{missing_summary}\n")

    print(
        missing_summary[
            missing_summary["missing_count"] > 0
        ]
    )


    # DUPLICATE ROWS

    print("\n5. DUPLICATES")

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows: {duplicate_count:,}")


    # NUMERIC SUMMARY

    print("\n6. NUMERIC SUMMARY")

    print(df.describe().transpose())


    # FIRST FIVE RECORDS

    print("\n7. SAMPLE RECORDS")

    print(df.head())


# 3. RUN PROFILING FOR BOTH DATASETS

def main():

    parser = argparse.ArgumentParser(
        description="Profile Mercedes project datasets"
    )

    parser.add_argument(
        "--real",
        action="store_true",
        help="Profile real project datasets"
    )

    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Profile CI test fixture datasets"
    )

    args = parser.parse_args()


    # REAL DATASETS

    if args.real:

        real_datasets = [
            DATA_DIR / "mercedes.csv",
            DATA_DIR / "train.csv"
        ]

        for dataset in real_datasets:
            profile_dataset(dataset)


    # CI FIXTURES

    if args.fixtures:

        fixture_datasets = [
            FIXTURE_DIR / "mercedes_test.csv",
            FIXTURE_DIR / "manufacturing_test.csv"
        ]

        for dataset in fixture_datasets:
            profile_dataset(dataset)


    # NO OPTION PROVIDED

    if not args.real and not args.fixtures:

        parser.print_help()


# 4. PYTHON ENTRY POINY

if __name__ == "__main__":
    main()
