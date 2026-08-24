import json
import time
from pathlib import Path

import pandas as pd
import requests


# 1. PROJECT CONFIGURATION

# BASE_DIR points to the root of the GitHub repository.
# __file__ = scripts/01_ingest_nhtsa.py
# .parents[1] moves: scripts/ -> project root/
# This allows the script to work regardless of wehere the
# repository is located on computer or Github Codespace.

BASE_DIR = Path(__file__).resolve().parents[1]

# Original Mercedes used-car dataset.
INPUT_FILE = BASE_DIR / "data" / "raw" / "mercedes.csv"

# NHTSA JSON files will be stored here.
OUTPUT_DIR = BASE_DIR / "data" / "raw" / "nhtsa"

# NHTSA API base URL.
BASE_URL = "https://api.nhtsa.gov"

MAKE = "Mercedes-Benz"

# For the smoke test, we deliberately use a small range.
# Once this works, we can expand the range.
MIN_YEAR = 2018
MAX_YEAR = 2020

# Small delay between requests.
REQUEST_DELAY = 0.2


# 2. NORMALIZE UK MODEL NAMES
# Standardize the UK and NHTSA model names before calling NHTSA.

def normalize_model(model):
    """
    Convert the UK dataset's model name into a format
    closer to the NHTSA model catalogue.

    Example:

        "A Class"   -> "A-CLASS"
        "C Class"   -> "C-CLASS"
        "CLA Class" -> "CLA-CLASS"
        "X-CLASS"   -> "X-CLASS"
    """

    # Convert to string.
    # Remove leading/trailing spaces.
    # Convert everything to uppercase.
    model = str(model).strip().upper()

    # Standardize separators.
    model = model.replace("-", " ")
    model = model.replace("_", " ")

    # Remove duplicate spaces.
    model = " ".join(model.split())

    # Convert "A CLASS" into "A-CLASS".
    # This is the naming convention we observed in NHTSA Mercedes model catalogue.
    if model.endswith(" CLASS"):

        model = (
            model[:-6]
            + "-CLASS"
        )

    return model


# 3. LOAD MODEL/YEAR COMBINATIONS FROM UK DATASET
# We do NOT manually type every Mercedes model.
# Instead, we use the actual UK used-car dataset as our
# catalogue of model/year combinations.

def load_model_years():
    """
    Read the UK Mercedes dataset and automatically determine
    which model/year combinations need to be queried.

    We do NOT manually type the Mercedes models.

    The dataset itself becomes our source catalogue.
    """

    # Read the source dataset.
    df = pd.read_csv(INPUT_FILE)

    # Keep only the columns required for NHTSA matching.
    combinations = (
        df[
            [
                "model",
                "year"
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    # Convert year to numeric.
    combinations["year"] = pd.to_numeric(
        combinations["year"],
        errors="coerce"
    )

    # Remove rows where year is invalid.
    combinations = combinations.dropna(
        subset=["year"]
    )

    # Restrict the current run to the selected
    # smoke-test years.
    combinations = combinations[
        (combinations["year"] >= MIN_YEAR)
        &
        (combinations["year"] <= MAX_YEAR)
    ]

    # Create the NHTSA-compatible model name.
    combinations["nhtsa_model"] = (
        combinations["model"]
        .apply(normalize_model)
    )

    # Sort for easier monitoring.
    combinations = combinations.sort_values(
        [
            "year",
            "nhtsa_model"
        ]
    )

    return combinations


# 4. REQUEST NHTSA VEHICLE VARIANTS

def get_vehicle_variants(year, model):
    """
    Ask NHTSA:

        "For this make + model + year,
         which crash-tested vehicle variants exist?"

    Example:

        2018 Mercedes-Benz C-CLASS

    may return:

        VehicleId 12471
        VehicleId 12470

    These VehicleIds are then used in the next API call
    to retrieve the detailed safety ratings.
    """

    url = (
        f"{BASE_URL}/SafetyRatings/"
        f"modelyear/{year}/"
        f"make/{MAKE}/"
        f"model/{model}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    # A 404 means NHTSA does not have a matching entry.
    if response.status_code == 404:
        return []

    response.raise_for_status()

    data = response.json()

    # NHTSA returns the vehicle variants inside "Results".
    return data.get("Results") or []


# 5. GET DETAILED SAFETY INFORMATION

def get_safety_details(vehicle_id):
    """
    Use the VehicleId returned by the previous endpoint
    to retrieve the detailed NHTSA crash-test information.
    """

    url = (
        f"{BASE_URL}/SafetyRatings/"
        f"VehicleId/{vehicle_id}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    # VehicleId no longer available.
    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()


# 6. SAVE ONE JSON FILE PER YEAR

def save_year_json(year, records):
    """
    Save all model/year/vehicle safety information
    for one year into one JSON file.
    We use one file per year instead of one file per vehicle.
    This keeps the RAW ingestion manageable.
    """
    # Create the directory if it does not exist.
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Build the output filename.
    output_file = (
        OUTPUT_DIR
        / f"nhtsa_safety_{year}.json"
    )

    # Overall JSON structure.
    payload = {
        "source": "NHTSA",
        "make": MAKE,
        "model_year": year,
        "record_count": len(records),
        "results": records
    }

    # Write JSON to disk.
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            payload,
            file,
            indent=2
        )

    print(
        f"\nSaved: {output_file}"
    )


# 7. MAIN INGESTION PROCESS

def main():

    print("=" * 70)
    print("NHTSA BATCH SAFETY INGESTION")
    print("=" * 70)


    # Load UK model/year combinations from mercedes.csv

    combinations = load_model_years()

    print(
        f"UK model/year combinations: "
        f"{len(combinations):,}"
    )


    # Dictionary store results by year.
    # {
    #     2018: [...],
    #     2019: [...]
    # }

    yearly_results = {}


    # Monitoring counters

    matched_combinations = 0
    combinations_with_no_variants = 0
    vehicle_variants_found = 0
    safety_details_found = 0
    failed_requests = 0


    # Process every unique model/year combination

    for _, row in combinations.iterrows():

        year = int(row["year"])

        uk_model = str(
            row["model"]
        )

        nhtsa_model = str(
            row["nhtsa_model"]
        )


        print("\n" + "-" * 70)

        print(
            f"{year} | "
            f"UK: {uk_model} | "
            f"NHTSA: {nhtsa_model}"
        )


        try:

            # STEP 1: Find the NHTSA vehicle variants.

            vehicles = get_vehicle_variants(
                year,
                nhtsa_model
            )

            variant_count = len(
                vehicles
            )

            print(
                f"  Vehicle variants: "
                f"{variant_count}"
            )


            # If no variants exists

            if variant_count == 0:

                combinations_with_no_variants += 1

                print(
                    "  No NHTSA crash-tested "
                    "vehicle variants found."
                )

            else:

                matched_combinations += 1

                vehicle_variants_found += (
                    variant_count
                )


            # Store detailed vehicle information.

            vehicle_records = []


            # STEP 2: For EVERY VehicleId, retrieve detailed safety ratings.

            for vehicle in vehicles:

                vehicle_id = vehicle.get(
                    "VehicleId"
                )

                vehicle_description = (
                    vehicle.get(
                        "VehicleDescription"
                    )
                )

                print(
                    f"    VehicleId: "
                    f"{vehicle_id}"
                )

                # Request detailed safety information.
                safety_data = (
                    get_safety_details(
                        vehicle_id
                    )
                )


                # Store both the vehicle identification and the
                # detailed safety response.

                vehicle_records.append({

                    "vehicle_id":
                        vehicle_id,

                    "vehicle_description":
                        vehicle_description,

                    "safety_ratings":
                        safety_data
                })

                if safety_data is not None:

                    safety_details_found += 1


                # Pause between VehicleId requests.
                time.sleep(REQUEST_DELAY)


            # STEP 3: Store the complete model/year result.

            if year not in yearly_results:

                yearly_results[year] = []

            yearly_results[year].append({

                "source": {

                    "uk_model": uk_model,
                    "nhtsa_model": nhtsa_model,
                    "model_year": year
                },

                "vehicle_count": variant_count,
                "vehicles": vehicle_records
            })


            # Pause before the next model/year request.
            time.sleep(REQUEST_DELAY)


        except Exception as exc:

            failed_requests += 1

            print("\n  !!! REQUEST FAILED !!!")
            print(f"  Year     : {year}")
            print(f"  UK model : {uk_model}")
            print(f"  NHTSA    : {nhtsa_model}")
            print(
                f"  Error    : "
                f"{type(exc).__name__}: {exc}"
            )


    # 8. WRITE ONE JSON FILE PER YEAR

    for year, records in yearly_results.items():

        save_year_json(
            year,
            records
        )


    # 9. FINAL INGESTION SUMMARY

    print("\n" + "=" * 70)
    print("INGESTION SUMMARY")
    print("=" * 70)

    print(
        f"Model/year combinations : "
        f"{len(combinations):,}"
    )

    print(
        f"With NHTSA variants     : "
        f"{matched_combinations:,}"
    )

    print(
        f"No variants returned    : "
        f"{combinations_with_no_variants:,}"
    )

    print(
        f"Vehicle variants found  : "
        f"{vehicle_variants_found:,}"
    )

    print(
        f"Safety details found    : "
        f"{safety_details_found:,}"
    )

    print(
        f"Failed requests         : "
        f"{failed_requests:,}"
    )

    print("=" * 70)


# 10. PYTHON ENTRY POINT

if __name__ == "__main__":
    main()
