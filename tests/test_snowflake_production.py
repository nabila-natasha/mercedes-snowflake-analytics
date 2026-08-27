import os
import snowflake.connector


def get_connection():

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database="MERCEDES_PROD",
        schema="AUDIT"
    )

def print_check(name, value, passed=True):

    status = "PASS" if passed else "FAIL"

    print(
        f"{status:<6} | "
        f"{name:<45}  | "
        f"{value}"
    )


def main():

    print("=" * 70)
    print("PRODUCTION DEPLOYMENT VALIDATION")
    print("=" * 70)    

    conn = get_connection()
    cursor = conn.cursor()

    overall_success = True

    expected_role = os.environ["SNOWFLAKE_ROLE"]

    try:

        # TEST 1 - DATABASE

        cursor.execute(
            """
            SELECT 
                CURRENT_USER()      AS CURRENT_USER,
                CURRENT_ROLE()      AS CURRENT_ROLE,
                CURRENT_DATABASE()  AS CURRENT_DATABASE,
                CURRENT_WAREHOUSE() AS CURRENT_WAREHOUSE;
            """
        )

        user, role, database, warehouse = cursor.fetchone()

        print_check(
            "Current User",
            user,
            user == "MERC_GITHUB_CI"
        )

        print_check(
            "Current Role",
            role,
            role == expected_role
        )

        print_check(
            "Current Database",
            database,
            database == "MERCEDES_PROD"
        )
        
        print_check(
            "Current Warehouse",
            warehouse,
            warehouse == "TRANSFORM_WH"
        )

        if user != "MERC_GITHUB_CI":
            overall_success = False

        if role != expected_role:
            overall_success = False

        if database != "MERCEDES_PROD":
            overall_success = False
        
        if warehouse != "TRANSFORM_WH":
            overall_success = False

    
    # TEST 2 - AUDIT TABLE

        cursor.execute("""
            SELECT COUNT(*)
            FROM MERCEDES_PROD.AUDIT.CI_CD_DEPLOYMENT_LOG;
        """)

        deployment_count = cursor.fetchone()[0]

        print_check(
            "Deployment Audit Records",
            deployment_count,
            deployment_count > 0
        )

        if deployment_count == 0:
            overall_success = False


        # TEST 3 - REQUIRED SCHEMAS

        cursor.execute("""
            SELECT COUNT(*)
            FROM MERCEDES_PROD.INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME IN
            (   
                'RAW',
                'SILVER',
                'GOLD',
                'AUDIT'
            );
        """)

        schema_count = cursor.fetchone()[0]

        print_check(
            "Required Production Schemas",
            f"{schema_count} / 4",
            schema_count == 4
        )

        if schema_count != 4:
            overall_success = False


        # FINAL RESULT

        print()

        if overall_success:

            print("=" * 70)
            print("PRODUCTION VALIDATION: SUCCESS")
            print("=" * 70)

        else:

            print("=" * 70)
            print("PRODUCTION VALIDATION: FAILED")
            print("=" * 70)


    finally:

        cursor.close()
        conn.close()



if __name__ == "__main__":
    main()