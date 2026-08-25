/***************************************************************************************************
Project : Mercedes-Benz Vehicle Analytics
Layer   : GOLD
Task    : Create FACT tables
Purpose : Create the central fact table for the GOLD star schema
Grain   : One row = one used-car listing
          One row = one NHTSA crash-tested vehicle variant
***************************************************************************************************/

USE ROLE MERC_DE;

ALTER SESSION SET QUERY_TAG =
'{"project":"mercedes","task":"create_fact_tables","day":"5"}';

USE WAREHOUSE TRANSFORM_WH;
USE DATABASE MERCEDES_DEV;
USE SCHEMA GOLD;


-- 1. FACT USED CAR

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
FROM MERCEDES_DEV.SILVER.USED_CAR_CLEAN c
LEFT JOIN MERCEDES_DEV.GOLD.DIM_MODEL m
    ON UPPER(TRIM(c.MODEL)) = UPPER(TRIM(m.MODEL))
LEFT JOIN MERCEDES_DEV.GOLD.DIM_YEAR y
    ON c.YEAR = y.YEAR_KEY;



-- 2. FACT VEHICLE SAFETY

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
FROM MERCEDES_DEV.SILVER.NHTSA_VEHICLE_SAFETY;
