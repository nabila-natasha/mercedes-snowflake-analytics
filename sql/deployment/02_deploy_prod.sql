/***************************************************************************************************
Project  : Mercedes-Benz Vehicle Analytics
Task     : Production Deployment
Day      : 6

Purpose  : 1) Establish the production Snowflake environment and create the
              objects required for CI/CD deployment tracking.
           2) Build the production analytics environment from scratch.

Architecture:
    RAW → SILVER → GOLD

Deployment:
    GitHub Actions → Snowflake MERCEDES_PROD
***************************************************************************************************/

USE ROLE MERC_CI_CD;

ALTER SESSION SET QUERY_TAG = '{"project":"mercedes","task":"prod_deployment","day":"6"}';

USE DATABASE MERCEDES_PROD;


-- 1. RAW FILE FORMAT

USE SCHEMA RAW;

CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = CSV
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '');


-- For Manufacturing Schema Inference
CREATE FILE FORMAT IF NOT EXISTS MERCEDES_PROD.RAW.MANUFACTURING_INFER_FORMAT
    TYPE = CSV
    PARSE_HEADER = TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';


-- For Manufacturing Data Loading
CREATE FILE FORMAT IF NOT EXISTS MERCEDES_PROD.RAW.MANUFACTURING_LOAD_FORMAT
    TYPE = CSV
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '');


CREATE FILE FORMAT IF NOT EXISTS NHTSA_JSON_FORMAT
    TYPE = JSON;


-- 2. RAW INTERNAL STAGE

CREATE STAGE IF NOT EXISTS USED_CAR_STAGE
    FILE_FORMAT = CSV_FORMAT;


CREATE STAGE IF NOT EXISTS MANUFACTURING_STAGE
    FILE_FORMAT = MANUFACTURING_INFER_FORMAT;


CREATE STAGE IF NOT EXISTS NHTSA_STAGE
    FILE_FORMAT = NHTSA_JSON_FORMAT;


-- 3. RAW TABLES

CREATE TABLE IF NOT EXISTS USED_CAR_RAW (
    MODEL           VARCHAR,
    YEAR            NUMBER,
    PRICE           NUMBER,
    TRANSMISSION    VARCHAR,
    MILEAGE         NUMBER,
    FUEL_TYPE       VARCHAR,
    TAX             NUMBER,
    MPG             FLOAT,
    ENGINE_SIZE     FLOAT
);


CREATE TABLE IF NOT EXISTS MERCEDES_PROD.RAW.MANUFACTURING_RAW
USING TEMPLATE (
    SELECT ARRAY_AGG(
        OBJECT_CONSTRUCT(
            'COLUMN_NAME', COLUMN_NAME,
            'TYPE', TYPE,
            'NULLABLE', TRUE
        )
    )
    FROM TABLE(
        INFER_SCHEMA(
            LOCATION => '@MERCEDES_PROD.RAW.MANUFACTURING_STAGE',
            FILE_FORMAT => 'MERCEDES_PROD.RAW.MANUFACTURING_INFER_FORMAT' -- use infer file format
        )
    )
);


CREATE TABLE IF NOT EXISTS VEHICLE_SAFETY_RAW (
    SOURCE_FILE     VARCHAR,
    INGESTED_AT     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    API_RESPONSE    VARIANT
);


-- 4. LOAD RAW DATA

COPY INTO MERCEDES_PROD.RAW.USED_CAR_RAW
FROM @MERCEDES_PROD.RAW.USED_CAR_STAGE
FILE_FORMAT = (
    FORMAT_NAME = MERCEDES_PROD.RAW.CSV_FORMAT
)
ON_ERROR = 'ABORT_STATEMENT'
FORCE = FALSE;


COPY INTO MERCEDES_PROD.RAW.MANUFACTURING_RAW
FROM @MERCEDES_PROD.RAW.MANUFACTURING_STAGE
FILE_FORMAT = (
    FORMAT_NAME = MERCEDES_PROD.RAW.MANUFACTURING_LOAD_FORMAT  -- use this file format for LOAD DATA (SKIP_HEADER = 1)
)
ON_ERROR = 'ABORT_STATEMENT'
FORCE = FALSE;


COPY INTO MERCEDES_PROD.RAW.VEHICLE_SAFETY_RAW
(
    SOURCE_FILE,
    API_RESPONSE
)
FROM (
    SELECT
        METADATA$FILENAME,          -- return provenance filename
        $1                          -- return API_RESPONSE
    FROM @MERCEDES_PROD.RAW.NHTSA_STAGE
)
FILE_FORMAT = (
    FORMAT_NAME = MERCEDES_PROD.RAW.NHTSA_JSON_FORMAT
)
ON_ERROR = 'ABORT_STATEMENT'
FORCE = FALSE;


-- 5. BUILD SILVER

USE SCHEMA SILVER;

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
FROM MERCEDES_PROD.RAW.USED_CAR_RAW
WHERE MODEL IS NOT NULL;


CREATE OR REPLACE TABLE MANUFACTURING_CLEAN 
AS
SELECT *
FROM MERCEDES_PROD.RAW.MANUFACTURING_RAW;


CREATE OR REPLACE DYNAMIC TABLE NHTSA_VEHICLE_SAFETY 
    TARGET_LAG = '1 hour'
    WAREHOUSE = 'TRANSFORM_WH'
    REFRESH_MODE = FULL
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
    
FROM MERCEDES_PROD.RAW.VEHICLE_SAFETY_RAW r

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


-- 6. BUILD GOLD STAR SCHEMA

USE SCHEMA GOLD;

-- Dimension Tables
CREATE OR REPLACE TABLE DIM_MODEL 
AS
SELECT
    ROW_NUMBER() OVER (ORDER BY MODEL) AS MODEL_KEY,
    MODEL
FROM (
    SELECT DISTINCT
        TRIM(MODEL) AS MODEL
    FROM MERCEDES_PROD.SILVER.USED_CAR_CLEAN
    WHERE MODEL IS NOT NULL
);


CREATE OR REPLACE TABLE DIM_YEAR
AS
SELECT 
    DISTINCT YEAR   AS YEAR_KEY,
    YEAR
FROM MERCEDES_PROD.SILVER.USED_CAR_CLEAN
WHERE YEAR IS NOT NULL;


CREATE OR REPLACE TABLE DIM_SAFETY
AS
SELECT
    ROW_NUMBER() OVER(ORDER BY VEHICLE_ID)    AS SAFETY_KEY,
    VEHICLE_ID,
    VEHICLE_DESCRIPTION,
    NHTSA_MODEL,
    UK_MODEL
FROM MERCEDES_PROD.SILVER.NHTSA_VEHICLE_SAFETY
QUALIFY ROW_NUMBER() OVER(
    PARTITION BY VEHICLE_ID
    ORDER BY VEHICLE_ID
) = 1; 


-- Fact tables
CREATE OR REPLACE TABLE FACT_USED_CAR 
AS
SELECT 
    ROW_NUMBER() OVER(
        ORDER BY
        c.MODEL,
        c.YEAR,
        c.PRICE,
        c.MILEAGE     
    ) AS CAR_ID,
    -- Model dimension key
    m.MODEL_KEY,
    m.MODEL,
    -- Year dimension key
    y.YEAR_KEY,
    -- Business measures
    c.PRICE,
    c.MILEAGE,
    c.TAX,
    c.MPG,
    c.ENGINE_SIZE,
    -- Descriptive attributes
    c.TRANSMISSION,
    c.FUEL_TYPE
FROM MERCEDES_PROD.SILVER.USED_CAR_CLEAN c
LEFT JOIN MERCEDES_PROD.GOLD.DIM_MODEL m
    ON UPPER(TRIM(c.MODEL)) = UPPER(TRIM(m.MODEL))
LEFT JOIN MERCEDES_PROD.GOLD.DIM_YEAR y
    ON c.YEAR = y.YEAR_KEY;


CREATE OR REPLACE TABLE FACT_VEHICLE_SAFETY 
AS
SELECT
    VEHICLE_ID,
    MODEL_YEAR,
    UK_MODEL,
    NHTSA_MODEL,
    VEHICLE_DESCRIPTION,
    TRY_TO_NUMBER(OVERALL_RATING)                  AS OVERALL_RATING,
    TRY_TO_NUMBER(OVERALL_FRONT_CRASH_RATING)      AS FRONT_CRASH_RATING,
    TRY_TO_NUMBER(OVERALL_SIDE_CRASH_RATING)       AS SIDE_CRASH_RATING,
    TRY_TO_NUMBER(ROLLOVER_RATING)                 AS ROLLOVER_RATING,
    ROLLOVER_POSSIBILITY,
    COMPLAINTS_COUNT,
    RECALLS_COUNT,
    INVESTIGATION_COUNT,
    ELECTRONIC_STABILITY_CONTROL,
    FORWARD_COLLISION_WARNING,
    LANE_DEPARTURE_WARNING
FROM MERCEDES_PROD.SILVER.NHTSA_VEHICLE_SAFETY;


-- 7. ML RESULT TABLES
-- These tables are populated by the ML Python pipeline.
-- MANUFACTURING_PREDICTIONS
-- MANUFACTURING_FEATURE_IMPORTANCE
-- MANUFACTURING_MODEL_METRICS


-- 8. AUDIT LOG TABLE
-- Records every production deployment executed by CI/CD

USE SCHEMA AUDIT;

CREATE TABLE IF NOT EXISTS CI_CD_DEPLOYMENT_LOG (
    DEPLOYMENT_ID           INTEGER AUTOINCREMENT,
    DEPLOYMENT_TIMESTAMP    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DEPLOYED_BY             VARCHAR,
    DEPLOYMENT_SOURCE       VARCHAR,
    DEPLOYMENT_STATUS       VARCHAR
);

-- Record successful deployment
INSERT INTO CI_CD_DEPLOYMENT_LOG (
    DEPLOYED_BY,
    DEPLOYMENT_SOURCE,
    DEPLOYMENT_STATUS
)
SELECT 
    CURRENT_USER(),
    'GitHub Actions',
    'SUCCESS';

