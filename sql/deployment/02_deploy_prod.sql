/***************************************************************************************************
Project  : Mercedes-Benz Vehicle Analytics
Task     : Production Deployment
Day      : 6

Purpose  : Establish the production Snowflake environment and create the
          objects required for CI/CD deployment tracking.

Important:
    This script deploys DATABASE OBJECT DEFINITIONS.

    It does NOT copy the DEV data into PROD.

    Production data should be loaded through the production
    ingestion pipeline.
***************************************************************************************************/

USE ROLE MERC_CI_CD;

ALTER SESSION SET QUERY_TAG = '{"project":"mercedes","task":"prod_deployment","day":"6"}';

USE DATABASE MERCEDES_PROD;


-- 1. AUDIT TABLE
-- Records every production deployment executed by CI/CD

USE SCHEMA AUDIT;

CREATE TABLE IF NOT EXISTS CI_CD_DEPLOYMENT_LOG (
    DEPLOYMENT_ID           INTEGER AUTOINCREMENT,
    DEPLOYMENT_TIMESTAMP    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DEPLOYED_BY             VARCHAR,
    DEPLOYMENT_SOURCE       VARCHAR,
    DEPLOYMENT_STATUS       VARCHAR
);


-- 2. RECORD SUCCESSFUL DEPLOYMENT

INSERT INTO CI_CD_DEPLOYMENT_LOG (
    DEPLOYED_BY,
    DEPLOYMENT_SOURCE,
    DEPLOYMENT_STATUS
)
SELECT 
    CURRENT_USER(),
    'GitHub Actions',
    'SUCCESS';


-- 3. DEPLOYMENT VALIDATION

SELECT 
    CURRENT_DATABASE()  AS DATABASE_NAME,
    CURRENT_ROLE()      AS DEPLOYMENT_ROLE,
    CURRENT_USER()      AS DEPLOYED_BY;


SELECT
    COUNT(*)    AS DEPLOYMENT_COUNT
FROM MERCEDES_PROD.AUDIT.CI_CD_DEPLOYMENT_LOG;

