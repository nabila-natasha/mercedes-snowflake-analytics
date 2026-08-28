import os
from pathlib import Path
import snowflake.connector


# PROJECT CONFIGURATION

BASE_DIR = Path(__file__).resolve().parents[1]

USED_CAR_DIR = BASE_DIR / "data" / "raw"


# ENVIRONMENT CONFIGURATION

SNOWFLAKE_DATABASE = os.environ["SNOWFLAKE_DATABASE"]
SNOWFLAKE_ROLE = os.environ["SNOWFLAKE_ROLE"]

RAW_SCHEMA = "RAW"

USED_CAR_STAGE = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.USED_CAR_STAGE"
)

USED_CAR_RAW_TABLE = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.USED_CAR_RAW"
)

USED_CAR_CSV_FORMAT = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.CSV_FORMAT"
)


# MAIN

def main():

    print("=" * 70)
    print("LOADING MERCEDES USED CAR CSV INTO SNOWFLAKE")
    print("=" * 70)


    # 1. FIND SOURCE CSV

    csv_files = sorted(
        USED_CAR_DIR.glob("mercedes.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No mercedes.csv file found in {USED_CAR_DIR}"
        )

    print(f"\nCSV file found: {len(csv_files)}")

    for file in csv_files:
        print(f"  - {file.name}")


    # 2. CONNECT TO SNOWFLAKE USING GITHUB ACTIONS SECRETS 

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=SNOWFLAKE_DATABASE,
        schema=RAW_SCHEMA,
        role=SNOWFLAKE_ROLE
    )

    cursor = conn.cursor()


    try:

        # 3. CREATE FILE FORMAT

        print("\nCreating used car CSV file format...")

        cursor.execute(
            f"""
            CREATE FILE FORMAT IF NOT EXISTS
                {USED_CAR_CSV_FORMAT}
                TYPE = CSV
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                SKIP_HEADER = 1
                NULL_IF = ('NULL', 'null', '')
            """
        )


        # 4. CREATE INTERNAL STAGE

        print("Creating used car internal stage...")

        cursor.execute(
            f"""
            CREATE STAGE IF NOT EXISTS
                {USED_CAR_STAGE}
                FILE_FORMAT = {USED_CAR_CSV_FORMAT}
            """
        )


         # 5. CREATE RAW TABLE

        print("Creating used car RAW table...")

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS
                {USED_CAR_RAW_TABLE}
            (
                MODEL           VARCHAR,
                YEAR            NUMBER,
                PRICE           NUMBER,
                TRANSMISSION    VARCHAR,
                MILEAGE         NUMBER,
                FUEL_TYPE       VARCHAR,
                TAX             NUMBER,
                MPG             FLOAT,
                ENGINE_SIZE     FLOAT
            )
            """
        )


        # 6. UPLOAD CSV TO INTERNAL STAGE

        for file in csv_files:

            print(f"\nUploading: {file.name}")

            cursor.execute(
                f"""
                PUT
                'file://{file.as_posix()}'
                @{USED_CAR_STAGE}
                AUTO_COMPRESS=FALSE
                OVERWRITE=FALSE
                """
            )


        # 7. COPY INTO RAW TABLE

        print(
            f"\nLoading staged CSV into "
            f"{USED_CAR_RAW_TABLE}..."
        )

        cursor.execute(
            f"""
            COPY INTO {USED_CAR_RAW_TABLE}
            FROM @{USED_CAR_STAGE}
            FILE_FORMAT = (
                FORMAT_NAME = '{USED_CAR_CSV_FORMAT}'
            )
            ON_ERROR = 'ABORT_STATEMENT'
            FORCE = FALSE
            """
        )

        results = cursor.fetchall()

        print("\nCOPY INTO results:")

        for result in results:
            print(result)


        # 8. VALIDATE RAW TABLE

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {USED_CAR_RAW_TABLE}
            """
        )

        row_count = cursor.fetchone()[0]

        print(
            f"\nRAW USED CAR rows: {row_count:,}"
        )

        print("\n" + "=" * 70)
        print(
            f"USED CAR RAW LOAD SUCCESS - "
            f"{SNOWFLAKE_DATABASE}"
        )
        print("=" * 70)

    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
