import os
import snowflake.connector



def main():

    print("=" * 70)
    print("GOLD DATA QUALITY TEST")
    print("=" * 70)

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

        # TEST 1: GOLD FACT table must contain records.

        cursor.execute("""
            SELECT COUNT(*)
            FROM MERCEDES_DEV.GOLD.FACT_USED_CAR
        """)

        used_car_count = cursor.fetchone()[0]

        if used_car_count == 0:
            raise AssertionError(
                "FACT_USED_CAR contains zero records."
            )

        print(
            f"FACT_USED_CAR rows: "
            f"{used_car_count:,}"
        )


        # TEST 2: Safety table must contain records.

        cursor.execute("""
            SELECT COUNT(*)
            FROM MERCEDES_DEV.GOLD.FACT_VEHICLE_SAFETY
        """)

        safety_count = cursor.fetchone()[0]

        if safety_count == 0:
            raise AssertionError(
                "FACT_VEHICLE_SAFETY contains zero records."
            )

        print(
            f"FACT_VEHICLE_SAFETY rows: "
            f"{safety_count:,}"
        )


        # TEST 3: No negative vehicle prices.

        cursor.execute("""
            SELECT COUNT(*)
            FROM MERCEDES_DEV.GOLD.FACT_USED_CAR
            WHERE PRICE < 0
        """)

        negative_prices = cursor.fetchone()[0]

        if negative_prices > 0:
            raise AssertionError(
                f"Found {negative_prices} negative prices."
            )


        print("Negative price test: PASSED")


        print()
        print("=" * 70)
        print("GOLD DATA QUALITY: SUCCESS")
        print("=" * 70)


    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()