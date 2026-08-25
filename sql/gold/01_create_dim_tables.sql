/***************************************************************************************************
Project : Mercedes-Benz Vehicle Analytics
Layer   : GOLD
Task    : Create DIMS tables
Purpose : Create reusable dimensions for the GOLD star schema.
***************************************************************************************************/

USE ROLE MERC_DE;

ALTER SESSION SET QUERY_TAG =
'{"project":"mercedes","task":"create_dim_tables","day":"5"}';

USE WAREHOUSE TRANSFORM_WH;
USE DATABASE MERCEDES_DEV;
USE SCHEMA GOLD;


-- 1. MODEL DIMENSION

CREATE OR REPLACE TABLE DIM_MODEL 
AS
SELECT
    ROW_NUMBER() OVER (ORDER BY MODEL) AS MODEL_KEY,
    MODEL
FROM (
    SELECT DISTINCT
        TRIM(MODEL) AS MODEL
    FROM MERCEDES_DEV.SILVER.USED_CAR_CLEAN
    WHERE MODEL IS NOT NULL
);


-- 2. YEAR DIMENSION

CREATE OR REPLACE TABLE DIM_YEAR
AS
SELECT 
    DISTINCT YEAR   AS YEAR_KEY,
    YEAR
FROM MERCEDES_DEV.SILVER.USED_CAR_CLEAN
WHERE YEAR IS NOT NULL;


-- 3. SAFETY DIMENSION

CREATE OR REPLACE TABLE DIM_SAFETY
AS
SELECT
    ROW_NUMBER() OVER(ORDER BY VEHICLE_ID)    AS SAFETY_KEY,
    VEHICLE_ID,
    VEHICLE_DESCRIPTION,
    NHTSA_MODEL,
    UK_MODEL
FROM MERCEDES_DEV.SILVER.NHTSA_VEHICLE_SAFETY
QUALIFY ROW_NUMBER() OVER(  
    PARTITION BY VEHICLE_ID
    ORDER BY VEHICLE_ID
) = 1;      
