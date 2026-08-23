import os
from pathlib import Path
import snowflake.connector

def main():

    sql_file = Path("sql/deployment/01_deploy_dev.sql")

    if not sql_file.exists():
        raise FileNotFoundError(
            f"SQL deployment file not found: {sql_file}"
        )

    sql = sql_file.read_text()

    print(f"Loading SQL file: {sql_file}")

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

        statements = [
            statement.strip()
            for statement in sql.split(";")
            if statement.strip()
        ]

        print(f"Executing {len(statements)} SQL statements...")

        for i, statement in enumerate(statements, start=1):

            print(f"Executing statement {i}...")

            cursor.execute(statement)


        print()
        print("==========================================")
        print("Snowflake DEV deployment: SUCCESS")
        print("==========================================")


    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()