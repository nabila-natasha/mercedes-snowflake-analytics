import os
import snowflake.connector


def main():
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
        cursor.execute("""
            SELECT
                CURRENT_USER(),
                CURRENT_ROLE(),
                CURRENT_WAREHOUSE(),
                CURRENT_DATABASE(),
                CURRENT_REGION()
        """)

        result = cursor.fetchone()

        print("Snowflake connection successful!")
        print(f"User: {result[0]}")
        print(f"Role: {result[1]}")
        print(f"Warehouse: {result[2]}")
        print(f"Database: {result[3]}")
        print(f"Region: {result[4]}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()