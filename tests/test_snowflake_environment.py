import os
import snowflake.connector

EXPECTED_USER = "MERC_GITHUB_CI"
EXPECTED_ROLE = "MERC_CI_CD"
EXPECTED_DATABASE = "MERCEDES_DEV"
EXPECTED_WAREHOUSE = "TRANSFORM_WH"

REQUIRED_SCHEMAS = {
    "RAW",
    "SILVER",
    "GOLD",
    "AUDIT",
}


def main():

    print("Connecting to Snowflake...")

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

        # 1. VALIDATE CURRENT EXECUTION CONTEXT

        cursor.execute("""
            SELECT
                CURRENT_USER()      AS CURRENT_USER,
                CURRENT_ROLE()      AS CURRENT_ROLE,
                CURRENT_DATABASE()  AS CURRENT_DATABASE,
                CURRENT_WAREHOUSE() AS CURRENT_WAREHOUSE
        """)

        user, role, database, warehouse = cursor.fetchone()

        print(f"User:       {user}")
        print(f"Role:       {role}")
        print(f"Database:   {database}")
        print(f"Warehouse:  {warehouse}")


        # 2. VALIDATE USER

        if user != EXPECTED_USER:
            raise AssertionError(
                f"Expected User: {EXPECTED_USER}, "
                f"but found: {user}"
            )

        print("User validation: PASS")


        # 3. VALIDATE CI/CD ROLE

        if role != EXPECTED_ROLE:
            raise AssertionError(
                f"Expected Role: {EXPECTED_ROLE}, "
                f"but found: {role}"
            )

        print("Role validation: PASS")

        # 4. VALIDATE DATABASE

        if database != EXPECTED_DATABASE:
            raise AssertionError(
                f"Expected Database: {EXPECTED_DATABASE}, "
                f"but found: {database}"
            )

        print("Database validation: PASS")

        # 5. VALIDATE WAREHOUSE
        
        if warehouse != EXPECTED_WAREHOUSE:
            raise AssertionError(
                f"Expected Warehouse: {EXPECTED_WAREHOUSE}, "
                f"but found: {warehouse}"
            )

        print("Warehouse validation: PASS")


        # 6. VALIDATE REQUIRED SCHEMAS
        
        cursor.execute("""
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
        """)

        existing_schemas = {
            row[0]
            for row in cursor.fetchall()
        }

        missing_schemas = REQUIRED_SCHEMAS - existing_schemas

        if missing_schemas:
            raise AssertionError(
                f"Missing required schemas: {sorted(missing_schemas)}"
            )

        print("Schema validation: PASS")
        print(f"Required schemas found: {sorted(REQUIRED_SCHEMAS)}")


        # 7. FINAL RESULT

        print()
        print("==========================================")
        print("Snowflake environment validation: PASS")
        print("==========================================")


    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
