/***************************************************************************************************
Project : Mercedes-Benz Vehicle Analytics
Task    : Create NHTSA RAW objects
Day     : 3

Purpose :
    1. Create JSON file format
    2. Create NHTSA internal stage
    3. Create RAW table that preserves the complete NHTSA API response

Important:
    The actual PUT and COPY INTO operations are performed by
    scripts/02_load_nhtsa_snowflake.py.

    This SQL file creates the RAW infrastructure only.
***************************************************************************************************/

USE ROLE MERC_DE;

ALTER SESSION SET QUERY_TAG =
'{"project":"mercedes","task":"create_nhtsa_raw","day":"3"}';

USE WAREHOUSE LOAD_WH;
USE DATABASE MERCEDES_DEV;
USE SCHEMA RAW;



-- 1. CREATE JSON FILE FORMAT

CREATE FILE FORMAT IF NOT EXISTS NHTSA_JSON_FORMAT
    TYPE = JSON;


-- 2. CREATE NHTSA INTERNAL STAGE

CREATE STAGE IF NOT EXISTS NHTSA_STAGE
    FILE_FORMAT = NHTSA_JSON_FORMAT;


-- 3. RAW NHTSA TABLE
-- One row represents one source JSON file.

-- API_RESPONSE contains the COMPLETE JSON response.
-- We deliberately keep it as VARIANT because RAW should
-- preserve the original source structure.

CREATE TABLE IF NOT EXISTS VEHICLE_SAFETY_RAW (
    SOURCE_FILE     VARCHAR,
    INGESTED_AT     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    API_RESPONSE    VARIANT
);


-- 4. VALIDATION

DESC TABLE VEHICLE_SAFETY_RAW;

LIST @MERCEDES_DEV.RAW.NHTSA_STAGE;


SELECT 
    COUNT(*) AS API_RESPONSES       -- 3 
FROM MERCEDES_DEV.RAW.VEHICLE_SAFETY_RAW;


SELECT
    SOURCE_FILE,
    INGESTED_AT,
    API_RESPONSE,
    TYPEOF(API_RESPONSE)    AS DATA_TYPE
FROM MERCEDES_DEV.RAW.VEHICLE_SAFETY_RAW;


-- 5. INSPECT JSON RESPONSE AND FLATTEN RESULTS ARRAY

SELECT 
    API_RESPONSE:"make"::VARCHAR        AS MAKE,
    API_RESPONSE:"model_year"::NUMBER   AS MODEL_YEAR,
    API_RESPONSE:"record_count"::NUMBER AS RECORD_COUNT,
    API_RESPONSE:"results"              AS RESULTS  
FROM MERCEDES_DEV.RAW.VEHICLE_SAFETY_RAW;


SELECT 
    value
FROM MERCEDES_DEV.RAW.VEHICLE_SAFETY_RAW,
LATERAL FLATTEN(
    INPUT => API_RESPONSE:"results"     -- results is an array
)
LIMIT 10;
