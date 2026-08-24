/***************************************************************************************************
Project : Mercedes-Benz Vehicle Analytics
Task    : NHTSA SILVER transformation
Day     : 4
Purpose : 1) Used-car SILVER transformation 
          2) Manufacturing SILVER table (no transformation)
          3) Flatten NHTSA JSON into analytics-ready vehicle safety records
***************************************************************************************************/

USE ROLE MERC_DE;

ALTER SESSION SET QUERY_TAG =
'{"project":"mercedes","task":"create_silver_tables","day":"4"}';

USE WAREHOUSE LOAD_WH;
USE DATABASE MERCEDES_DEV;
USE SCHEMA SILVER;


-- 1. CREATE USED_CAR_CLEAN SILVER TABLE

CREATE OR REPLACE TABLE USED_CAR_CLEAN 
AS
SELECT 
    TRIM(MODEL)                 AS MODEL,
    TRY_TO_NUMBER(YEAR)         AS YEAR,
    TRY_TO_NUMBER(PRICE)        AS PRICE,
    UPPER(TRIM(TRANSMISSION))   AS TRANSMISSION,
    TRY_TO_NUMBER(MILEAGE)      AS MILEAGE,
    UPPER(TRIM(FUEL_TYPE))      AS FUEL_TYPE,
    TRY_TO_NUMBER(TAX)          AS TAX,
    TRY_TO_DOUBLE(MPG)          AS MPG,
    TRY_TO_DOUBLE(ENGINE_SIZE)  AS ENGINE_SIZE
FROM MERCEDES_DEV.RAW.USED_CAR_RAW
WHERE MODEL IS NOT NULL;


-- 2. VALIDATE USED_CAR_CLEAN

SELECT 
    COUNT(*)                AS TOTAL_ROWS,  -- 13119
    COUNT_IF(MODEL IS NULL) AS NULL_MODEL,  -- 0
    COUNT_IF(YEAR IS NULL)  AS NULL_YEAR,   -- 0
    COUNT_IF(PRICE IS NULL) AS NULL_PRICE   -- 0
FROM MERCEDES_DEV.SILVER.USED_CAR_CLEAN;


-- 3. CREATE MANUFACTURING SILVER TABLE

CREATE OR REPLACE TABLE MANUFACTURING_CLEAN 
AS
SELECT *
FROM MERCEDES_DEV.RAW.MANUFACTURING_RAW;


-- 4. VALIDATE MANUFACTURING_CLEAN

SELECT 
    COUNT(*)        -- 4209
FROM MERCEDES_DEV.SILVER.MANUFACTURING_CLEAN;

DESC TABLE MERCEDES_DEV.SILVER.MANUFACTURING_CLEAN;


-- 5. CREATE NHTSA_VEHICLE_SAFETY SILVER TABLE

CREATE OR REPLACE TABLE NHTSA_VEHICLE_SAFETY 
AS
SELECT
    -- Source/Provenance
    r.SOURCE_FILE,
    r.INGESTED_AT,
    
    -- UK model information
    result.value:"source":"model_year"::NUMBER              AS MODEL_YEAR,
    result.value:"source":"nhtsa_model"::VARCHAR            AS NHTSA_MODEL,
    result.value:"source":"uk_model"::VARCHAR               AS UK_MODEL,

    -- Vehicle information
    vehicle.value:"vehicle_id"::NUMBER                      AS VEHICLE_ID,
    vehicle.value:"vehicle_description"::VARCHAR            AS VEHICLE_DESCRIPTION,

    -- Crash-test safety ratings
    rating.value:"OverallRating"::VARCHAR                   AS OVERALL_RATING,
    rating.value:"OverallFrontCrashRating"::VARCHAR         AS OVERALL_FRONT_CRASH_RATING,
    rating.value:"FrontCrashDriversideRating"::VARCHAR      AS FRONT_CRASH_DRIVER_RATING,
    rating.value:"FrontCrashPassengersideRating"::VARCHAR   AS FRONT_CRASH_PASSENGER_RATING,
    rating.value:"OverallSideCrashRating"::VARCHAR          AS OVERALL_SIDE_CRASH_RATING,
    rating.value:"SideCrashDriversideRating"::VARCHAR       AS SIDE_CRASH_DRIVER_RATING,
    rating.value:"SideCrashPassengersideRating"::VARCHAR    AS SIDE_CRASH_PASSENGER_RATING,
    rating.value:"RolloverRating"::VARCHAR                  AS ROLLOVER_RATING,
    rating.value:"RolloverPossibility"::FLOAT               AS ROLLOVER_POSSIBILITY,
    rating.value:"SidePoleCrashRating"::VARCHAR             AS SIDE_POLE_CRASH_RATING,

    -- Safety technology
    rating.value:"NHTSAElectronicStabilityControl"::VARCHAR AS ELECTRONIC_STABILITY_CONTROL,
    rating.value:"NHTSAForwardCollisionWarning"::VARCHAR    AS FORWARD_COLLISION_WARNING,
    rating.value:"NHTSALaneDepartureWarning"::VARCHAR       AS LANE_DEPARTURE_WARNING,

    -- Safety-relates NHTSA counts
    rating.value:"ComplaintsCount"::NUMBER                  AS COMPLAINTS_COUNT,
    rating.value:"RecallsCount"::NUMBER                     AS RECALLS_COUNT,
    rating.value:"InvestigationCount"::NUMBER               AS INVESTIGATION_COUNT,

    -- NHTSA's own vehicle metadata
    rating.value:"ModelYear"::NUMBER                        AS NHTSA_MODEL_YEAR,
    rating.value:"Make"::VARCHAR                            AS NHTSA_MAKE, 
    rating.value:"Model"::VARCHAR                           AS NHTSA_MODEL_FROM_RATING
    
FROM MERCEDES_DEV.RAW.VEHICLE_SAFETY_RAW r

-- LEVEL 1 - Expand: API_RESPONSE.results[]
,LATERAL FLATTEN(
    INPUT => r.API_RESPONSE:"results"
) result

-- LEVEL 2 - Expand: vehicles[]
,LATERAL FLATTEN(
    INPUT => result.value:"vehicles"
) vehicle

-- LEVEL 3 - Expand: safety_ratings:Results[]
,LATERAL FLATTEN(
    INPUT => vehicle.value:"safety_ratings":"Results"
) rating;


-- 6. VALIDATE NHTSA_VEHICLE_SAFETY

SELECT 
    COUNT(*)
FROM MERCEDES_DEV.SILVER.NHTSA_VEHICLE_SAFETY;  -- 89


SELECT *
FROM MERCEDES_DEV.SILVER.NHTSA_VEHICLE_SAFETY
LIMIT 20;


SELECT  
    MODEL_YEAR,
    COUNT(*)    AS VEHICLES,
    AVG(
        TRY_TO_NUMBER(OVERALL_RATING)
    )           AS AVG_OVERALL_RATING 
FROM MERCEDES_DEV.SILVER.NHTSA_VEHICLE_SAFETY
GROUP BY MODEL_YEAR
ORDER BY MODEL_YEAR;

