import os
import sys
from pathlib import Path
import snowflake.connector

def main():

    # 1. GET SQL FILE FROM COMMAND LINE
    # EXAMPLE:
    # python scripts/deploy_sql.py sql/silver/01_build_silver_tables.sql
    # The SQL file is passed dynamically from GitHub Actions.

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


    # 3. SPLIT SQL INTO INDIVIDUAL STATEMENTS
    # We remove empty statements after splitting.
    # This prevents Snowflake from receiving:
    #     cursor.execute("")
    # which causes:
    #     SQL compilation error:
    #     Empty SQL statement.

    statements = []

    for statement in sql.split(";"):

        statement = statement.strip()

        # Only keep statements that actually contain SQL.
        if statement:
            statements.append(statement)


    print(
        f"SQL statements found: "
        f"{len(statements)}"
    )


    # 4. CONNECT TO SNOWFLAKE
    # Credentials are supplied through GitHub Actions.
    # They are NOT hard-coded in the repository.

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "RAW"),
    )

    cursor = conn.cursor()

    
    # 5. EXECUTE EACH SQL STATEMENT

    try:

        for i, statement in enumerate(
            statements,
            start=1
        ):

            print()
            print(
                f"Executing statement "
                f"{i}/{len(statements)}..."
            )

            try:

                cursor.execute(statement)

            except Exception as exc:

                # Print the statement that caused the failure.
                # This makes GitHub Actions debugging much easier.

                print()
                print("=" * 70)
                print(
                    f"SQL FAILED - STATEMENT {i}"
                )
                print("=" * 70)

                print(statement)

                print()
                print(
                    f"Error: "
                    f"{type(exc).__name__}: {exc}"
                )

                raise

        print()
        print("=" * 70)
        print("SQL DEPLOYMENT SUCCESS")
        print("=" * 70)


    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
