import os
import sys
from pathlib import Path
import snowflake.connector

def main():

    # 1. GET SQL FILE FROM COMMAND LINE
    # EXAMPLE:
    # python scripts/deploy_sql.py sql/silver/01_build_silver_tables.sql

    if len(sys.argv) != 2:
        print(
            "Usage: python scripts/deploy_sql.py <sql_file>"
        )
        sys.exit(1)


    sql_file = Path(sys.argv[1])

    if not sql_file.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_file}"
        )

    print("=" * 70)
    print(f"Executing SQL: {sql_file}")
    print("=" * 70)


    # 2. READ SQL FILE

    sql = sql_file.read_text(
        encoding="utf-8"
    )


    # 3. CONNECT TO SNOWFLAKE
    # Credentials come from GitHub Actions Secrets.
    # We DO NOT hard-code passwords in GitHub.

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
    )

    cursor = conn.cursor()


    try:

        # 4. SPLIT SQL INTO INDIVIDUAL STATEMENTS

        statements = [
            statement.strip()
            for statement in sql.split(";")
            if statement.strip()
        ]


        print(
            f"SQL statements found: "
            f"{len(statements)}"
        )


        # 5. EXECUTE EACH STATEMENT

        for i, statement in enumerate(statements, start=1):

            print(
                f"Executing statement {i}..."
            )

            cursor.execute(statement)

        print()
        print("=" * 70)
        print("SQL DEPLOYMENT SUCCESS")
        print("=" * 70)

    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
