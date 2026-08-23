import json
import argparse
from pathlib import Path
import requests


# CONFIGURATION

BASE_URL = (
    "https://vpic.nhtsa.dot.gov/api/vehicles/"
    "GetModelsForMakeYear/make/mercedes-benz/"
)

OUTPUT_DIR = Path("data/raw")


#   MAIN

def main():

    parser = argparse.ArgumentParser(
        description="Ingest Mercedes-Benz vehicle data from NHTSA API"
    )

    parser.add_argument(
        "--year",
        type=int,
        default=2018,
        help="Mercedes-Benz model year to retrieve"
    )

    args = parser.parse_args()

    year = args.year

    api_url = (
        f"{BASE_URL}"
        f"modelyear/{year}?format=json"
    )

    output_file = (
        OUTPUT_DIR /
        f"nhtsa_mercedes_{year}.json"
    )

    print("=" * 70)
    print("NHTSA API INGESTION")
    print("=" * 70)

    print(f"Model year  : {year}")
    print(f"Requesting  : {api_url}")


    # CALL API

    response = requests.get(
        api_url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()


    # VALIDATE RESPONSE

    print(f"HTTP status : {response.status_code}")

    print(
        f"Records returned: "
        f"{len(data.get('Results', [])):,}"
    )


    # CREATE OUTPUT DIRECTORY (IF NOT EXISTS)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # Save API response

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


    print(f"Saved to    : {output_file}")

    print("NHTSA ingestion successful!")


if __name__ == "__main__":
    main()
    