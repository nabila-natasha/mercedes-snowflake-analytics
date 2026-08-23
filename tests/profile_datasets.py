from pathlib import Path
import pandas as pd

# 1. DEFINE WHERE OUR RAW DATASETS ARE STORED

DATA_DIR = Path("data/raw")


# 2. DEFINE A FUNCTION TO PROFILE ONE CSV FILE

def profile_dataset(file_name):
    file_path = DATA_DIR / file_name

    print("\n" + "=" * 70)
    print(f"PROFILE: {file_name}")
    print("=" * 70)


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

    datasets = [
        "mercedes.csv",
        "train.csv"
    ]

    for dataset in datasets:
        profile_dataset(dataset)


# 4. PYTHON ENTRY POINY

if __name__ == "__main__":
    main()





