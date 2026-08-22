/***************************************************************************************************
Project : Mercedes-Benz Vehicle Analytics
Task    : DEV Deployment Test
Day     : 2

Purpose :
    Demonstrate automated deployment from GitHub Actions into Snowflake DEV.
****************************************************************************************************/

USE DATABASE MERCEDES_DEV;
USE SCHEMA AUDIT;

CREATE TABLE IF NOT EXISTS CI_CD_DEPLOYMENT_LOG (
    DEPLOYMENT_ID INTEGER AUTOINCREMENT,
    DEPLOYMENT_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DEPLOYED_BY VARCHAR,
    DEPLOYMENT_SOURCE VARCHAR,
    DEPLOYMENT_STATUS VARCHAR
);

INSERT INTO CI_CD_DEPLOYMENT_LOG (
    DEPLOYED_BY,
    DEPLOYMENT_SOURCE,
    DEPLOYMENT_STATUS
)
SELECT
    CURRENT_USER(),
    'GitHub Actions',
    'SUCCESS';