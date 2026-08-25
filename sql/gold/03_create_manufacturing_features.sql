/***************************************************************************************************
Project : Mercedes-Benz Vehicle Analytics
Task    : Manufacturing ML Feature Dataset
Day     : 5

Purpose :
    Prepare the manufacturing dataset for predictive modelling.

    Target:
        Y = manufacturing test time

    The source dataset contains categorical and numerical/binary
    manufacturing configuration variables.

    GOLD.MANUFACTURING_FEATURES acts as the controlled feature
    interface between Snowflake and the ML process.
***************************************************************************************************/

USE ROLE MERC_DE;

ALTER SESSION SET QUERY_TAG =
'{"project":"mercedes","task":"manufacturing_features","day":"5"}';

USE WAREHOUSE TRANSFORM_WH;
USE DATABASE MERCEDES_DEV;
USE SCHEMA GOLD;


-- 1. CREATE ML FEATURE TABLE

CREATE OR REPLACE TABLE GOLD.MANUFACTURING_FEATURES 
AS
SELECT *
FROM MERCEDES_DEV.SILVER.MANUFACTURING_CLEAN
WHERE 'y' IS NOT NULL;