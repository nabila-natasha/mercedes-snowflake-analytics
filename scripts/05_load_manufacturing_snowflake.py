import os
from pathlib import Path
import snowflake.connector


# PROJECT CONFIGURATION

BASE_DIR = Path(__file__).resolve().parents[1]

MANUFACTURING_DIR = BASE_DIR / "data" / "raw"


# ENVIRONMENT CONFIGURATION

SNOWFLAKE_DATABASE = os.environ["SNOWFLAKE_DATABASE"]
SNOWFLAKE_ROLE = os.environ["SNOWFLAKE_ROLE"]

RAW_SCHEMA = "RAW"

MANUFACTURING_STAGE = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.MANUFACTURING_STAGE"
)

MANUFACTURING_RAW_TABLE = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.MANUFACTURING_RAW"
)

MANUFACTURING_INFER_FORMAT = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.MANUFACTURING_INFER_FORMAT"
)

MANUFACTURING_LOAD_FORMAT = (
    f"{SNOWFLAKE_DATABASE}.{RAW_SCHEMA}.MANUFACTURING_LOAD_FORMAT"
)


# MAIN

def main():

    print("=" * 70)
    print("LOADING MANUFACTURING CSV INTO SNOWFLAKE")
    print("=" * 70)


    # 1. FIND SOURCE CSV

    csv_files = sorted(
        MANUFACTURING_DIR.glob("train.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No train.csv file found in {MANUFACTURING_DIR}"
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

        # 3. CREATE INFERENCE FILE FORMAT

        print(
            "\nCreating manufacturing inference "
            "file format..."
        )

        cursor.execute(
            f"""
            CREATE FILE FORMAT IF NOT EXISTS
                {MANUFACTURING_INFER_FORMAT}
                TYPE = CSV
                PARSE_HEADER = TRUE
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            """
        )


        # 4. CREATE LOAD FILE FORMAT

        print(
            "Creating manufacturing load file format..."
        )

        cursor.execute(
            f"""
            CREATE FILE FORMAT IF NOT EXISTS
                {MANUFACTURING_LOAD_FORMAT}
                TYPE = CSV
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                SKIP_HEADER = 1
                NULL_IF = ('NULL', 'null', '')
            """
        )


        # 5. CREATE INTERNAL STAGE

        print(
            "Creating manufacturing internal stage..."
        )

        cursor.execute(
            f"""
            CREATE STAGE IF NOT EXISTS
                {MANUFACTURING_STAGE}
                FILE_FORMAT = {MANUFACTURING_INFER_FORMAT}
            """
        )


        # 6. UPLOAD CSV TO INTERNAL STAGE

        for file in csv_files:

            print(f"\nUploading: {file.name}")

            cursor.execute(
                f"""
                PUT
                'file://{file.as_posix()}'
                @{MANUFACTURING_STAGE}
                AUTO_COMPRESS=FALSE
                OVERWRITE=FALSE
                """
            )


        # 7. CREATE RAW TABLE USING INFER_SCHEMA

        print(
            "\nCreating manufacturing RAW table "
            "using schema inference..."
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS
                {MANUFACTURING_RAW_TABLE}
            USING TEMPLATE (
                SELECT ARRAY_AGG(
                    OBJECT_CONSTRUCT(
                        'COLUMN_NAME', COLUMN_NAME,
                        'TYPE', TYPE,
                        'NULLABLE', TRUE
                    )
                )
                FROM TABLE(
                    INFER_SCHEMA(
                        LOCATION => '@{MANUFACTURING_STAGE}',
                        FILE_FORMAT =>
                            '{MANUFACTURING_INFER_FORMAT}'
                    )
                )
            )
            """
        )


        # 8. COPY INTO RAW TABLE

        print(
            f"\nLoading staged CSV into "
            f"{MANUFACTURING_RAW_TABLE}..."
        )

        cursor.execute(
            f"""
            COPY INTO {MANUFACTURING_RAW_TABLE}
            FROM @{MANUFACTURING_STAGE}
            FILE_FORMAT = (
                FORMAT_NAME =
                    '{MANUFACTURING_LOAD_FORMAT}'
            )
            ON_ERROR = 'ABORT_STATEMENT'
            FORCE = FALSE
            """
        )

        results = cursor.fetchall()

        print("\nCOPY INTO results:")

        for result in results:
            print(result)


        # 9. VALIDATE RAW TABLE

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {MANUFACTURING_RAW_TABLE}
            """
        )

        row_count = cursor.fetchone()[0]

        print(
            f"\nRAW MANUFACTURING rows: "
            f"{row_count:,}"
        )

        print("\n" + "=" * 70)
        print(
            f"MANUFACTURING RAW LOAD SUCCESS - "
            f"{SNOWFLAKE_DATABASE}"
        )
        print("=" * 70)

    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
